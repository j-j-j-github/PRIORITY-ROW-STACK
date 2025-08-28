import random
from prs import PRS

def main():
    # Each batch row can hold up to 5 tasks, 3 priority levels, max 4 rows
    stack = PRS(k=5, n=3, m=4)

    # Generate tasks (batch jobs)
    jobs = [f"Job-{i}" for i in range(1, 13)]
    for job in jobs:
        prio = random.randint(1, 3)
        stack.push(job, prio)
        print(f"📥 Scheduled {job} (priority {prio})")

    print("\n=== Processing jobs ===")
    while not stack.is_empty():
        job = stack.pop()
        print(f"⚡ Running {job}")

    print("\n✅ All jobs processed.")


if __name__ == "__main__":
    main()