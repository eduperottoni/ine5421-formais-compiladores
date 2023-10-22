from syntax_tree import SyntaxTree

class SyntaxTreeBuilder():
    """
    Syntax Tree builder
    """

    operators = {
        'concat': '.',
        'or': '|',
        'star': '*',
        'open_par': '(',
        'close_par': ')'
    }

    @classmethod
    def build_tree(cls, regex: str) -> SyntaxTree:
        return SyntaxTree(regex, cls.operators)
