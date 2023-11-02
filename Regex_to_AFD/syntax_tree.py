from collections import deque
# from typing import Self
from PrettyPrint import PrettyPrintTree
from transition import Transition
from state import State

class SyntaxTreeNode:
    """
    This class is a node of the Syntax Tree
    """
    def __init__(self, symbol: str):
        # Symbol: a operator or an item of the alphabet
        self.symbol = symbol
        # Information needed to AFD tranmformation
        self.nullable = symbol in ('*', '&')
        self.first_pos = None
        self.last_pos = None
        self.id = None
        # Child nodes
        self.__children = []

    @property
    def children(self) -> 'list[Self]':
        return self.__children
    
    @property
    def first_child(self) -> 'Self | None':
        return self.__get_child(0)

    @property
    def last_child(self) -> 'Self | None':
        return self.__get_child(1)

    def __get_child(self, index: int) -> 'Self | None':
        """
        Reusable function to get specified child from list
        """
        try:
            return self.__children[index]
        except:
            return None

    def append_child(self, child: 'Self') -> None:
        self.__children.append(child)


class SyntaxTree:
    """
    Class to represent the Syntax Tree
    """
    def __init__(self, regex: str, operators: tuple[str]):
        self.__define_alphabet(regex, operators)
        self.__complete_regex(regex)
        self.root = SyntaxTreeNode(None)
        self.aux_stack = deque()
        self.__create_tree(self.completed_regex, self.root)

        self.__id_counter: int = 1
        self.__leaf_nodes = {}
        self.__followpos = {}

        self.__process_in_post_order(self.root)
        self.__create_followpos(self.root)
    
    def __define_alphabet(self, regex: str, operators: dict[str | str]) -> None:
        """
        We define here wich are the symbols of the Regex
        """
        alphabet = {i for i in f'({regex})#' if i not in operators.values()}
        self.alphabet = alphabet
        print(f'Alphabet defined: {self.alphabet}')

    
    def __complete_regex(self, regex: str) -> None:
        """
        Adds the final symmbol ('#') and the concats ('.') in the regex 
        """
        masked_regex = f'({regex})#'
        new_regex = ''
        
        for index, item in enumerate(masked_regex[:-1]):
            next_item = masked_regex[index + 1]
            if item in self.alphabet:
                new_regex += item if next_item in [')', '*', '|'] else f'{item}.'
            elif item == ')':
                new_regex += item if next_item in ['*', ')'] else f'{item}.'
            elif item == '*':
                new_regex += item if next_item in ['.', '|', ')'] else f'{item}.'
            else:
                new_regex += item

        self.completed_regex = f'{new_regex}#'
        print(f"Regex's completeness result: {self.completed_regex}")


    def __create_tree(self, regex: str, root: SyntaxTreeNode) -> None:
        """
        Recursive function that creates nodes from a root one
        """
        # Base case (we have just one symbol)
        if len(regex) == 1:
            root.symbol = regex
        # If we have operations -> we call this function recursvely
        else:
            # 1 - We find out the position of the operator which can split the regex
            operator, position = self.__search_operator_position(regex)
            # 2 - This operator will be the root of the new subtree
            root.symbol = operator
            # 3 - We get the splitted parts 
            left, right = self.__divide_regex(regex, position)
            print(f'Calling recursively: {left}')
            print(f'Calling recursively: {right}')
            # 4 - We create new nodes and call recursively to each one
            root.append_child(SyntaxTreeNode(None))
            self.__create_tree(left, root.first_child)
            if right:
                root.append_child(SyntaxTreeNode(None))
                self.__create_tree(right, root.last_child)


    def __search_operator_position(self, regex):
        """
        Considering the regex, we found out the position of the last
        occurrence of one of the operators, in inverse order of precedence
        """
        print(f'Searching operator {regex}')
        # We search in the inverse order of natural precedence
        for oper in ['|', '.', '*']:
            self.aux_stack.clear()
            for index, item in enumerate(regex[::-1]):
                # We are passign through a new level of depth
                if item == ')': self.aux_stack.append(item)
                # We are leaving a deeper level
                elif item == '(': self.aux_stack.pop()
                # We could only consider current level of depth
                elif not bool(self.aux_stack):
                    if item == oper:
                        return oper, len(regex) - index - 1


    def __divide_regex(self, regex: str, position: int) -> tuple[str, str]:
        """
        We split the regex in two parts based on the position of the
        operator with less precedence
        """
        # If position is zero, we are in case of a * operation
        left = regex[:position]
        right = regex[position + 1 :] if position > 0 else None

        new_list = []
        # 1 - We discard unecessary parenthesis
        for i in [left, right]:
            if i:
                has_extra, carac = self.__has_extra_parenthesis(i)
                if not has_extra:
                    if i[0] == '(' and i[-1] != '*': i = i[1:]
                    if i[-1] == ')': i = i[:-1]
                else:
                    if carac == '(':
                        i.replace(carac, '', 1)
                    elif carac == ')':
                        rev_s = i[::-1]
                        i = len(i) - rev_s.index(carac) - 1
                        i = i[:i] + i[i+1:]
            new_list.append(i)

        return new_list


    def __has_extra_parenthesis(self, regex: str) -> (bool, str):
        """
        Analyses whether the regex contains extra parenthesis
        """        
        stack = deque()
        for item in regex:
            if item == '(': stack.append(item)
            elif item == ')':
                # If empty while reading ')'
                if not bool(stack):
                    return True, ')'
                else:
                    stack.pop()

        # To be validated, stack must be empty
        is_empty = not bool(stack)

        return not is_empty, '(' if not is_empty else None
    

    def __process_in_post_order(self, node: SyntaxTreeNode) -> None:
        """
        Recursive method to set firstpos and lastpos;
        Goes through the tree in post-order
        """
        if node.first_child is not None:
            self.__process_in_post_order(node.first_child)

        if node.last_child is not None:
            self.__process_in_post_order(node.last_child)

        self.__set_firstpos_and_lastpos(node)


    def __set_firstpos_and_lastpos(self, node: SyntaxTreeNode) -> None:
        """
        Atribute values to firstpos, lastpos and nullable attributes of nodes
        """
        if node.symbol == '&':
            node.nullable = True

        elif node.symbol == '|':

            node.first_pos = [
                pos
                for child in [node.first_child, node.last_child]
                for pos in (child.first_pos or [])
                if pos != []
            ]
            node.last_pos = [
                pos
                for child in [node.first_child, node.last_child]
                for pos in (child.last_pos or [])
                if pos != []
            ]

            if node.first_child.nullable or node.last_child.nullable:
                node.nullable = True

        elif node.symbol == '*':
            node.first_pos = [pos for pos in node.first_child.first_pos if pos != []]
            node.last_pos = [pos for pos in node.first_child.last_pos if pos != []]
            node.nullable = True

        elif node.symbol == '.':
            if node.first_child.nullable and node.last_child.nullable:
                node.nullable = True

            if node.first_child.nullable:
                node.first_pos = [
                    pos
                    for child in [node.first_child, node.last_child]
                    for pos in child.first_pos
                ]
            else:
                node.first_pos = [pos for pos in node.first_child.first_pos]

            if node.last_child.nullable:
                node.last_pos = [
                    pos
                    for child in [node.first_child, node.last_child]
                    for pos in child.last_pos
                ]
            else:
                node.last_pos = [pos for pos in node.last_child.last_pos]
        
        else:
            node.id = self.__id_counter
            self.__leaf_nodes[self.__id_counter] = node
            self.__followpos[self.__id_counter] = set()

            self.__id_counter += 1

            node.first_pos = [node.id]
            node.last_pos = [node.id]


    def __create_followpos(self, node: SyntaxTreeNode) -> None:
        """
        Create the followpos for each node with a symbol from expression alphabet in the tree
        """
        # traverse in post-order
        if node.first_child is not None:
            self.__create_followpos(node.first_child)

        if node.last_child is not None:
            self.__create_followpos(node.last_child)

        if node.symbol in ['.', '*']: self.__set_followpos(node)

    
    def __set_followpos(self, node: SyntaxTreeNode) -> None:
        """
        Set followpos to concat or star node
        """
        match node.symbol:
            case '*':
                for n in node.last_pos:
                    for id in node.first_pos:
                        self.__followpos[n].add(id)
            case '.':
                for n in node.first_child.last_pos:
                    for id in node.last_child.first_pos:
                        self.__followpos[n].add(id)


    def to_afd(self):
        print('-'*30)
        print(f'LEAF NODES: {self.__leaf_nodes}')
        print('-'*30)
        print(f'FOLLOWPOS: {self.__followpos}')
        print('-'*30)
        states = [self.__get_initial_state()]
        visited_states = []
        final_states = []
        transitions = []
        
        final_id = list(self.__leaf_nodes.keys())[-1]
        print(f'ID FINAL = {final_id}')
        while states:
            state = states.pop(0)
            visited_states.append(state)

            print(f'CURRENT STATE: {state}')
            # Checking if it's a final state
            if final_id in state:
                final_states.append(state)
            
            new_transitions = self.__create_transitions(state)
            transitions.extend(new_transitions)

            for transition in new_transitions:
                if transition.target != []:
                    new_state = transition.target
                    if not self.__check_state_already_created(new_state, visited_states):
                        states.append(new_state)
            
        print(visited_states)
        print(final_states)
        print(transitions)


    def __check_state_already_created(self, state: list[int], states_list:list[list[int]]) -> bool:
        print(f'{state} já existe?')
        print(states_list)
        exist = False
        for s in states_list:
            if len(s) == len(state):
                for index, item in enumerate(s):
                    exist = True if state[index] == item else False
                if exist == True:
                    print('Sim')
                    return True
        print('não')
        return False


    def __create_transitions(self, state: list[int]):
        """
        Creating transitions
        """
        transitions = {}
        print(f'STATE: {state}')
        for id in state:
            # Create transition by symbol
            symbol = self.__leaf_nodes[id].symbol
            followpos = self.__followpos[id]
            if symbol in transitions:
                for i in followpos:
                    transitions[symbol].add(i)
            else:
                transitions[symbol] = set(followpos)
        
        transitions_list = []
        for symbol, target in transitions.items():
            print(f'SYMBOL: {symbol}')
            print(f'TARGET: {target}')
            t = Transition(state, symbol, sorted(list(target)))
            transitions_list.append(t)
        
        return transitions_list



    def __get_initial_state(self) -> list[int]:
        return self.root.first_pos


    def pretty_print(self):
        """
        Using PrettyPrintTree lib to print our Syntax Tree
        """

        pt = PrettyPrintTree(
            lambda x: x.children,
            lambda x: f'{x.first_pos if x.first_pos else x.id} {x.symbol} {x.last_pos if x.last_pos else x.id}' 
        )
        pt(self.root)

        print('Numbered nodes: ')
        for k, v in self.__leaf_nodes.items():
            print(f'{k} - {v.symbol}')
