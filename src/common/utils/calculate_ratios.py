from collections import defaultdict

def calculate_ratios(data):
    sums = defaultdict(int)
    ratios = defaultdict(dict)

    for key, value, amount in data:
        sums[key] += amount

    for key, value, amount in data:
        ratios[key][value] = amount / sums[key]

    return ratios
