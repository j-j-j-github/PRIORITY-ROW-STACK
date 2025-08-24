# priority-row-stack
A novel data structure combining stack semantics with intra-row priority levels.
# Priority Row Stack (PRS)

A **novel data structure** that combines the *row-based grouping* of elements with *intra-row priority levels*.  
The **Priority Row Stack (PRS)** is designed to support situations where data must be stored in batches (rows),  
but elements within each row may have different priorities that affect retrieval order.  

---

## 📖 Motivation

Traditional data structures like **stack**, **queue**, and **priority queue** solve many fundamental problems in computer science.  
However, in some real-world scenarios, we need:

- **Grouping of elements into rows or batches** (e.g., events in a frame, tasks in a batch).  
- **Priorities within each row**, not just across the entire structure.  
- **Row-level access** where some rows are considered "higher" than others (like stack ordering).  

The **Priority Row Stack (PRS)** addresses these gaps by combining stack-like row organization with intra-row priority-based access.

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
