

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
            file = self.FILES[file_index]
        except (ValueError, IndexError):
            file = self.NULL_FILE

        return self.__class__(file, rank)


class Board(object):
    """dict of files"""

    def __init__(self):
        self.position = {f: [Square(f, r) for r in Square.RANK]
                         for f in Square.FILES}

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
        assert isinstance(key, Square)
        assert isinstance(value, Piece)
        square = self[key]
        square.piece = value


class Piece(object):
    steps = []
    relative_value = 0
    can_travel = False
    WHITE = 'W'
    BLACK = 'B'
    COLORS = (WHITE, BLACK)

    def __init__(self, position, color):
        assert isinstance(position, Square)
        self.position = position
        self.color = color
        self.original_position = position

    def take_step(self, board, position, step):
        new_position = position.step(step)
        board_position = board[new_position]
        cant_step = board_position is None \
                    or new_position.is_out_of_bounds \
                    or (not board_position.is_empty
                        and board_position.piece.COLOR == self.color)

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

class Knight(Piece):
    relative_value = 3
    steps = [(2, 3), (-2, 3), (2, -3), (-2, -3),
             (3, 2), (-3, 2), (3, -2), (-3, -2)]
    can_travel = False


class Bishop(Piece):
    relative_value = 3
    steps = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    can_travel = True


class Rook(Piece):
    relative_value = 5
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    can_travel = True


class King(Piece):
    relative_value = 100
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1), ]
    can_travel = False


class Queen(Piece):
    relative_value = 9
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1),]
    can_travel = True