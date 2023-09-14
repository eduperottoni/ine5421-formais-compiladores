from .transition import Transition

class AF:
    """
    Class to handle with the finite automata
    """
    def __init__(self, input: str):
        self.__states: set[str] = set()
        self.__has_e_transitions: bool = False
        self.__transitions: set[Transition] = set()
        self.__e_closure = {}
        self.__transitions_by_source = {}
        self.__load_from_input(input)
        self.__compute_e_closures()
        self.__rebuild_states()
        self.__build_transitions_by_source()
        self.determinize()

    def __build_transitions_by_source(self) -> None:
        for transition in self.__transitions:
            if transition.source in self.__transitions_by_source.keys():
                self.__transitions_by_source[transition.source].add(transition)
            else:
                self.__transitions_by_source[transition.source] = {transition, }

        print(f'Transições por source: {self.__transitions_by_source}')

    def __compute_e_closures(self):
        if self.__has_e_transitions:
            self.__generate_deep_e_closures()
        else:
            self.__generate_simple_e_closures()
        
        print(f'&-fechos: {self.__e_closure}')


    def __deep_search_e_closure(self, e_closure: set[str], state: str, transitions: set[Transition]):
        """
        deep search for calculation of 
        """
        for transition in transitions:
            if state == transition.source:
                e_closure.add(*transition.target)
                for target in transition.target:
                    return self.__deep_search_e_closure(e_closure, target, transitions)
        return e_closure
    

    def __generate_deep_e_closures(self):
        for state in self.__states:
            print(f'BUSCANDO FECHO DO ESTADO {state}')
            e_closure: set[str] = set(state)
            self.__e_closure[state] = self.__deep_search_e_closure(e_closure, 
                                                                   state, 
                                                                   self.__filter_transitions('&'))


    def __generate_simple_e_closures(self):
        for state in self.__states:
            self.__e_closure[state] = {state}


    def __filter_transitions(self, symbol: str) -> set[Transition]:
        filtered = set()
        for t in self.__transitions:
            if t.symbol == symbol:
                filtered.add(t)
        return filtered


    def __load_from_input(self, input: str) -> None:
        splited = input.split(';')

        states_qtt = int(splited[0])
        self.__initial_state: str = splited[1]
        self.__final_states: set[str] = set(splited[2][1:-1].split(','))
        self.__alphabet: set[str] = set(splited[3][1:-1].split(','))

        # Loading transitions
        for transition in splited[4:len(splited)]:
            source, symbol, target = transition.split(',')

            self.__states.add(source)
            self.__states.add(target) 

            if symbol == '&':
                self.__has_e_transitions = True

            transition_exists = False
            # Adds target on existent transitions or create new ones
            if len(self.__transitions) > 0 :
                for transition in self.__transitions:
                    # Add new target for already read transition
                    if source == transition.source and symbol == transition.symbol:
                        transition.target.add(target)
                        transition_exists = True
            # New transition
            if not transition_exists:
                new_transition = Transition(source, symbol, set(target))
                self.__transitions.add(new_transition)

        assert states_qtt == len(self.__states)

        print(f'Estado inicial: {self.__initial_state}')
        print(f'Estados finais: {self.__final_states}')
        print(f'Estados: {self.__states}')
        print(f'Alfabeto: {self.__alphabet}')
        print(f'Transitions: {self.__transitions}')
        print(f'Has &-transitions: {self.__has_e_transitions}')

    def __rebuild_states(self) -> None:
        """
        Rebuild the states based on the sets created in targets
        """

        if self.__has_e_transitions:
            self.__initial_state = self.__e_closure[self.__initial_state]

        print(f'STATES REBUILDED: {self.__states}')

    def __get_transition_by_source_and_symbol(self, source: str, symbol: str) -> Transition | None:
        
        for transition in self.__transitions_by_source[source]:
            if transition.symbol == symbol:
                return transition
        return None
        


    def determinize(self):
        to_visit_list = [self.__initial_state]
        visited_list = []
        while len(to_visit_list) > 0:

            state = to_visit_list.pop(0)
            state = set(state) if not isinstance(state, set) else state
            visited_list.append(state)


            # Para cada subestado
            for symbol in self.__alphabet:
                if symbol != '&':
                    tmp_result = set()
                    for substate in state:
                        if substate in self.__transitions_by_source.keys():
                            transition = self.__get_transition_by_source_and_symbol(substate, symbol)
                            if transition:
                                for target in transition.target:
                                    tmp_result |= self.__e_closure[target]

                    if tmp_result:
                        print(f'TRANSIÇÃO: {state} + {symbol} -> {tmp_result}')
                    
                    insert = bool(tmp_result)
                    for item in to_visit_list + visited_list:
                        if item == tmp_result:
                            insert = False

                    if insert: 
                        to_visit_list.append(tmp_result)
            
        print(f'LISTA DE ESTADOS: {visited_list}')
