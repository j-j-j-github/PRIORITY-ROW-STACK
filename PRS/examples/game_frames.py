import random
from prs import PRS

def main():
    # Frames: each row = 6 frames, 3 priority levels, 5 rows max
    stack = PRS(k=6, n=3, m=5)

    # Simulate frame updates with priorities
    frames = [f"Frame-{i}" for i in range(1, 16)]
    for frame in frames:
        prio = random.choice([1, 2, 3])
        stack.push(frame, prio)
        print(f"🎮 Queued {frame} (priority {prio})")

    print("\n=== Rendering Frames ===")
    while not stack.is_empty():
        frame = stack.pop()
        print(f"🖼️ Rendered {frame}")

    print("\n✅ All frames rendered.")


if __name__ == "__main__":
    main()