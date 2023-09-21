from .transition import Transition
import logging
from copy import deepcopy

logging.basicConfig(level=logging.DEBUG)

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


    def __order(self, collection: set[str] | list[str]) -> list[str]:
        return sorted(collection)
    

    def __filter_transitions(self, symbol: str) -> set[Transition]:
        """
        Seach for the transitions that have this specific symbol
        """
        filtered = set()
        for t in self.__transitions:
            if t.symbol == symbol:
                filtered.add(t)
        return filtered


    def __build_transitions_by_source(self) -> None:
        """
        Build a dict of transitions with source state as dict key
        """
        for transition in self.__transitions:
            if transition.source in self.__transitions_by_source.keys():
                self.__transitions_by_source[transition.source].add(transition)
            else:
                self.__transitions_by_source[transition.source] = {transition, }

        # logging.debug(f'Transições por source: {self.__transitions_by_source}')


    def __compute_e_closures(self):
        if self.__has_e_transitions:
            self.__generate_deep_e_closures()
        else:
            self.__generate_simple_e_closures()
        
        # logging.debug(f'&-fechos: {self.__e_closure}')


    def __generate_simple_e_closures(self):
        """
        &-closure is the state itself
        """
        for state in self.__states:
            self.__e_closure[state] = {state}

    
    def __generate_deep_e_closures(self):
        """
        Generates &-closure of the states based on &-transitions
        """
        for state in self.__states:
            # logging.debug(f'BUSCANDO FECHO DO ESTADO {state}')
            e_closure: set[str] = set(state)
            self.__e_closure[state] = self.__deep_search_e_closure(e_closure, 
                                                                   state, 
                                                                   self.__filter_transitions('&'))


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


    def __load_from_input(self, input: str) -> None:
        """
        Loads the Automata from a string
        """
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
        

        # TODO Uncomment below command when Jerusa fix the input
        # assert states_qtt == len(self.__states)

        # logging.debug(f'Estado inicial: {self.__initial_state}')
        # logging.debug(f'Estados finais: {self.__final_states}')
        # logging.debug(f'Estados: {self.__states}')
        # logging.debug(f'Alfabeto: {self.__alphabet}')
        # logging.debug(f'Transitions: {self.__transitions}')
        # logging.debug(f'Has &-transitions: {self.__has_e_transitions}')


    def __rebuild_initial_state(self) -> None:
        """
        Rebuild the states based on the sets created in targets
        """
        self.__initial_state = self.__e_closure[self.__initial_state]

        # logging.debug(f'STATES REBUILDED: {self.__states}')


    # TODO Remove this, and make something more generic
    def __get_transition_by_source_and_symbol(self, source: str, symbol: str) -> Transition | None:
        
        for transition in self.__transitions_by_source[source]:
            if transition.symbol == symbol:
                return transition
        return None


    def determinize(self) -> None:
        """
        Macro algorithm to determinization
        """
        self.__compute_e_closures()
        self.__rebuild_initial_state()
        self.__build_transitions_by_source()
        self.__execute_determinization()


    def __execute_determinization(self):
        """
        Execute main algorith of determinization
        """
        to_visit_list = [self.__initial_state]
        visited_list = []
        self.__determinized_transitions = []
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
                        self.__determinized_transitions.append(Transition(state, symbol, tmp_result))
                    
                    insert = bool(tmp_result)
                    for item in to_visit_list + visited_list:
                        if item == tmp_result:
                            insert = False

                    if insert: 
                        to_visit_list.append(tmp_result)

        self.__determinized_states = visited_list

        self.__format_and_print_af(self.__determinized_states, self.__determinized_transitions, True) 

    
    def minimize(self) -> None:
        """
        Macro algorithm to miniminization
        """
        self.__compute_unreachable_states()
        self.__compute_dead_states()
        self.__compute_equivalent_states()

    
    def __compute_unreachable_states(self) -> None:
        """
        Computes the unreachable states, creating new transitions
        and states sets without this computed states
        """
        self.__minimized_transitions = set()
        to_visit, visited = [self.__initial_state], []

        # Busca pelos inalcançáveis
        while len(to_visit) > 0:
            state = to_visit.pop(0)
            visited.append(state)

            reachable, transitions = self.__get_all_target_states_and_transitions(state)

            for state in reachable:
                if state not in to_visit and state not in visited:
                    to_visit.append(state)

            self.__minimized_transitions |= transitions
        
        self.__minimized_states = set(visited) & set(self.__states)
        self.__minimized_final_states = set(visited) & self.__final_states
        # logging.debug(f'States after computing of unreachable: {self.__minimized_states}')

    
    def __get_all_target_states_and_transitions(self, state: str) -> list[str]:
        """
        Returns all reachable states and transitions from specified state
        """
        reachable, transitions = set(), set()
        for transition in self.__transitions:
            if transition.source == state:
                reachable.add(transition.target[0])
                transitions.add(transition)
        return reachable, transitions


    def __compute_dead_states(self) -> None:
        """
        Computes dead states and updates the minimized structures
        """
        to_visit, visited = list(self.__minimized_final_states), []

        # Seach for the dead states
        while len(to_visit) > 0:
            state = to_visit.pop(0)
            visited.append(state)

            not_dead, transitions = self.__get_all_source_states_and_transitions(state)

            for state in not_dead:
                if state not in visited and state not in to_visit:
                    to_visit.append(state)

            self.__minimized_transitions |= transitions

        self.__minimized_states = set(visited) & self.__minimized_states
        self.__minimized_final_states = set(visited) & self.__minimized_final_states
        # logging.debug(f'States after computing dead: {self.__minimized_states}')


    def __get_all_source_states_and_transitions(self, state: str) -> list[str]:
        """
        Returns all reachable source states from specified target_state
        """
        reachable, transitions = set(), set()
        for transition in self.__minimized_transitions:
            if transition.target[0] == state:
                reachable.add(transition.source)
                transitions.add(transition)
        return reachable, transitions


    def __compute_equivalent_states(self) -> None:
        """
        Algorithm to separe the states to equivalent states sets
        """
        # We store a copy from last alphabet interation and a current equivalent
        current_eq_states = {frozenset(self.__minimized_final_states), frozenset(self.__minimized_states - self.__minimized_final_states)}
        last_eq_states = deepcopy(current_eq_states)

        while True:
            # For each transition
            for symbol in self.__alphabet:
                # logging.debug(f'Symbol: {symbol}')

                new_eq_states = set()
                # For each equivalent set in current_states 
                for _set in current_eq_states:
                    # logging.debug(f'Set: {_set}')

                    current_set = set()

                    # Dicionário auxiliar para mapear quem pode chegar nos determinados conjuntos
                    # Preenche o dicionário auxiliar de acordo com as transições de cada estado
                    new_sets = self.__create_auxiliary_dict(current_eq_states)
                    # logging.debug(f'Auxiliary dict: {new_sets}')

                    # A cada conjunto de cada conjunto, eu crio novos conjuntos baseados em onde eles apontam
                    for state in _set:

                        transition = self.__get_transition_by_source_and_symbol(state, symbol, self.__minimized_transitions)
                        target = transition.target[0]
                        inserted = False
                        
                        """
                        If target in set, state continue in the same equivalent states
                        If target in other equivalente set, state will be added as value of the key with this equivalent set
                        If target goes to a dead state, state will be added in the death key of the auxiliar dict
                        """
                        if target in _set:
                            # logging.debug(f'state {state} added in current_set')
                            current_set.add(state)
                            inserted = True
                        else:
                            for key in new_sets:
                                if target in key:
                                    # logging.debug(f'state {state} added in new_sets')
                                    new_sets[key].add(state)
                                    inserted = True

                        if not inserted:
                            # logging.debug(f'state {state} added in death')
                            new_sets['death'].add(state)                    
                    
                    # logging.debug(f'CURRENT_SET: {current_set}')
                    # logging.debug(f'NEW_SETS: {new_sets}')

                    new_set = set()
                    if current_set:
                        new_set.add(frozenset(current_set))
                    for _set in new_sets.values():
                        if _set:
                            new_set.add(frozenset(_set))

                    # logging.debug(f'NEW_CURRENT_EQ: {new_set}')
                    new_eq_states |= new_set
                
                current_eq_states = new_eq_states
            
            if len(current_eq_states) == len(self.__minimized_states) or last_eq_states == current_eq_states:
                break

            # Atualizo o último set calculado apenas quando tiver calculado para todo o alfabeto
            last_eq_states = current_eq_states


        self.__minimized_states = [self.__order(set(frozen)) for frozen in current_eq_states]
        self.__minimized_states_unique_name = [item[0] for item in self.__minimized_states]
        self.__update_transitions_source_and_target_names()
        self.__remove_redundant_transitions()
        
        self.__minimized_states = [{item[0]} for item in self.__minimized_states_unique_name]
        self.__minimized_states.remove({self.__initial_state})
        self.__minimized_states.insert(0, {self.__initial_state})

        self.__format_and_print_af(self.__minimized_states, list(self.__minimized_transitions), False)

    
    def __get_transition_by_source_and_symbol(self, source: str, symbol: str, transitions: list | set) -> Transition | None:
        """
        Filter transitions by a source and a symbol
        """
        for t in transitions:
            if t.source == source and t.symbol == symbol:
                return t
        return None


    def __create_auxiliary_dict(self, eq_sets: set[str]) -> None:
        """
        Creates auxiliary dict based on the current equivalent sets
        """
        aux_dict = {}

        for _set in eq_sets:
            aux_dict[_set] = set()
        aux_dict['death'] = set()

        return aux_dict
    

    def __update_transitions_source_and_target_names(self) -> None:
        """
        Update transition's states names with the new name of the equivalent state
        """
        for transition in self.__minimized_transitions:
            # logging.debug(f'Transition before modified: {transition}')
            for index, state in enumerate(self.__minimized_states):
                if transition.source in state:
                    transition.source = self.__minimized_states_unique_name[index]
                if transition.target[0] in state:
                    transition.target = [self.__minimized_states_unique_name[index]]
            # logging.debug(f'Transition modified: {transition}')


    def __remove_redundant_transitions(self):
        """
        When we have equivalent states, we can remove redundant transitions
        """
        new_transitions = set()
        for transition in self.__minimized_transitions:
            # We only want what gets out of current minimized states
            # and what does not goes to dead states
            if transition.source in self.__minimized_states_unique_name and\
               transition.target[0] in self.__minimized_states_unique_name:
                new_transitions.add(transition)
        self.__minimized_transitions = new_transitions


    def __format_and_print_af(self, states_list: list[set[str]], transitions_list: list[Transition], states_as_sets: bool) -> None:
        """
        Formats the output string and print the result
        """
        
        ## Número de estados do autômao determinizado
        number_of_states = len(states_list)

        ## Novos estados de aceitação
        final_states = []
        for state in states_list:
            # Verifica quais dos estados do novo autômato são de aceitação
            if state & self.__final_states and state not in final_states:
                final_states.append(state)

        ordered_final_states = []
        for state in final_states:
            state_str = "".join(self.__order(state))
            ordered_final_states.append(
                f'{{{state_str}}}' if states_as_sets else state_str
            )
        ordered_final_states_str = f'{{{",".join(ordered_final_states)}}}'

        ## Alfabeto sem epsilon
        alphabet = self.__alphabet.copy()
        if self.__has_e_transitions: alphabet.remove('&') 
        alphabet_str = f'{{{",".join(alphabet)}}}'

        ## Estado inicial
        initial_state = "".join(self.__order(states_list[0]))
        initial_state_str = f'{{{initial_state}}}' if states_as_sets else initial_state

        ## Transições
        transitions = [{'source': t.source, 'symbol': t.symbol, 'target': t.target} for t in transitions_list]

        for t in transitions:
            t['source'] = "".join(self.__order(t['source']))

        # Ordena as transições pelo source da transição e depois pelo symbol
        ordered_transitions = sorted(transitions, key=lambda x: (x['source'], x['symbol']))

        ordered_transitions_str = []
        for t in ordered_transitions:
            source = "".join(self.__order(t["source"]))
            target = "".join(self.__order(t["target"]))
            ordered_transitions_str.append(
                f'{{{source}}},{t["symbol"]},{{{target}}}' if states_as_sets else f'{source},{t["symbol"]},{target}'
            )
            
        ordered_transitions_str = ';'.join(ordered_transitions_str)
        
        final_str = ';'.join([str(number_of_states), initial_state_str, ordered_final_states_str, alphabet_str, ordered_transitions_str])

        print(final_str)
