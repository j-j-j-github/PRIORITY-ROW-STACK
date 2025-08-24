# Priority-Row-Stack
A novel data structure combining stack semantics with intra-row priority levels.
# Priority Row Stack (PRS)

A **novel data structure** that combines the *row-based grouping* of elements with *intra-row priority levels*.  
The **Priority Row Stack (PRS)** is designed to support situations where data must be stored in batches (rows),  
but elements within each row may have different priorities that affect retrieval order.  

---

## 📖 Motivation

The idea for PRS was inspired by a real-life scenario: organizing a personal to-do list on a wall using sticky notes.  
- Each **day** represented a "row".  
- Within each day, tasks had **different priority levels** (urgent, normal, optional).  
- I noticed that existing structures like stacks or queues couldn’t fully capture this two-dimensional organization:  
  - A stack gives order but no priority.  
  - A priority queue gives priority but no row/batch grouping.  

This led to the creation of the **Priority Row Stack (PRS)**:  
A structure that combines **row-based grouping** (like days) with **intra-row priority** (like sticky note importance).

---

## 🏗️ Structure

- The PRS is parameterized as `PRS(m, k, n)`, where:
  - `m`: maximum number of rows (optional, can be dynamic).
  - `k`: maximum elements per row.
  - `n`: number of priority levels (1 = highest priority, n = lowest).

- Each **row**:
  - Can hold up to `k` elements.
  - Each element has an associated **priority level**.
  - Elements are retrieved based on priority, then insertion order.

- The **rows**:
  - Are stacked on top of each other (like a stack).
  - New rows are created when the top row is full.
  - Elements are popped starting from the **top row**.

---

## ⚙️ Operations

### `push(element, priority)`
- Inserts an element with given priority into the **top row**.
- If the top row is full, a new row is created on top.
- Complexity: **O(1)** (amortized).

### `pop()`
- Removes and returns the highest-priority element from the **top row**.
- If multiple elements share the same highest priority:
  - Follows LIFO order (last inserted, first out).
- If the top row becomes empty after popping, it is discarded.
- Complexity: **O(k)** (must check priorities in the row).

### `peek()`
- Returns (but does not remove) the next element to be popped.
- Complexity: **O(k)**.

### `isEmpty()`
- Returns true if there are no rows or all rows are empty.
- Complexity: **O(1)**.

---

## 📊 Comparison with Classical Structures

| Structure        | Organization Rule              | Priority Support | Batch/Row Grouping | Use Cases |
|------------------|--------------------------------|-----------------|---------------------|-----------|
| Stack            | LIFO                           | ❌              | ❌                  | Function calls, undo |
| Queue            | FIFO                           | ❌              | ❌                  | Scheduling, buffering |
| Priority Queue   | Global priority ordering       | ✅              | ❌                  | Scheduling, pathfinding |
| **PRS (this)**   | Row-based (stack of rows) + intra-row priority | ✅ (per row) | ✅                  | Batch scheduling, grouped undo, resource allocation |

---

## 🔥 Example Usage

```python
from prs import PriorityRowStack

# Create PRS with 3 elements per row, 3 priority levels
prs = PriorityRowStack(k=3, n=3)

prs.push("task1", priority=2)
prs.push("task2", priority=1)   # higher priority
prs.push("task3", priority=3)

prs.push("task4", priority=2)   # goes into new row since row 1 is full

print(prs.pop())  # -> "task2" (highest priority in top row)
print(prs.pop())  # -> "task1"
```

---

## 🎮 Real-World Applications

- **Game Engines**:  
  Store game events in frames (rows), but execute them based on urgency (priority).  

- **Batch Task Scheduling**:  
  In OS or distributed systems, tasks are grouped in batches but within each batch some are more urgent.  

- **Undo/Redo Systems**:  
  Group actions in rows (like editing sessions), but allow undo of higher-priority changes first.  

- **Networking**:  
  Data packets grouped by time window (row), prioritized by type (control > data > logs).  

---

## ⏱️ Complexity Summary

| Operation | Worst-case Complexity |
|-----------|------------------------|
| `push`    | O(1)                   |
| `pop`     | O(k)                   |
| `peek`    | O(k)                   |
| `isEmpty` | O(1)                   |

*(Future work may explore faster priority lookups using auxiliary heaps or balanced trees per row.)*

---

## 🛠️ Roadmap

- [ ] Formalize definition in academic-style paper.  
- [ ] Implement reference version in **Python**.  
- [ ] Add optimized versions in **C++** and **Rust**.  
- [ ] Benchmark against stack, queue, priority queue.  
- [ ] Write blog post explaining PRS with diagrams.  
- [ ] Submit preprint to **arXiv**.  
- [ ] Create Wikipedia page after peer-reviewed mentions.  

---

## 📚 References

- Classic structures: Stack, Queue, Priority Queue.  
- [Introduction to Algorithms (CLRS)](https://en.wikipedia.org/wiki/Introduction_to_Algorithms)  

---

## 👨‍💻 Author

**Jeeval Jolly Jacob**  
Inventor of the **Priority Row Stack (PRS)**, a new data structure idea in 2025.  

Contributions welcome! Feel free to fork and open issues.
