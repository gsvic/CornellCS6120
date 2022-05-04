from synthesis import parser, synthesize, pretty, model_values


def intersect():
    tree1 = parser.parse("{2, 5}")
    tree2 = parser.parse("{2, h5, 6} intersect {h1, h2, h}")

    model = synthesize(tree1, tree2)
    print(model)
    print(pretty(tree1))
    print(pretty(tree2, model_values(model)))


def union():
    tree1 = parser.parse("{2, 5}")
    tree2 = parser.parse("{h1, h2} union {h3, h4}")

    model = synthesize(tree1, tree2)
    print(model)
    print(pretty(tree1))
    print(pretty(tree2, model_values(model)))


def diff():
    tree1 = parser.parse("{2, 5, 100}")
    tree2 = parser.parse("{h1, h2, h3, h4} diff {h6, h7, h8}")

    model = synthesize(tree1, tree2)
    print(pretty(tree1))
    print(pretty(tree2, model_values(model)))


if __name__ == "__main__":
    intersect()
    print()
    union()
    print()
    diff()