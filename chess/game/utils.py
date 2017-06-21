

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


# class SquareList(object):
#
#     def __init__(self, *args):
#         self.list = [s for s in args]
#
#     def __repr__(self):
#         return str(self.list)
#
#     def __iter__(self):
#         for s in self.list:
#             yield s
#
#     def __contains__(self, item):
#         for s in self.list:
#             if s == item:
#                 return True
#
#         return False


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
    steps = []
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
        self.original_position = position

    def __repr__(self):
        return '%s: %s (%s)' % (self.symbol, self.position, self.color)

    def take_step(self, board, position, step):
        new_position = position.step(step)
        board_position = board[new_position]
        cant_step = board_position is None \
                    or new_position.is_out_of_bounds \
                    or (not board_position.is_empty
                        and board_position.piece.color == self.color)

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

        return available_steps





class Pawn(Piece):
    steps = [(0, 1)]
    relative_value = 1
    can_travel = False
    symbol = 'P'

    # @property
    # def steps(self):
    #     return [(0, 1)] if self.has_moved else [(0, 1), (0, 2)]

    @property
    def has_moved(self):
        initial_rank = 2 if self.color == Piece.WHITE else 7
        return self.position.rank == initial_rank


class Knight(Piece):
    relative_value = 3
    steps = [(1, 2), (-1, 2), (1, -2), (-1, -2),
             (2, 1), (-2, 1), (2, -1), (-2, -1)]
    can_travel = False
    symbol = 'N'


class Bishop(Piece):
    relative_value = 3
    steps = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    can_travel = True
    symbol = 'B'


class Rook(Piece):
    relative_value = 5
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    can_travel = True
    symbol = 'R'


class King(Piece):
    relative_value = 100
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1), ]
    can_travel = False
    symbol = 'K'


class Queen(Piece):
    relative_value = 9
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
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