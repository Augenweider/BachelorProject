import re

class SyntaxTree(object):
    pass

"""
class Node(SyntaxTree):
    def __init__(self, left=None, operator, right=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.parent = None
    
    def setParent(self):
        self.left.parent = self
        self.right.parent = self
    
    def getParent(self):
        return self.parent
    
    def conversion(self):
        if self.operator == "BiImpl":
            self.operator = "And"
            self.left = Node(self.left, "Impl", self.right)
            self.right = Node(self.right, "Impl", self.left)
        if self.operator == "Impl":
            self.operator = "Or"
            self.left = Node(self.left, "Not")
            self.right = self.right
        if self.operator == "Or":
            if self.left is Node and self.right is Var and self.left.operator == "And":
                self.operator = "And"
                self.left = Node(self.left.left, "Or", self.right)
                self.right = Node(self.left.right, "Or", self.right)
            if self.left is Var and self.right is Node and self.right.operator == "And":
                self.operator = "And"
                self.left = Node(self.left, "Or", self.right.left)
                self.right = Node(self.left, "Or", self.right.right)
        self.setParent()

    def __repr__(self):
        if self.left is not None and self.right is not None:
            print("%s(%s, %s)" % self.operator, self.left.__repr__, self.right.__repr__)
        elif self.left is not None and self.right is None:
            print("Not(%s)" % self.left)
        else:
            print("%s" % self.operator)
"""
class Operator(SyntaxTree):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
        self.parent = None
        self.left.parent = self
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

    def __repr__(self):
        if self.left == None and self.right == None:
            return ("%s" % self.operator)
        if self.left != None and self.right == None:
            return ("%s(%s)" % (self.operator, str(self.left)))
        if self.left != None and self.right != None:
            return ("%s(%s, %s)" % (self.operator, str(self.left), str(self.right)))
        

class And(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "And"

class Or(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "Or"

    def conversion(self):
        side = self.parent.getSide
        if self.left.operator == "And":
            eval("self.parent.%s = And(Or(self.left.left, self.right), Or(self.left.right, self.right))" % side)
        if self.right.operator == "Or":
            eval("self.parent.%s = And(Or(self.left, self.right.left), Or(self.left, self.right.right))" % side)


class Impl(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "Impl"

    def conversion(self):
        side = self.parent.getSide
        if side == "left":
            self.parent.left = Or(Not(self.left), self.right)
        if side == "right":
            self.parent.right = Or(Not(self.left), self.right)

class BiImpl(Operator):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = "BiImpl"

    def conversion(self):
        side = self.parent.getSide
        eval("self.parent.%s = And(Impl(self.left, self.right), Impl(self.right, self.left))" % side)

class Not(Operator):
    def __init__(self, left):
        super().__init__(left)
        self.operator = "Not"
    def conversion(self):
        side = self.parent.getSide
        if self.left.operator == "Or":
            eval("self.parent.%s = And(Not(self.left.left), Not(self.left.right))" % side)
        if self.left.operator == "And":
            eval("self.parent.%s = Or(Not(self.left.left), Not(self.left.right))" % side)
        if self.left.operator == "Not":
            eval("self.parent.%s = self.left.left" % side)


class Var(SyntaxTree):
    def __init__(self):
        self.variable = {}

    def addVariable(self, v):
        self.variable[v] = len(self.variable) + 1


def parser(text):
    words = re.findall('\w+', text)
    tree = None
    v = Var()
    for word in words:
        if words not in v and len(word) == 1:
            eval("%s = \"%s\"" % (word, word))
            v.addVariable(word)
    eval("tree = %s" % text)
    
    










