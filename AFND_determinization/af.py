from .transition import Transition

class AF:
    """
    Class to handle with the finite automata
    """
    def __init__(self, input: str):
        self.__load_from_input(input)

    def __load_from_input(self, input: str) -> None:
        splited = input.split(';')

        states_qtt = int(splited[0])
        self.__initial_state: str = splited[1]
        self.__final_states: set[str] = set(splited[2][1:-1].split(','))
        self.__alphabet: set[str] = set(splited[3][1:-1].split(','))


        self.__transitions: set[Transition] = set(Transition(*i.split(',')) for i in splited[4:len(splited)])

        print(f'Estado inicial: {self.__initial_state}')
        print(f'Estados finais: {self.__final_states}')
        print(f'Alfabeto: {self.__alphabet}')
        print(f'Transitions: {self.__transitions}')
        