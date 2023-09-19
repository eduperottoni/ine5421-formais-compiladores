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
        self.__states = self.__order(self.__states)
        self.__compute_e_closures()
        self.__rebuild_states()
        self.__build_transitions_by_source()
        self.determinize()

    def __order(self, collection: set[str] | list[str]) -> list[str]:
        return sorted(collection)

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
        self.__alphabet: list[str] = sorted(set(splited[3][1:-1].split(',')))

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

        for transition in self.__transitions:
            transition.target = self.__order(transition.target)
        
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
        print_information = {
            'transitions': [],
            'states': []
        }
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
                        print_information['transitions'].append({
                            'source': state,
                            'symbol': symbol,
                            'target': tmp_result
                        })
                        print(f'TRANSIÇÃO: {state} + {symbol} -> {tmp_result}')
                    
                    insert = bool(tmp_result)
                    for item in to_visit_list + visited_list:
                        if item == tmp_result:
                            insert = False

                    if insert: 
                        to_visit_list.append(tmp_result)

        print_information['states'] = visited_list

        self.__print_determinized_af(print_information) 

    def __print_determinized_af(self, information: dict) -> None:
        ## Número de estados do autômao determinizado
        number_of_states = len(information['states'])

        ## Novos estados de aceitação
        final_states = []
        for state in information['states']:
            # Verifica quais dos estados do novo autômato são de aceitação
            if state & self.__final_states and state not in final_states:
                final_states.append(state)
        ordered_final_states = []
        for state in final_states:
            ordered_final_states.append(self.__order(state))

        ## Estado inicial
        initial_state = self.__initial_state

        ## Transições
        ordered_transitions = []
        for t in information['transitions']:
            ordered_transitions.append(
                f'{{{"".join(self.__order(t["source"]))}}},{t["symbol"]},{{{"".join(self.__order(t["target"]))}}}'
            )
        ordered_transitions_str = ';'.join(ordered_transitions)

        print(number_of_states)
        print(initial_state)
        print(final_states)
        print(ordered_transitions_str)
