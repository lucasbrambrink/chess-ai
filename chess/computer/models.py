import os
from hashlib import sha256
from django.db import models
from django.contrib.postgres.fields import JSONField


class BoardState(models.Model):
    serialized_state = JSONField()
    hash = models.CharField(max_length=255)
    historical_games = models.ManyToManyField(to='HistoricalGame')

    @property
    def as_game(self):
        from game.models import Game
        return Game.initialize_from_dict(self.serialized_state)


class HistoricalGame(models.Model):
    event_name = models.CharField(max_length=255)
    site = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    round_in_series = models.CharField(max_length=255)
    player_white = models.CharField(max_length=255)
    player_black = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    white_elo = models.CharField(max_length=255)
    black_elo = models.CharField(max_length=255)
    eco = models.CharField(max_length=255)
    moves = models.TextField()
    file_name = models.CharField(max_length=255, default='')
    hash = models.CharField(max_length=255, default='')

    ATTR_MAP = {
        'event_name': '[Event ',
        'site': '[Site ',
        'date': '[Date ',
        'round_in_series': '[Round ',
        'player_white': '[White ',
        'player_black': '[Black ',
        'result': '[Result ',
        'white_elo': '[WhiteElo ',
        'black_elo': '[BlackElo ',
        'eco': '[ECO'
    }
    WIN_WHITE = '1-0'
    WIN_BLACK = '0-1'
    DRAW = '1/2-1/2'
    RESULTS = (
        WIN_WHITE, WIN_BLACK, DRAW
    )

    def assign_hash(self):
        self.hash = self.__hash__()
        self.save(update_fields=['hash'])

    def __repr__(self):
        return '{}: {} ({})'.format(self.event_name, self.round_in_series, self.date)

    def __hash__(self):
        hash_string = '{}{}{}{}'.format(
            self.event_name,
            self.site,
            self.date,
            self.moves
        )
        return str(sha256(hash_string.encode()).hexdigest())

    @classmethod
    def parse_file(cls, file_path):
        try:
            with open(file_path, 'r',
                      encoding='utf-8',
                      errors='ignore') as file_text:
                all_lines = file_text.read().splitlines()
        except Exception as exc:
            print(exc)
            print('Unable to parse file %s' % file_path)
            return

        lines = (l for l in all_lines)
        event = None
        moves = []
        events = []
        for line in lines:
            if cls.ATTR_MAP['event_name'] in line:
                if event is not None:
                    event.moves = ''.join(moves)
                    event.hash = event.__hash__()
                    events.append(event)
                    moves = []

                event = HistoricalGame()
                event.file_name = file_path

            found_prop = False
            for key, value in cls.ATTR_MAP.items():
                if value in line:
                    found_prop = True
                    setattr(event, key, line.replace(value, '').replace(']', '').replace('"', ''))
                    break

            if found_prop:
                continue

            moves.append(line)

            if len(events) == 1000:
                print('Committing games....')
                HistoricalGame.objects.bulk_create(events)
                events = []

        print('Committing rest....')
        HistoricalGame.objects.bulk_create(events)

    @classmethod
    def parse_directory(cls, directory_path, start_at=None):
        found = False
        for file_ in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_)
            if start_at is not None and not found:
                found = start_at in file_path
                continue
            print('Parsing %s' % file_path)
            cls.parse_file(file_path)


    @classmethod
    def parse_moves_into_board(cls, moves):
        all_moves = []
        moves_string = moves
        move_num = 1
        while True:
            move_index = '%s.' % move_num
            move_index_next = '%s.' % (move_num + 1)
            index = moves_string.index(move_index)
            last_iteration = move_index_next not in moves_string
            if last_iteration:
                slice = moves_string[index:]
            else:
                next_index = moves_string.index(move_index_next)
                slice = moves_string[index:next_index]

            # 'e1 e4 ' => ['e1', 'e4', '']
            if not len(slice):
                break
            white_move = slice.split()[0].replace(move_index, '')
            black_move = slice.split()[1]  # can be ''

            if black_move in cls.RESULTS:
                last_iteration = True

            all_moves.append((white_move, 'w'))
            if black_move != '' and black_move not in cls.RESULTS:
                all_moves.append((black_move, 'b'))

            if last_iteration:
                break
            else:
                move_num += 1

        return all_moves

    def create_board_states(self):
        clean_moves = self.parse_moves_into_board(self.moves)
        from game.models import Game
        game = Game()
        try:
            for step in clean_moves:
                game.board.step(*step)
                obj, _ = BoardState.objects.get_or_create(
                    serialized_state=game.serialized,
                    hash=game.board.__hash__()
                )
                obj.historical_games.add(self)
                obj.save()
        except ValueError:
            print('Problem with game %s' % str(self))
        except TypeError as exc:
            print('Problem with game %s' % str(self))
            print(exc)

