

class Square(object):
    FILES = 'abcdefgh'
    RANK = tuple(range(8))
    NULL_FILE = 'z'

    def __init__(self, rank, file, piece=None):
        self.rank = rank
        self.file = file
        self.piece = piece

    def __repr__(self):
        return '%s%s' % (self.file, self.rank + 1)

    @property
    def is_out_of_bounds(self):
        return self.rank not in self.RANK or self.file == self.NULL_FILE

    @property
    def is_empty(self):
        return self.piece is None

    def step(self, step):
        rank = self.rank + step[0]
        file_index = self.FILES.index(self.file) + step[1]
        file = self.NULL_FILE if file_index not in self.RANK \
            else self.FILES[file_index]
        return self.__class__(rank, file)


class Board(object):
    """dict of files"""

    def __init__(self):
        self.position = {f: [Square(r, f) for r in Square.RANK]
                         for f in Square.FILES}

    def __repr__(self):
        return self.position

    def __getitem__(self, item):
        try:
            ranks = self.position[item.file]
            return ranks[item.rank]
        except KeyError:
            return None



class Piece(object):
    steps = []
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

        steps = []
        if not cant_step:
            steps.append(new_position)

        if self.can_travel:
            steps.extend(self.take_step(board, new_position, step))

        return steps


    def available_steps(self, board):
        available_steps = []
        for step in self.steps:
            steps_in_that_direction = self.take_step(board, self.position, step)
            available_steps.extend(steps_in_that_direction)

        return available_steps




class Pawn(Piece):
    steps = [(0, 1)]
    can_travel = False

class Knight(Piece):
    steps = [(2, 3), (-2, 3), (2, -3), (-2, -3),
             (3, 2), (-3, 2), (3, -2), (-3, -2)]
    can_travel = False


class Bishop(Piece):
    steps = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    can_travel = True


class Rook(Piece):
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    can_travel = True


class King(Piece):
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1), ]
    can_travel = False


class Queen(Piece):
    steps = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1),]
    can_travel = True