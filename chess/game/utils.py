

class Square(object):
    FILES = 'abcdefgh'
    RANK = tuple(range(1, 9))
    NULL_FILE = 'z'

    def __init__(self, file, rank, piece=None):
        self.file = file
        self.rank = rank
        self.piece = piece

    def __repr__(self):
        return '%s%s' % (self.file, self.rank)

    def __eq__(self, other):
        return self.file == other.file and \
            self.rank == other.rank

    @property
    def is_out_of_bounds(self):
        return self.rank not in self.RANK or self.file == self.NULL_FILE

    @property
    def is_empty(self):
        return self.piece is None

    def step(self, step):
        rank = self.rank + step[1]

        try:
            file_index = self.FILES.index(self.file) + step[0]
            if file_index < 0:
                raise IndexError()
            file_ = self.FILES[file_index]
        except (ValueError, IndexError):
            file_ = self.NULL_FILE

        return self.__class__(file_, rank)


class Board(object):
    """dict of files"""

    def __init__(self):
        self.position = {f: [Square(f, r) for r in Square.RANK]
                         for f in Square.FILES}

    @property
    def as_descending_rows(self):
        for rank in Square.RANK[::-1]:
            row = [self[Square(file_, rank)]
                   for file_ in Square.FILES]
            yield row

    @property
    def pieces(self):
        flat_squares = [s for row in self.as_descending_rows for s in row]
        return [s.piece for s in flat_squares
                if not s.is_empty]

    def __repr__(self):
        return str(self.position)

    def __getitem__(self, item):
        if type(item) is str:
            assert len(item) == 2
            item = Square(file=item[0], rank=int(item[1]))

        square = None
        try:
            ranks = self.position[item.file]
            square = ranks[item.rank - 1]
        except (IndexError, KeyError):
            pass
        return square

    def __setitem__(self, key, value):
        if type(key) is str:
            assert len(key) == 2
            key = Square(file=key[0], rank=key[1])
        assert isinstance(key, Square)
        assert isinstance(value, Piece)
        square = self[key]
        square.piece = value


class Piece(object):
    STEPS = []
    relative_value = 0
    can_travel = False
    symbol = ''
    WHITE = 'W'
    BLACK = 'B'
    COLORS = (WHITE, BLACK)

    def __init__(self, position, color):
        assert isinstance(position, Square)
        self.position = position
        self.color = color

    @property
    def steps(self):
        if hasattr(self, '_steps'):
            return getattr(self, '_steps')
        return self.STEPS


    def __repr__(self):
        return '%s: %s (%s)' % (self.symbol, self.position, self.color)

    def take_step(self, board, position, step):
        new_position = position.step(step)
        board_position = board[new_position]
        cant_step = board_position is None \
                    or new_position.is_out_of_bounds \
                    or (not board_position.is_empty
                        and board_position.piece.color == self.color)

        if self.square_hosts_enemy(board_position):
            return [new_position]

        if not self.can_travel:
            return [] if cant_step else [new_position]

        # step recursively until direction is exhausted
        return [] if cant_step \
            else [new_position] + self.take_step(board, new_position, step)

    def available_steps(self, board):
        available_steps = []
        for step in self.steps:
            steps_in_that_direction = self.take_step(board, self.position, step)
            available_steps.extend(steps_in_that_direction)

        available_steps.extend(self.special_steps(board))
        return self.filter(available_steps, board)

    def special_steps(self, board=None):
        return []

    def filter(self, available_steps, board):
        return available_steps

    def square_hosts_enemy(self, square):
        return square is not None and \
                not square.is_empty and \
                    square.piece.color != self.color


class Pawn(Piece):
    STEPS = [(0, 1)]
    relative_value = 1
    can_travel = False
    symbol = 'P'

    @property
    def direction(self):
        return 1 if self.color == self.WHITE else -1

    @property
    def _steps(self):
        return [(0, 1 * self.direction)] if not self.has_moved \
            else [(0, 1 * self.direction), (0, 2 * self.direction)]

    @property
    def has_moved(self):
        initial_rank = 2 if self.color == Piece.WHITE else 7
        return self.position.rank == initial_rank

    def special_steps(self, board=None, require_enemy_presence=True):
        steps = []
        top_left = board[self.position.step((-1, 1 * self.direction))]
        top_right = board[self.position.step((1, 1 * self.direction))]
        for attack_square in filter(None, (top_left, top_right)):
            if self.square_hosts_enemy(attack_square) or not require_enemy_presence:
                steps.append(attack_square)

        return steps

    def in_front(self, step):
        return step in map(self.position.step, self._steps)

    def filter(self, available_steps, board):
        for step in self.steps:
            front_position = board[self.position.step(step)]
            if self.square_hosts_enemy(front_position):
                index = available_steps.index(front_position)
                del available_steps[index]

        return available_steps


class Knight(Piece):
    relative_value = 3
    STEPS = [(1, 2), (-1, 2), (1, -2), (-1, -2),
             (2, 1), (-2, 1), (2, -1), (-2, -1)]
    can_travel = False
    symbol = 'N'


class Bishop(Piece):
    relative_value = 3
    STEPS = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    can_travel = True
    symbol = 'B'


class Rook(Piece):
    relative_value = 5
    STEPS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    can_travel = True
    symbol = 'R'


class King(Piece):
    relative_value = 100
    STEPS = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1), ]
    can_travel = False
    symbol = 'K'

    def filter(self, available_steps, board):
        enemy_units = filter(lambda p: p.color != self.color,
                             board.pieces)
        for unit in enemy_units:
            if isinstance(unit, King):
                continue
            elif isinstance(unit, Pawn):
                attack_squares = unit.special_steps(board, require_enemy_presence=False)
                for attack in attack_squares:
                    if attack in available_steps:
                        index = available_steps.index(attack)
                        del available_steps[index]
                continue

            steps = unit.available_steps(board)
            # print(unit, steps)
            for step in steps:
                if step in available_steps:
                    # print(step)
                    index = available_steps.index(step)
                    del available_steps[index]

        return available_steps


class Queen(Piece):
    relative_value = 9
    STEPS = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1),]
    can_travel = True
    symbol = 'Q'


class CommandParser(object):


    @classmethod
    def __call__(self, command):
        if len(command) == 2:
            symbol = Pawn.symbol
            square = Square(command[0], int(command[1]))

        elif len(command) == 3:
            symbol = command[0]
            square = Square(command[1], int(command[2]))

        elif len(command) == 4:
            symbol = command[0]
            square = Square(command[2], int(command[3]))

        else:
            raise ValueError('Wrong command')

        return symbol, square