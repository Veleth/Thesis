"""
Calculator module

Unified standard for calculator modules:
Input: values (Hex string array) and maxium number (Int)
Output: result (Int) and trace (String)
"""

def method1(values, maxNum):
    """
    This method uses standard Python RNG with the input as a seed.
    Result distribution is uniform.
    Input: array of input values, max number
    Output: calculation result, trace
    """
    import random

    s = ''.join(values)
    random.seed(s)
    result = random.randint(1, maxNum)
    trace = f'The joined array of values is\n{s}\nIt was used as a seed for random.randint(1, {maxNum}) call, which yielded {result}'
    
    return result, trace
    
def method2(values, maxNum):
    """
    This is an example method to show that methods can be easily swapped. This particular method uses mod operation on the sum of 
    the hex number array.
    Input: array of input values, max number
    Output: calculation result, trace
    """
    s = sum([int(v, 16) for v in values])
    result = s%maxNum or maxNum #if 0 then maxNum
    if result == maxNum:
        trace = f'The values: {values}\n, the sum: {s}, mod {maxNum} equals 0 (illegal) so it was changed to {result} (max, normally unachievable by mod {maxNum})'
    else:
        trace = f'The values: {values}\n, the sum: {s}, mod {maxNum} equals {result}'
    return result, trace