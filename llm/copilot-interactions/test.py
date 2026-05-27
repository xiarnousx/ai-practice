def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


def calculate_median(numbers):
    if not numbers:
        return 0
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    else:
        return sorted_numbers[mid]

# A function that returns the mode of a list of numbers
def calculate_mode(numbers):
    if not numbers:
        return None
    frequency = {}
    for number in numbers:
        frequency[number] = frequency.get(number, 0) + 1
    max_count = max(frequency.values())
    modes = [key for key, count in frequency.items() if count == max_count]
    return modes

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result