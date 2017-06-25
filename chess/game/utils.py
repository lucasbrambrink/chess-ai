from copy import deepcopy
from hashlib import sha256


class Square(object):
    FILES = 'abcdefgh'
    RANK = tuple(range(1, 9))
    NULL_FILE = 'z'

    def __init__(self, file, rank, piece=None):
        self.file = file
        self.rank = int(rank)
        self.piece = piece

    def __iter__(self):
        yield ('position', self.__repr__())

    def __repr__(self):
        return '%s%s' % (self.file, self.rank)

    def __eq__(self, other):
        return self.file == other.file and \
            self.rank == other.rank

    def __hash__(self):
        return int('%s%s' % (self.FILES.index(self.file), self.rank))

    @property
    def is_out_of_bounds(self):
        return self.rank not in self.RANK or self.file == self.NULL_FILE

    @property
    def is_empty(self):
        return self.piece is None

    @classmethod
    def is_hosting_enemy(cls, square, color):
        return square is not None and \
                not square.is_empty and \
                    square.piece.color != color

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

    @staticmethod
    def as_consumable_move(move_to_square, piece):
        consumable_move = str(move_to_square)
        if move_to_square in King.CASTLING_MOVES:
            consumable_move = str(piece.position.step(
                King.CASTLING_MOVES[move_to_square]
            ))
        return consumable_move


class Board(object):
    """dict of files"""

    def __init__(self):
        self.position = {f: [Square(f, r) for r in Square.RANK]
                         for f in Square.FILES}
        self.moves = []

    @property
    def as_descending_rows(self):
        for rank in reversed(Square.RANK):
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
        """
        allow lookup via location string or Square instance
        """
        if type(item) is str:
            assert len(item) == 2
            item = Square(file=item[0], rank=int(item[1]))
        else:
            assert isinstance(item, Square)

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

    def get_king(self, color):
        king = next((p for p in self.pieces
                     if p.color == color and p.symbol == King.symbol))
        assert king is not None and isinstance(king, King)
        return king

    def castle(self, command, color):
        king = self.get_king(color)
        files = 'hgf' if command == King.CASTLE_KING_SIDE else 'acd'
        rook_position = Square(files[0], king.position.rank)
        new_king_position = Square(files[1], king.position.rank)
        new_rook_position = Square(files[2], king.position.rank)
        rook = self[rook_position].piece
        self.move_piece(new_rook_position, rook)
        self.move_piece(new_king_position, king)
        self.moves.append((color, command))

    def step(self, command, color):
        args = CommandParser.__call__(command)
        symbol, square, is_attack_move, special_file, special_rank, castle = args

        if castle is not None:
            return self.castle(castle, color)

        all_pieces = self.pieces
        if special_file is not None:
            all_pieces = filter(lambda p: p.position.file == special_file,
                                all_pieces)
            if special_rank is not None:
                all_pieces = filter(lambda p: p.position.rank == special_rank,
                                    all_pieces)

        allow_special_steps = is_attack_move or symbol == King.symbol
        possible_pieces = [piece for piece in all_pieces
                           if (piece.color == color and
                               piece.symbol == symbol and
                               square in piece.available_steps(self,
                                                               allow_special_steps=allow_special_steps,
                                                               translate=True)
                               )
                           ]
        if len(possible_pieces) != 1:
            print(possible_pieces)
            # import ipdb; ipdb.set_trace()
            raise ValueError('That command is ambiguous')

        piece = possible_pieces[0]

        # test if move evades check
        hypothetical_board = deepcopy(self)
        hypothetical_board.moves = []
        hypothetical_board.execute_move(deepcopy(piece), color, deepcopy(square), is_attack_move)
        king = hypothetical_board.get_king(color)
        if king.is_in_check(hypothetical_board):
            raise ValueError('King is still in check after move')

        self.execute_move(piece, color, square, is_attack_move)

    def execute_move(self, piece, color, square, is_attack_move):
        if isinstance(piece, King) and piece.translate_move(square) in King.CASTLING_MOVES:
            return self.castle(piece.translate_move(square), piece.color)

        self.move_piece(square, piece)
        self.moves.append((color, piece.get_canonical_step(self, square, is_attack_move)))

    def move_piece(self, square, piece):
        piece.previous_position = str(piece.position)
        self[piece.position].piece = None
        piece.position = square
        self[piece.position] = piece
        piece.has_moved = True

    def king_is_in_check(self):
        for color in Piece.COLORS:
            king = self.get_king(color)
            if king.is_in_check(self):
                return (True, king)

        return (False, None)


class Piece(object):
    STEPS = []
    relative_value = 0
    can_travel = False
    symbol = ''
    WHITE = 'w'
    BLACK = 'b'
    COLORS = (WHITE, BLACK)

    def __init__(self, position, color, has_moved=False, previous_position=None):
        assert isinstance(position, Square)
        self.position = position
        self.color = color
        self.has_moved = has_moved
        self.previous_position = previous_position

    def __iter__(self):
        yield ('symbol', self.symbol)
        yield ('position', str(self.position))
        yield ('color', self.color)
        yield ('has_moved', self.has_moved)
        yield ('previous_position', self.previous_position)

    @property
    def steps(self):
        if hasattr(self, '_steps'):
            return getattr(self, '_steps')
        return self.STEPS

    @property
    def color_canonical(self):
        return 'white' if self.color == self.WHITE else 'black'

    @property
    def name(self):
        return '{}_{}'.format(self.color_canonical,
                              self.__class__.__name__.lower())

    def __repr__(self):
        return '%s: %s (%s)' % (self.symbol, self.position, self.color)

    def take_step(self, board, position, step):
        new_position = position.step(step)
        board_position = board[new_position]
        cant_step = board_position is None \
                    or new_position.is_out_of_bounds \
                    or (not board_position.is_empty
                        and board_position.piece.color == self.color)

        if cant_step:
            return []

        if Square.is_hosting_enemy(board_position, self.color) or \
                not self.can_travel:
            return [new_position]

        # step recursively until direction is exhausted
        return [new_position] + self.take_step(board, new_position, step)

    def available_steps(self, board, dont_filter=False, allow_special_steps=True, translate=False):
        available_steps = []
        for step in self.steps:
            steps_in_that_direction = self.take_step(board, self.position, step)
            available_steps.extend(steps_in_that_direction)
        if allow_special_steps:
            available_steps.extend(self.special_steps(board, translate=translate))
        return self.filter(set(available_steps), board, dont_filter=dont_filter)

    def special_steps(self, board, require_enemy_presence=True, translate=False):
        return []

    def filter(self, available_steps, board, dont_filter=False):
        return available_steps

    def get_step(self, new_position):
        return '%s%s' % (self.symbol, new_position)

    def get_canonical_step(self, board, new_position, is_attack_move):
        symbol = self.symbol
        if isinstance(self, Pawn):
            symbol = '' if not is_attack_move else self.previous_position[0]
        attack_char = 'x' if is_attack_move else ''
        is_in_check, _ = board.king_is_in_check()
        check_mark = '!' if is_in_check else ''
        return '{}{}{}{}'.format(symbol, attack_char, new_position, check_mark)




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
        return [(0, 1 * self.direction)] if self.has_moved \
            else [(0, 1 * self.direction), (0, 2 * self.direction)]

    # @property
    # def has_moved(self):
    #     initial_rank = 2 if self.color == Piece.WHITE else 7
    #     return self.position.rank == initial_rank

    def special_steps(self, board, require_enemy_presence=True, translate=False):
        steps = []
        top_left = board[self.position.step((-1, 1 * self.direction))]
        top_right = board[self.position.step((1, 1 * self.direction))]
        adjacent_left = board[self.position.step((-1, 0))]
        adjacent_right = board[self.position.step((1, 0))]
        for attack_square in filter(None, (top_left, top_right)):
            if Square.is_hosting_enemy(attack_square, self.color) or not require_enemy_presence:
                steps.append(attack_square)

        # enpassant
        for pair in filter(lambda p: all, ((adjacent_left, top_left),
                                           (adjacent_right, top_right))):
            adjacent_square, adjacent_front = pair
            if Square.is_hosting_enemy(adjacent_square, self.color) and \
                isinstance(adjacent_square.piece, Pawn) and \
                    adjacent_front.is_empty:
                steps.append(adjacent_front)

        return steps

    def in_front(self, step):
        return step in map(self.position.step, self._steps)

    def filter(self, available_steps, board, dont_filter=False):
        for step in self.steps:
            front_position = board[self.position.step(step)]
            if Square.is_hosting_enemy(front_position, self.color):
                available_steps.remove(front_position)

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
    CASTLE_KING_SIDE = 'O-O'
    CASTLE_QUEEN_SIDE = 'O-O-O'
    CASTLING_MOVES = {
        CASTLE_KING_SIDE: (2, 0),
        CASTLE_QUEEN_SIDE: (-2, 0)
    }
    symbol = 'K'

    def translate_move(self, move, reverse=False):
        if self.has_moved:
            return move

        if reverse and move in self.CASTLING_MOVES:
            file_ = 'g' if self.CASTLE_KING_SIDE == move else 'c'
            return Square(file_, self.position.rank)

        if not self.has_moved:
            if move in (Square('g', 1), Square('g', 8)):
                return self.CASTLE_KING_SIDE
            elif move in (Square('c', 1), Square('c', 8)):
                return self.CASTLE_QUEEN_SIDE
        return move



    def is_in_check(self, board):
        enemy_units = filter(lambda p: p.color != self.color,
                             board.pieces)
        is_in_check = False
        for unit in enemy_units:
            if isinstance(unit, King):
                continue

            if self.position in unit.available_steps(board):
                is_in_check = True
                break

        return is_in_check

    def is_check_mate(self, board):
        is_in_check = self.is_in_check(board)
        if not is_in_check:
            return False

        friendly_units = [unit for unit in board.pieces
                          if unit.color == self.color and unit.symbol != self.symbol]

        # check king first, highest likelihood of negating checkmate ability
        friendly_units.insert(0, self)

        # check if any available move leads to a state where king is no longer in check
        for unit in friendly_units:
            for available_step in unit.available_steps(board):
                hypothetical_board = deepcopy(board)
                try:
                    hypothetical_board.step(unit.get_step(available_step), self.color)
                except ValueError:
                    continue
                king = hypothetical_board.get_king(self.color)
                if not king.is_in_check(hypothetical_board):
                    return False

        return True

    def special_steps(self, board, require_enemy_presence=True, translate=False):
        # castle
        castling_moves = []
        if self.has_moved or self.is_in_check(board):
            return castling_moves

        rank = 1 if self.color == self.WHITE else 8
        left_rook = board['{}{}'.format('a', str(rank))]
        right_rook = board['{}{}'.format('h', str(rank))]
        move_pairs = (
            (left_rook, (-1, 0)),
            (right_rook, (1, 0))
        )
        for rook_position, step in move_pairs:
            if rook_position.piece is None:
                continue

            rook = rook_position.piece
            if rook.has_moved:
                continue
            position_next_to_king = self.position.step(step)
            if position_next_to_king in rook.available_steps(board):
                castling_symbol = self.CASTLE_KING_SIDE if step[0] == 1 else self.CASTLE_QUEEN_SIDE
                castling_moves.append(castling_symbol)

        if translate:
            castling_moves = [self.translate_move(move, True)
                              for move in castling_moves]
        return castling_moves

    def filter(self, available_steps, board, dont_filter=False):
        """
        disallow moves that would put King in check
        """
        if dont_filter is True:
            return available_steps

        enemy_units = filter(lambda p: p.color != self.color,
                             board.pieces)
        for unit in enemy_units:
            if isinstance(unit, Pawn):
                attack_squares = unit.special_steps(board, require_enemy_presence=False)
                for attack in attack_squares:
                    if attack in available_steps:
                        available_steps.remove(attack)

                continue

            steps = unit.available_steps(board, dont_filter=isinstance(unit, King))
            for step in steps:
                if step in available_steps:
                    available_steps.remove(step)

        return available_steps


class Queen(Piece):
    relative_value = 9
    STEPS = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
             (0, -1), (1, -1), (1, 0), (1, 1),]
    can_travel = True
    symbol = 'Q'


class PieceFactory(object):
    PIECES = (
        Pawn, Rook, Knight, Bishop, Queen, King
    )

    @classmethod
    def create(cls, symbol, position, color, has_moved):
        piece_class = next((kls for kls in cls.PIECES
                            if kls.symbol == symbol))
        file_, rank = position
        piece = piece_class(Square(file_, rank), color=color, has_moved=has_moved)
        return piece


class CommandParser(object):


    @classmethod
    def __call__(self, command):
        is_attack_move = 'x' in command
        special_file = None
        special_rank = None
        castle = None
        if command in King.CASTLING_MOVES:
            symbol = King.symbol
            square = None
            castle = command
        elif len(command) == 2:
            symbol = Pawn.symbol
            square = Square(command[0], int(command[1]))

        elif len(command) == 3:
            symbol = command[0]
            square = Square(command[1], int(command[2]))

        elif len(command) == 4:
            symbol = command[0]
            if not is_attack_move:
                special_file = command[1]
            square = Square(command[2], int(command[3]))
        elif len(command) == 5:
            symbol = command[0]
            if not is_attack_move:
                special_file = command[1]
                special_rank = int(command[2])
            else:
                special_file = command[1]
            square = Square(command[3], int(command[4]))
        elif is_attack_move and len(command) == 6:
            symbol = command[0]
            special_file = command[1]
            special_rank = int(command[2])
            square = Square(command[4], int(command[5]))
        else:
            raise ValueError('Wrong command')

        return symbol, square, is_attack_move, special_file, special_rank, castle
