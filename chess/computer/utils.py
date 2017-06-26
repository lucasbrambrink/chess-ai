from .heuristics.tactics import Tactics


class RuleSuite(object):


    def __init__(self, heuristics):
        self.heuristics = heuristics


class AlphaBlue(object):

    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.rule_suites = None


class AlphaBlueFactory(object):

    @classmethod
    def create(cls, rule_suites):
        rule_instances = []
        for rule in rule_suites:
            if rule == Tactics.__class__.__name__:
                rule_instances.append(Tactics)
            elif rule == Tactics.__class__.__name__:
                pass
            elif rule == Tactics.__class__.__name__:
                pass

