import timeit

from PrintTree import PrettyPrintTree
from colorama import Back


class Graph:
    def __init__(self, value):
        self.val = value
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        return neighbor


class Tree:
    def __init__(self, value, label=None):
        self.val = value
        self.children = []
        self.label = label

    def add_child(self, child):
        self.children.append(child)
        return child


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"""Person {{ 
    age: {self.age}, 
    name: {self.name} 
}}"""


print()
pt = PrettyPrintTree(lambda x: x.children, lambda x: x.val, max_depth=2)

tree = Tree("parent")
child0 = tree.add_child(Tree("1"))
child1 = tree.add_child(Tree("2"))
c1_1 = child0.add_child(Tree("33333\n333333"))
c1_2 = child0.add_child(Tree("44444444444"))
c1_1.add_child(Tree("5"))
c1_1.add_child(Tree("66666"))
c1_1.add_child(Tree("777"))
c1_2.add_child(Tree("88"))
c1_2.add_child(Tree("9"))
pt(tree)

print()
print()
# some_json = [
# {'foo': {'a': 1, 'b': 2}, 'bar': (['a', 'a2'], 'b'), 'qux': {'foo': 1, 'bar': [{'a': 1, 'b': 2}, 'b']}}, 1
# ]
some_json = {'foo': 1, 'bar': ('a', 'b'), 'qux': {'foo': 1, 'bar': ['a', 'b']}}

pt = PrettyPrintTree()
pt(some_json)

# print(timeit.timeit(stmt="PrettyPrintTree(lambda x: x.children, lambda x: x.val, return_instead_of_print=True)(tree)",
#                     globals=globals(), number=10000))