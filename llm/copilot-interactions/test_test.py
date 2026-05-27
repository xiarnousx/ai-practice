from copilot-interactions.test import merge_sort

def test_merge_sort_empty():
    assert merge_sort([]) == []

def test_merge_sort_single_element():
    assert merge_sort([42]) == [42]

def test_merge_sort_sorted():
    assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_merge_sort_reverse():
    assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_merge_sort_duplicates():
    assert merge_sort([3, 1, 2, 3, 1]) == [1, 1, 2, 3, 3]

def test_merge_sort_negative_numbers():
    assert merge_sort([-2, -5, 0, 3, 1]) == [-5, -2, 0, 1, 3]

def test_merge_sort_mixed_types():
    arr = [0, -1, 5, 3, -10, 2]
    assert merge_sort(arr) == sorted(arr)