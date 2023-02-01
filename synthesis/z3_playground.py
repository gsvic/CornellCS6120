from z3 import *

def solve(phi):
    s = z3.Solver()
    s.add(phi)
    s.check()
    return s.model()

# Find a x such as x / 7 == 23
formula = z3.Int('x') / 7 == 23

# Find y such as y << 3
bit_vec_formula = z3.BitVec('y', 5) << 3 == 40

z = z3.Int('x')
n = z3.Int('n')
mul_formula = z3.ForAll([z], z * n == z)

x = z3.BitVec('x', 5)
slow = x * 8
fast = x << z3.BitVec('y', 5)

obj = z3.ForAll([x], slow == fast)

z3.Set

S1 = EmptySet(IntSort())
S1 = SetAdd(S1, 2)
S1 = SetAdd(S1, 5)
S1 = SetAdd(S1, 6)
S1 = SetAdd(S1, 8)

S2 = EmptySet(IntSort())
S2 = SetAdd(S2, 2)
S2 = SetAdd(S2, 5)

N = EmptySet(IntSort())
N = SetAdd(N, n)
N = SetAdd(N, z)

goal = SetUnion(S2, N) == S1

print(solve(goal))

