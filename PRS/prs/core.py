"""core.py
Professional implementation of Priority Row Stack (PRS).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar
import threading

T = TypeVar("T")


# ----------------------------
# Exceptions
# ----------------------------
class PRSError(Exception):
    pass


class PriorityError(PRSError):
    pass


class EmptyError(PRSError):
    pass


class RowFullError(PRSError):
    pass


# ----------------------------
# Internal Row implementation
# ----------------------------
@dataclass
class PRSRow(Generic[T]):
    k: int
    n: int
    buckets: List[List[T]] = field(default_factory=list)
    count: int = 0
    top_priority_idx: Optional[int] = None

    def __post_init__(self) -> None:
        if self.k <= 0:
            raise ValueError("k must be > 0")
        if self.n <= 0:
            raise ValueError("n must be > 0")
        if not self.buckets:
            self.buckets = [[] for _ in range(self.n)]
        self._recompute_top_priority()

    def is_full(self) -> bool:
        return self.count >= self.k

    def is_empty(self) -> bool:
        return self.count == 0

    def _recompute_top_priority(self) -> None:
        self.top_priority_idx = None
        for idx in range(self.n):
            if self.buckets[idx]:
                self.top_priority_idx = idx
                return

    def push(self, item: T, priority: int) -> None:
        if not (1 <= priority <= self.n):
            raise PriorityError(f"priority must be between 1 and {self.n}, got {priority}")
        if self.is_full():
            raise RowFullError("row is full")
        idx = priority - 1
        self.buckets[idx].append(item)
        self.count += 1
        if self.top_priority_idx is None or idx < self.top_priority_idx:
            self.top_priority_idx = idx

    def peek(self) -> T:
        if self.is_empty():
            raise EmptyError("peek from empty row")
        if self.top_priority_idx is None:
            self._recompute_top_priority()
        assert self.top_priority_idx is not None
        bucket = self.buckets[self.top_priority_idx]
        return bucket[-1]

    def pop(self) -> T:
        if self.is_empty():
            raise EmptyError("pop from empty row")
        if self.top_priority_idx is None:
            self._recompute_top_priority()
        assert self.top_priority_idx is not None
        bucket = self.buckets[self.top_priority_idx]
        item = bucket.pop()
        self.count -= 1
        if not bucket:
            self._recompute_top_priority()
        return item

    def tolist(self) -> List[T]:
        out: List[T] = []
        for idx in range(self.n):
            out.extend(reversed(self.buckets[idx]))
        return out

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        parts = []
        for i, b in enumerate(self.buckets, start=1):
            if b:
                parts.append(f"P{i}={len(b)}")
        return f"<Row count={self.count} {' '.join(parts)}>"


# ----------------------------
# Public Priority Row Stack
# ----------------------------
class PriorityRowStack(Generic[T]):
    def __init__(self, k: int, n: int, m: Optional[int] = None, thread_safe: bool = False) -> None:
        if k <= 0 or n <= 0:
            raise ValueError("k and n must be > 0")
        if m is not None and m <= 0:
            raise ValueError("m must be None or > 0")
        self.k = k
        self.n = n
        self.m = m
        self._rows: List[PRSRow[T]] = []
        self._size = 0
        self._lock = threading.RLock() if thread_safe else None

    def _lock_acquire(self):
        if self._lock:
            self._lock.acquire()

    def _lock_release(self):
        if self._lock:
            self._lock.release()

    def _ensure_top_row(self) -> None:
        if not self._rows or self._rows[-1].is_full():
            if self.m is not None and len(self._rows) >= self.m and (not self._rows or self._rows[-1].is_full()):
                raise PRSError("maximum number of rows reached (m)")
            self._rows.append(PRSRow(self.k, self.n))

    def push(self, item: T, priority: int) -> None:
        self._lock_acquire()
        try:
            self._ensure_top_row()
            self._rows[-1].push(item, priority)
            self._size += 1
        finally:
            self._lock_release()

    def peek(self) -> T:
        self._lock_acquire()
        try:
            if self._size == 0:
                raise EmptyError("peek from empty PRS")
            while self._rows and self._rows[-1].is_empty():
                self._rows.pop()
            if not self._rows:
                raise EmptyError("peek from empty PRS")
            return self._rows[-1].peek()
        finally:
            self._lock_release()

    def pop(self) -> T:
        self._lock_acquire()
        try:
            if self._size == 0:
                raise EmptyError("pop from empty PRS")
            while self._rows and self._rows[-1].is_empty():
                self._rows.pop()
            if not self._rows:
                raise EmptyError("pop from empty PRS")
            item = self._rows[-1].pop()
            self._size -= 1
            if self._rows and self._rows[-1].is_empty():
                self._rows.pop()
            return item
        finally:
            self._lock_release()

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def rows_count(self) -> int:
        return len(self._rows)

    def tolist(self) -> List[T]:
        self._lock_acquire()
        try:
            out: List[T] = []
            for row in reversed(self._rows):
                out.extend(row.tolist())
            return out
        finally:
            self._lock_release()

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        top = self._rows[-1] if self._rows else None
        return f"<PRS rows={len(self._rows)} size={self._size} top={top}>"


# ----------------------------
# Public API
# ----------------------------
__all__ = ["PriorityRowStack", "PRSError", "PriorityError", "EmptyError", "RowFullError"]