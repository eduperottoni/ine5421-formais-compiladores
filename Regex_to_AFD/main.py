from syntax_tree_builder import SyntaxTreeBuilder

regex = '(&|b)(ab)*(&|a)'
# regex = 'aa*(bb*aa*b)*'
# regex = 'a(a|b)*a'
# regex = 'a(a*(bb*a)*)*|b(b*(aa*b)*)*'

tree = SyntaxTreeBuilder.build_tree(regex)
tree.pretty_print()
