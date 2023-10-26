from colorama import Back, Style, Fore


class GrowingBoard:
    def __init__(self, start_board):
        self.board = start_board

    def set(self, row, col, val):
        while row >= len(self.board):
            self.board.append([])
        self.board[row].extend([None] * max(0, 1 + col - len(self.board[row])))
        self.board[row][col] = val

    def get(self, row=None, col=None, pos=None):
        if pos:
            row, col = pos.row, pos.col
        if row < len(self.board) and col < len(self.board[row]):
            return self.board[row][col]
        return False

    def __str__(self):
        return "\n".join("".join(x if x else " " for x in row) if row else "" for row in self.board)


class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self):
        return f"Pos {{ row={self.row}, col={self.col} }}"


class Pos2d:
    def __init__(self, start_r, start_c):
        self.start = Pos(start_r, start_c)
        self.end = None

    def set_end(self, row, col):
        self.end = Pos(row, col)

    def __str__(self):
        return f"Pos2d{{ start: { self.start }, end: { self.end } }}"


def print_graph(graph, get_neighbors, get_val):
    all_nodes = get_all_nodes(graph, {}, get_neighbors).values()
    formatted_nodes = format_all_nodes(all_nodes, get_val)
    board, node_to_pos = make_board(formatted_nodes)
    # print("\n".join(str(x) for x in node_to_pos.values()))
    print(node_to_pos)
    make_connections(board, node_to_pos, all_nodes, get_neighbors)
    print('~' * 100)
    print()
    print(board)


def get_all_nodes(node, dic, get_neighbors):
    if id(node) in dic:
        return dic
    dic[id(node)] = node
    for n in get_neighbors(node):
        get_all_nodes(n, dic, get_neighbors)
    return dic


def format_all_nodes(nodes, get_val):
    return [
        ([list(x) for x in str(get_val(node)).split('\n')], id(node))
        for node in nodes
    ]


def make_board(formatted_nodes):
    nodes_to_pos = {}
    padding = 10
    widest_node = max(max(len(x) for x in node) for node, _ in formatted_nodes)
    board_width = max(25, widest_node)
    # formatted_nodes = sorted(formatted_nodes, key=lambda x: len(x))
    nodes_by_row = [[]]
    cur_width = 0
    for node, n_id in formatted_nodes:
        max_ln = max(len(x) for x in node)
        if cur_width + max_ln > board_width:
            nodes_by_row.append([])
            cur_width = 0
        nodes_by_row[-1].append((node, n_id))
        cur_width += max_ln + padding
    board = GrowingBoard([[None] * board_width])
    cur_pos = [0, 0]
    for nodes_row in nodes_by_row:
        max_height = 0
        cur_pos[1] = 0
        for node, n_id in nodes_row:
            nodes_to_pos[n_id] = Pos2d(cur_pos[0], cur_pos[1])
            max_height = max(max_height, len(node))
            for r, row in enumerate(node):
                for c, ch in enumerate(row):
                    board.set(cur_pos[0] + r, cur_pos[1] + c, ch)
            end_col = cur_pos[1] + max(len(x) for x in node)
            nodes_to_pos[n_id].set_end(cur_pos[0] + len(node) - 1, end_col - 1)
            cur_pos[1] = end_col + padding
        cur_pos[0] += max_height + padding
    # total_width = sum(max(len(x) for x in node) for node in formatted_nodes)
    print(board)
    return board, nodes_to_pos


def make_connections(board, node_to_pos, nodes, get_neighbors):
    for node in nodes:
        pos = node_to_pos[id(node)]
        neighbors = get_neighbors(node)
        for neighbor in neighbors:
            n_pos = node_to_pos[id(neighbor)]
            connect_line(pos, n_pos, board)


def get_ports(pos, board):
    for r in range(pos.start.row - 1, pos.end.row + 1):
        if 0 <= r < len(board):
            if pos.start.col > 0:
                yield Pos(r, pos.start.col-1)
            if pos.end.col + 1 < len(board[r]):
                yield Pos(r, pos.end.col+1)
    for c in range(pos.start.col - 1, pos.end.col + 1):
        if 0 <= c:
            if board.get(pos.start.row - 1, c) is not False:
                yield Pos(pos.start.row - 1, c)
            if board.get(pos.end.row + 1, c) is not False:
                yield Pos(pos.end.row + 1, c)



def connect_line(pos1, pos2, board):
    pos1_ports = get_ports(pos1)
    pos2_ports = get_ports(pos2)


    pos1_middle_row = sum(divmod(pos1.start.row + pos1.end.row, 2))
    pos1_middle_col = sum(divmod(pos1.start.col + pos1.end.col, 2))
    pos2_middle_row = sum(divmod(pos2.start.row + pos2.end.row, 2))
    pos2_middle_col = sum(divmod(pos2.start.col + pos2.end.col, 2))

    is_above = lambda p_1, p_2: p_1.row < p_2.row
    is_right = lambda p_1, p_2: p_1.col > p_2.col
    is_left = lambda p_1, p_2: p_1.col < p_2.col

    def set_to(p, to):
        if not board.get(pos=p):
            board.set(p.row, p.col, to)
            return Pos(p.row, p.col)

    def set_ports(fromport, toport, prt):
        if not fromport:
            fromport = prt
        elif port:
            toport = prt
        return fromport, toport

    pos1 = Pos(pos1_middle_row, pos1_middle_col)
    pos1_copy = Pos(pos1_middle_row, pos1_middle_col)
    pos2 = Pos(pos2_middle_row, pos2_middle_col)
    pos2_copy = Pos(pos2_middle_row, pos2_middle_col)
    print(pos1, pos2)
    from_port = False
    to_port = None
    for p1, p2 in [(pos1, pos2), (pos2, pos1)]:
        while is_above(p1, p2) and is_left(p1, p2):
            port = set_to(p1, '\\')
            from_port, to_port = set_ports(from_port, to_port, port)
            p1.row += 1
            p1.col += 1
        while is_above(p1, p2) and is_right(p1, p2):
            port = set_to(p1, '/')
            from_port, to_port = set_ports(from_port, to_port, port)
            p1.row += 1
            p1.col -= 1
        while is_above(p1, p2):
            port = set_to(p1, '|')
            from_port, to_port = set_ports(from_port, to_port, port)
            p1.row += 1
        while is_right(p1, p2):
            port = set_to(p1, '-')
            from_port, to_port = set_ports(from_port, to_port, port)
            p1.col -= 1
    from_port, to_port = closest(from_port, to_port, pos1_copy), closest(from_port, to_port, pos2_copy)
    board.set(from_port.row, from_port.col, Fore.GREEN + 'O' + Style.RESET_ALL)
    board.set(to_port.row, to_port.col, Fore.RED + 'X' + Style.RESET_ALL)


def closest(p1, p2, pos):
    print(pos, p1, p2)
    d1 = (pos.row - p1.row) ** 2 + (pos.col - p1.col) ** 2
    d2 = (pos.row - p2.row) ** 2 + (pos.col - p2.col) ** 2
    return p1 if d1 < d2 else p2
