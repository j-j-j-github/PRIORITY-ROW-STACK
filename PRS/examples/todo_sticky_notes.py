import random
from prs import PRS, PriorityError

def main():
    # cap=4 tasks per row, 3 priorities, up to 3 rows
    stack = PRS(k=4, n=3, m=3)
    categories = {1: "Critical", 2: "Normal", 3: "Optional"}

    tasks = [
        ("Finish project report", 1),
        ("Buy groceries", 2),
        ("Clean desk", 3),
        ("Pay bills", 1),
        ("Read a book", 3),
        ("Workout", 2),
        ("Call mom", 1),
        ("Water plants", 3),
    ]

    # Add tasks
    for task, prio in tasks:
        try:
            stack.push(task, prio)
            print(f"📝 Added: {task} ({categories[prio]})")
        except PriorityError as e:
            print(f"❌ Priority error for {task}: {e}")
        except Exception as e:
            print(f"❌ Couldn’t add {task}: {e}")

    print("\n=== Starting Day ===")
    while not stack.is_empty():
        if random.random() > 0.2:  # sometimes skip tasks
            task = stack.pop()
            print(f"✅ Completed: {task}")
        else:
            print("⏸ Skipped a cycle (procrastination)")

    print("\nAll tasks done. PRS empty?", stack.is_empty())


if __name__ == "__main__":
    main()