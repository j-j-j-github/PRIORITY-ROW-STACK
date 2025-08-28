# examples/large_interactive.py
"""
Large-scale interactive PRS stress test and baseline comparison.

Features:
- Generate a large synthetic workload (>1000 jobs by default).
- Optionally let the user add custom jobs interactively before the run.
- Run three schedulers over the same final job list:
    * PRS (rows, your structure)
    * Global Priority Queue (heapq)
    * Plain Stack (LIFO)
- Compute metrics and print comparison results.

Usage (from repo root):
    python3 -m examples.large_interactive --num-jobs 1500 --row-capacity 8 --priority-levels 5

Interactive usage:
    python3 -m examples.large_interactive --interactive
    (then follow prompts to add custom jobs; press Enter on empty line to finish)
"""
from __future__ import annotations
import argparse
import random
import time
import heapq
import statistics
from typing import List, Dict, Tuple

# Import your PRS library; ensure you're running from repo root so `prs` package is importable.
from prs import PRS

# ----------------------------
# Job generation
# ----------------------------
def generate_jobs(num_jobs: int, priority_levels: int,
                  batch_min: int = 1, batch_max: int = 12, seed: int | None = None) -> List[Dict]:
    """
    Create a list of job dicts with fields: id, priority, arrival_idx.
    Jobs are generated in batches to create row-like grouping behavior.
    """
    if seed is not None:
        random.seed(seed)

    jobs: List[Dict] = []
    jid = 0
    while jid < num_jobs:
        batch_size = random.randint(batch_min, batch_max)
        batch_bias = random.random()
        for _ in range(batch_size):
            if jid >= num_jobs:
                break
            # create varied priority distributions using bias
            if batch_bias < 0.15:
                pr = random.choices(range(1, priority_levels+1), weights=[40,25,15,12,8][:priority_levels])[0]
            elif batch_bias < 0.5:
                pr = random.choices(range(1, priority_levels+1), weights=[10,25,30,20,15][:priority_levels])[0]
            else:
                pr = random.randint(1, priority_levels)
            jobs.append({"id": f"job-{jid+1}", "priority": pr, "arrival_idx": jid})
            jid += 1
    return jobs

# ----------------------------
# Scheduler implementations
# ----------------------------
def run_global_priority_queue(jobs: List[Dict]) -> Tuple[List[Dict], float]:
    start = time.perf_counter()
    heap: List[Tuple[int, int, Dict]] = []
    for job in jobs:
        heapq.heappush(heap, (job["priority"], job["arrival_idx"], job))
    out: List[Dict] = []
    while heap:
        _, _, j = heapq.heappop(heap)
        out.append(j)
    elapsed = time.perf_counter() - start
    return out, elapsed

def run_stack(jobs: List[Dict]) -> Tuple[List[Dict], float]:
    start = time.perf_counter()
    st = []
    for job in jobs:
        st.append(job)
    out = []
    while st:
        out.append(st.pop())
    elapsed = time.perf_counter() - start
    return out, elapsed

def run_prs(jobs: List[Dict], k: int, n: int, m: int | None = None) -> Tuple[List[Dict], float]:
    start = time.perf_counter()
    prs = PRS(k=k, n=n, m=m)
    for job in jobs:
        prs.push(job, job["priority"])
    out: List[Dict] = []
    while not prs.is_empty():
        out.append(prs.pop())
    elapsed = time.perf_counter() - start
    return out, elapsed

# ----------------------------
# Metrics
# ----------------------------
def compute_metrics(jobs: List[Dict], completion_order: List[Dict]) -> Dict:
    N = len(jobs)
    arrival_map = {job["id"]: job["arrival_idx"] for job in jobs}
    completion_pos = {job["id"]: idx for idx, job in enumerate(completion_order)}
    # positions in original arrival order
    positions = [completion_pos[j["id"]] for j in jobs]
    avg_pos = statistics.mean(positions)
    norm_avg = avg_pos / N
    # per-priority stats
    by_pr = {}
    for j in jobs:
        p = j["priority"]
        by_pr.setdefault(p, []).append(completion_pos[j["id"]])
    pr_stats = {p: {"count": len(lst), "mean_pos": statistics.mean(lst)} for p, lst in by_pr.items()}

    # inversions: count pairs (i before j) in completion where priority[i] > priority[j]
    # We'll use O(N^2) approach — acceptable for ~1500 jobs; reduce if you scale >20k.
    inversions = 0
    id_to_priority = {j["id"]: j["priority"] for j in jobs}
    N = len(completion_order)
    for i in range(N):
        pri_i = id_to_priority[completion_order[i]["id"]]
        for j in range(i+1, N):
            pri_j = id_to_priority[completion_order[j]["id"]]
            if pri_i > pri_j:  # lower priority finished earlier than higher priority => inversion
                inversions += 1

    return {
        "N": len(jobs),
        "avg_completion_pos": avg_pos,
        "normalized_avg_pos": norm_avg,
        "per_priority": pr_stats,
        "inversions": inversions
    }

def pretty_print_metrics(name: str, metrics: Dict, elapsed: float):
    print(f"\n--- {name} ---")
    print(f"Jobs processed: {metrics['N']}")
    print(f"Elapsed time: {elapsed:.6f} s")
    print(f"Average completion index: {metrics['avg_completion_pos']:.2f} "
          f"(normalized {metrics['normalized_avg_pos']:.4f})")
    print(f"Inversions (lower-priority before higher-priority): {metrics['inversions']}")
    print("Per-priority mean completion positions:")
    for p in sorted(metrics['per_priority']):
        s = metrics['per_priority'][p]
        print(f"  priority {p}: count={s['count']} mean_pos={s['mean_pos']:.2f}")

# ----------------------------
# Interactive pre-run (optional)
# ----------------------------
def prompt_user_jobs() -> List[Dict]:
    print("Enter custom jobs one per line in the format: <name> <priority>")
    print("Priority must be integer (1 = highest). Press Enter on an empty line to finish.")
    user_jobs = []
    idx = 0
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        parts = line.split()
        if len(parts) < 2:
            print("  invalid format — expected: name priority")
            continue
        name = " ".join(parts[:-1])
        try:
            pr = int(parts[-1])
        except ValueError:
            print("  priority must be integer")
            continue
        user_jobs.append({"id": f"user-{idx+1}-{name.replace(' ','_')}", "priority": pr, "arrival_idx": None})
        idx += 1
    return user_jobs

# ----------------------------
# Main driver with argparse
# ----------------------------
def main():
    parser = argparse.ArgumentParser(prog="large_interactive",
                                     description="Large PRS demo with interactive job input and baseline comparison.")
    parser.add_argument("--num-jobs", type=int, default=1500, help="Total auto-generated jobs (excluding user-added).")
    parser.add_argument("--priority-levels", type=int, default=5, help="Number of priority levels (1..n).")
    parser.add_argument("--row-capacity", type=int, default=8, help="k: items per PRS row.")
    parser.add_argument("--max-rows", type=int, default=0,
                        help="m: maximum rows for PRS (0 means unbounded).")
    parser.add_argument("--batch-min", type=int, default=1, help="min batch size for job generation.")
    parser.add_argument("--batch-max", type=int, default=12, help="max batch size for job generation.")
    parser.add_argument("--seed", type=int, default=42, help="random seed for reproducibility (0 for random).")
    parser.add_argument("--interactive", action="store_true", help="Allow adding custom jobs before run.")
    parser.add_argument("--sample", type=int, default=30, help="How many first-completions to print for comparison.")
    args = parser.parse_args()

    seed = None if args.seed == 0 else args.seed

    print("=== PRS Large Interactive Simulation ===")
    print(f"Generating {args.num_jobs} synthetic jobs (priority levels 1..{args.priority_levels})")
    user_jobs = []
    if args.interactive:
        print("\nYou chose interactive mode — add jobs now (optional).")
        user_jobs = prompt_user_jobs()
        print(f"You added {len(user_jobs)} custom jobs.\n")

    # Generate synthetic workload to reach total count (auto jobs only)
    jobs = generate_jobs(args.num_jobs, args.priority_levels, args.batch_min, args.batch_max, seed=seed)

    # Append user jobs at the end, assign arrival indices following auto-generated ones
    base_idx = len(jobs)
    for i, uj in enumerate(user_jobs):
        uj["arrival_idx"] = base_idx + i
        jobs.append(uj)

    total_jobs = len(jobs)
    print(f"Final job count (auto + user): {total_jobs}")

    # Run PRS
    max_rows = None if (args.max_rows == 0) else args.max_rows
    print("\nRunning PRS...")
    prs_order, prs_time = run_prs(jobs, k=args.row_capacity, n=args.priority_levels, m=max_rows)
    prs_metrics = compute_metrics(jobs, prs_order)
    pretty_print_metrics("PRS", prs_metrics, prs_time)

    # Run Global Priority Queue
    print("\nRunning Global Priority Queue (heapq)...")
    pq_order, pq_time = run_global_priority_queue(jobs)
    pq_metrics = compute_metrics(jobs, pq_order)
    pretty_print_metrics("Global Priority Queue", pq_metrics, pq_time)

    # Run Plain Stack
    print("\nRunning Plain Stack (LIFO)...")
    st_order, st_time = run_stack(jobs)
    st_metrics = compute_metrics(jobs, st_order)
    pretty_print_metrics("Plain Stack (LIFO)", st_metrics, st_time)

    # Print samples
    sample = min(args.sample, total_jobs)
    print(f"\nFirst {sample} completions (PRS):")
    print([j["id"] for j in prs_order[:sample]])
    print(f"\nFirst {sample} completions (PQ):")
    print([j["id"] for j in pq_order[:sample]])
    print(f"\nFirst {sample} completions (STACK):")
    print([j["id"] for j in st_order[:sample]])

    print("\nDone. Interpretation hints:")
    print(" - Lower avg_completion_pos means jobs finished earlier on average.")
    print(" - Fewer inversions means fewer cases where low-priority tasks finished before high-priority ones.")
    print(" - PRS will show mixed behavior: it preserves per-row locality while offering intra-row priority;")
    print("   PQ strictly enforces priority; stack ignores priority in favor of LIFO.")

if __name__ == "__main__":
    main()