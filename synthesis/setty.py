import lark
import z3

# A language based on a Lark example from:
# https://github.com/lark-parser/lark/wiki/Examples
GRAMMAR = """
?start: item
  | item "union"        item -> union
  | item "intersect"    item -> intersect
?item: set
?element: NUMBER        -> num
  | CNAME               -> var
    
set  : "{" [element ("," element)*] "}"

%import common.NUMBER
%import common.WS
%import common.CNAME
%ignore WS
""".strip()



def interp(tree, lookup):
    """Evaluate the arithmetic expression.
    Pass a tree as a Lark `Tree` object for the parsed expression. For
    `lookup`, provide a function for mapping variable names to values.
    """

    op = tree.data
    if op in ('union', 'intersect'):  # Binary operators.
        lhs = interp(tree.children[0], lookup)
        rhs = interp(tree.children[1], lookup)
        if op == 'union':
            return z3.SetUnion(lhs, rhs)
        elif op == 'intersect':
            return z3.SetIntersect(lhs, rhs)
    elif op == 'neg':  # Negation.
        sub = interp(tree.children[0], lookup)
        return -sub
    elif op == 'num':  # Literal number.
        return int(tree.children[0])
    elif op == 'var':  # Variable lookup.
        return lookup(tree.children[0])
    elif op == 'set':
        s = z3.EmptySet(z3.IntSort())
        for token in tree.children:
            val = interp(token, lookup)
            s = z3.SetAdd(s, val)
        return s


def pretty(tree, subst={}, paren=False):
    """Pretty-print a tree, with optional substitutions applied.
    If `paren` is true, then loose-binding expressions are
    parenthesized. We simplify boolean expressions "on the fly."
    """

    # Add parentheses?
    if paren:
        def par(s):
            return '({})'.format(s)
    else:
        def par(s):
            return s

    op = tree.data
    if op in ('intersect', 'union'):
        lhs = pretty(tree.children[0], subst, True)
        rhs = pretty(tree.children[1], subst, True)
        c = {
            'intersect': 'intersect',
            'union': 'union',
        }[op]
        return par('{} {} {}'.format(lhs, c, rhs))
    elif op == 'num':
        return tree.children[0]
    elif op == 'var':
        name = tree.children[0]
        return str(subst.get(name, name))
    elif op == 'set':
        r = set([pretty(t, subst) for t in tree.children])
        return r


def run(tree, env):
    """Ordinary expression evaluation.
    `env` is a mapping from variable names to values.
    """

    return interp(tree, lambda n: env[n])


def z3_expr(tree, vars=None):
    """Create a Z3 expression from a tree.
    Return the Z3 expression and a dict mapping variable names to all
    free variables occurring in the expression. All variables are
    represented as BitVecs of width 8. Optionally, `vars` can be an
    initial set of variables.
    """

    vars = dict(vars) if vars else {}

    # Lazily construct a mapping from names to variables.
    def get_var(name):
        if name in vars:
            return vars[name]
        else:
            v = z3.Int(name)
            vars[name] = v
            return v

    return interp(tree, get_var), vars


def solve(phi):
    """Solve a Z3 expression, returning the model.
    """

    s = z3.Solver()
    s.add(phi)
    s.check()
    return s.model()


def model_values(model):
    """Get the values out of a Z3 model.
    """
    return {
        d.name(): model[d]
        for d in model.decls()
    }


def synthesize(tree1, tree2):
    """Given two programs, synthesize the values for holes that make
    them equal.
    `tree1` has no holes. In `tree2`, every variable beginning with the
    letter "h" is considered a hole.
    """

    expr1, vars1 = z3_expr(tree1)
    expr2, vars2 = z3_expr(tree2, vars1)

    # Filter out the variables starting with "h" to get the non-hole
    # variables.
    plain_vars = {k: v for k, v in vars1.items()
                  if not k.startswith('h')}

    # Formulate the constraint for Z3.
    # goal = z3.ForAll(
    #     list(plain_vars.values()),  # For every valuation of variables...
    #     expr1 == expr2,  # ...the two expressions produce equal results.
    # )
    goal = expr1 == expr2

    # Solve the constraint.
    return solve(goal)


def ex2(source):
    src1, src2 = source.strip().split('\n')

    parser = lark.Lark(GRAMMAR)
    tree1 = parser.parse(src1)
    tree2 = parser.parse(src2)

    model = synthesize(tree1, tree2)
    print(pretty(tree1))
    print(pretty(tree2, model_values(model)))

parser = lark.Lark(GRAMMAR)


tree1 = parser.parse("{2, 5}")
tree2 = parser.parse("{2, h5, 6} intersect {h1, h2, h}")

# print(tree1)
# print(tree2)

model = synthesize(tree1, tree2)

print(model)

print(pretty(tree1))
print(pretty(tree2, model_values(model)))