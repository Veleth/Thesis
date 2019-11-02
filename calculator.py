
"""
Unified standard for calculator modules:
Input: values (Hex array) and maximal number (Int)
Output: result (Int) and trace (String)
"""

def method1(values, maxNum):
    import random

    s = ''.join(values)
    random.seed(s)
    result = random.randint(1, maxNum)
    trace = f'The joined array of values is\n{s}\nIt was used as a seed for random.randint(1, {maxNum}) call, which yielded {result}'
    
    return result, trace
    
def method2(values, maxNum):
    s = sum([int(v, 16) for v in values])
    result = s%maxNum or maxNum #if 0 then maxNum
    if result == maxNum:
        trace = f'The values: {values}\n, the sum: {s}, mod {maxNum} equals 0 (illegal) so it was changed to {result} (max, normally unachievable by mod {maxNum})'
    else:
        trace = f'The values: {values}\n, the sum: {s}, mod {maxNum} equals {result}'
    return result, trace