class SyntaxTree():
    def __init__(self, regex: str, operators: tuple[str]):
        self.__define_alphabet(regex, operators)
        self.__mask_regex(regex, operators)
        # self.__parse_regex(regex)


    def __mask_regex(self, regex: str, operators: dict) -> None:
        """
        Adiciona # ao final da palavra
        Adiciona . nos lugares que estão faltando
        """
        masked_regex = f'({regex})#'
        # print(f'SELF_MASKED_REGEX: {self.masked_regex}')
        new_regex = ''
        
        for index, item in enumerate(masked_regex[:-1]):
            # print(f'CURR_ELEMENT: {item}')
            next_item = masked_regex[index + 1]
            # print(f'NEXT_ELEMENT: {next_item}')
            if item in self.alphabet:
                # Case 'ab', 'a('
                new_regex += item if next_item in operators.values() and next_item != operators['par_initial'] else f'{item}.'
            elif item == operators['par_final']:
                #Case ')*', '))'
                new_regex += item if next_item in [operators['star'], operators['par_final']] else f'{item}.'
            elif item == operators['star']:
                new_regex += item if next_item in operators.values() and next_item != operators['par_initial'] else f'{item}.'
            else:
                new_regex += item
            # print(f'=>{new_regex}')

        self.completed_regex = f'{new_regex}#'
        print(self.completed_regex)


    def __define_alphabet(self, regex: str, operators: dict[str | str]) -> None:
        """
        We define here wich are the symbols of the Regex
        """
        alphabet = {i for i in f'({regex})#' if i not in operators.values()}
        self.alphabet = alphabet


    # def __parse_regex(self, regex):
    #     self.__alphabet = 


class SyntaxTreeBuilder():
    
    operators = {
        'concat': '.',
        'or': '|',
        'star': '*',
        'par_initial': '(',
        'par_final': ')'
    }


    @classmethod
    def build_tree(cls, regex: str) -> SyntaxTree:
        return SyntaxTree(regex, cls.operators)