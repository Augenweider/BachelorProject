import re


class SyntaxTree(object):
    pass


class Operator(SyntaxTree):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
        self.parent = None
        if not isinstance(left, str):
            self.left.parent = self
        if not isinstance(right, str):
            if self.right is not None:
                self.right.parent = self
        self.operator = None

    def getParent(self):
        return self.parent

    def getSide(self, node):
        if node == self.left:
            return "left"
        elif node == self.right:
            return "right"
        else:
            return "Not my child"

    def conversion(self):
        pass

    def preorder(self):
        if self.operator is not None:
            self.conversion()
            if not isinstance(self.left, str):
                self.left.preorder()
            if not isinstance(self.right, str) and self.right is not None:
                self.right.preorder()

    def isCNF(self):
        cnf = True
        if self.operator != "Or" and self.operator != "And" and self.operator != "Not":
            return False
        if self.operator == "Or":
            if not isinstance(self.left, str) and self.left.operator == "And":
                return False
            if not isinstance(self.right, str) and self.right.operator == "And":
                return False
        if self.operator == "Not":
            if not isinstance(self.left, str) or self.right is not None:
                return False
        if not isinstance(self.left, str):
            if not self.left.isCNF():
                return False
        if not isinstance(self.right, str) and self.right is not None:
            if not self.right.isCNF():
                return False
        return cnf

    def __repr__(self):
        if self.left is None and self.right is None:
            return "%s" % self.operator
        if self.left is not None and self.right is None:
            return "%s(%s)" % (self.operator, str(self.left))
        if self.left is not None and self.right is not None:
            return "%s(%s, %s)" % (self.operator, str(self.left), str(self.right))


class And(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "And"


class Or(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "Or"

    def conversion(self):
        side = self.parent.getSide(self)
        if not isinstance(self.left, str) and self.left.operator == "And":
            exec("self.parent.%s = And(Or(self.left.left, self.right), Or(self.left.right, self.right))" % side)
        if not isinstance(self.right, str) and self.right.operator == "And":
            exec("self.parent.%s = And(Or(self.left, self.right.left), Or(self.left, self.right.right))" % side)


class Impl(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "Impl"

    def conversion(self):
        side = self.parent.getSide(self)
        if side == "left":
            self.parent.left = Or(Not(self.left), self.right)
            self.parent.left.parent = self.parent
        if side == "right":
            self.parent.right = Or(Not(self.left), self.right)
            self.parent.right.parent = self.parent


class BiImpl(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "BiImpl"

    def conversion(self):
        side = self.parent.getSide(self)
        exec("self.parent.%s = And(Impl(self.left, self.right), Impl(self.right, self.left))" % side)


class Not(Operator):
    def __init__(self, left):
        super().__init__(left)
        self.operator = "Not"

    def conversion(self):
        side = self.parent.getSide(self)
        if not isinstance(self.left, str):
            if self.left.operator == "Or":
                exec("self.parent.%s = And(Not(self.left.left), Not(self.left.right))" % side)
                exec("self.parent.%s.parent = self.parent" % side)
            if self.left.operator == "And":
                exec("self.parent.%s = Or(Not(self.left.left), Not(self.left.right))" % side)
                exec("self.parent.%s.parent = self.parent" % side)
            if self.left.operator == "Not":
                exec("self.parent.%s = self.left.left" % side)
                if not isinstance(self.left.left, str):
                    exec("self.parent.%s.parent = self.parent" % side)


class Var(SyntaxTree):
    def __init__(self):
        self.variable = {}

    def addVariable(self, v):
        self.variable[v] = len(self.variable) + 1


def parser(text):
    words = re.findall('\w+', text)
    v = Var()
    for word in words:
        if word not in v.variable and len(word) == 1:
            exec("%s = \"%s\"" % (word, word))
            v.addVariable(word)
    tree = eval(text)
    # Transfer the tree to CNF
    while not tree.isCNF():
        tree.preorder()
    # Transfer CNF to DIMACS-Format
    clauses = dimacs_generator(tree, v).split("\n")
    for i, clause in enumerate(clauses):
        if clause[-1] != '0':
            clauses[i] += '0'
    dimacs = "c cnf %d %d\n" % (len(v.variable), len(clauses))
    for clause in clauses:
        dimacs += (clause + "\n")
    print(dimacs)


def dimacs_generator(tree, v):
    text = ""
    if not isinstance(tree, str):
        if tree.operator == "And":
            if isinstance(tree.left, str):
                text += "\n%s 0" % v.variable[tree.left]
            if isinstance(tree.right, str):
                text += "\n%s 0" % v.variable[tree.right]
            if not isinstance(tree.left, str):
                if tree.left.operator == "And" or tree.left.operator == "Or":
                    text += dimacs_generator(tree.left, v)
                if tree.left.operator == "Not":
                    text += "\n-%s 0" % v.variable[tree.left.left]
            if not isinstance(tree.right, str):
                if tree.right.operator == "Or" or tree.right.operator == "And":
                    text += dimacs_generator(tree.right, v)
                if tree.right.operator == "Not":
                    text += "\n-%s 0" % v.variable[tree.right.left]
        if tree.operator == "Or":
            if isinstance(tree.left, str):
                text += "%s " % v.variable[tree.left]
            if isinstance(tree.right, str):
                text += "%s " % v.variable[tree.right]
            if not isinstance(tree.left, str):
                if tree.left.operator == "Or":
                    text += dimacs_generator(tree.left, v)
                if tree.left.operator == "Not":
                    text += "-%s " % v.variable[tree.left.left]
            if not isinstance(tree.right, str):
                if tree.right.operator == "Or":
                    text += dimacs_generator(tree.right, v)
                if tree.right.operator == "Not":
                    text += "-%s " % v.variable[tree.right.left]
    return text


if __name__ == '__main__':
    parser("And(Impl(And(Not(a), b), c), And(Not(b), Not(a)))")
    parser("And(Or(Not(a), b), And(Not(b), Not(a)))")
    parser("And(Or(Or(Not(a), c), b), And(And(Not(b), c), Not(a)))")
