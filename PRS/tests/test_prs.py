import pytest
from prs import PRS, PriorityRowStack, PriorityError

def test_push_pop_basic():
    prs = PriorityRowStack(k=3, n=3)
    prs.push('a', 2)
    prs.push('b', 1)
    prs.push('c', 3)
    prs.push('d', 2)
    assert prs.peek() == 'd'
    assert prs.pop() == 'd'
    assert prs.pop() == 'b'
    assert prs.pop() == 'a'
    assert prs.pop() == 'c'
    assert prs.is_empty()

def test_lifo_within_priority():
    prs = PriorityRowStack(k=5, n=2)
    prs.push('x1', 1)
    prs.push('x2', 1)
    prs.push('x3', 1)
    assert prs.pop() == 'x3'
    assert prs.pop() == 'x2'
    assert prs.pop() == 'x1'

def test_invalid_priority():
    prs = PriorityRowStack(k=2, n=2)
    with pytest.raises(PriorityError):
        prs.push('bad', 0)
    with pytest.raises(PriorityError):
        prs.push('bad', 3)

def test_row_capacity_and_m_limit():
    prs = PriorityRowStack(k=1, n=1, m=2)
    prs.push('r1', 1)
    prs.push('r2', 1)
    with pytest.raises(Exception):
        prs.push('r3', 1)

def test_tolist_order():
    prs = PriorityRowStack(k=3, n=3)
    prs.push('a', 2)
    prs.push('b', 1)
    prs.push('c', 3)
    prs.push('d', 1)
    assert prs.tolist() == ['d', 'b', 'a', 'c']