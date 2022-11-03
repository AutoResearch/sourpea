from __future__ import annotations
from scipy.stats import chisquare


class Level:
    """
    A discrete value that a :class:`.Factor` can hold.
    """
    name: str
    weight: float = 1

    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight


class DerivedLevel(Level):
    name: str
    weight: float = 1
    window: Window

    def __init__(self, name, window, weight=1):
        self.name = name
        self.window = window
        self.weight = weight


class Factor:
    """"An independent variable in a factorial experiment. Factors are composed
    of :class:`Levels <.Level>` and come in two flavors:
    """
    name: str
    levels: list(Level)

    def __init__(self, name=str, initial_levels=list):
        self.name = name
        self.levels = []
        for level in initial_levels:
            if type(level) == str:
                self.levels.append(Level(level))
            elif type(level) == Level:
                self.levels.append(level)


class Window:
    function: function
    factors: list(Factor)


class Design:
    factors: list(Factor)
    _counter_balanced_levels: list(Level)
    _counter_balanced_names_weights: list

    def __init__(self, factors):
        self.factors = factors
        levels = [[l] for l in self.factors[0].levels]
        i = 1
        while i < len(self.factors):
            list_2 = self.factors[i].levels
            tmp = [x + [y] for x in levels for y in list_2]
            levels = tmp
            i += 1
        self._counter_balanced_levels = levels
        self._counter_balanced_names_weights = []
        for level in levels:
            name = [l.name for l in level]
            weight = 1
            for l in level:
                weight *= l.weight
            res = {'name': name, 'weight': weight}
            self._counter_balanced_names_weights.append(res)

    def test(self, sequence):
        weights_empirical = [0 for _ in self._counter_balanced_names_weights]
        for t in sequence:
            level = []
            for factor in self.factors:
                level.append(t[factor.name])
            i = 0
            for lvl in self._counter_balanced_names_weights:
                if level == lvl['name']:
                    weights_empirical[i] += 1
                else:
                    i += 1
        weights_expected = [lvl['weight'] for lvl in self._counter_balanced_names_weights]
        return chisquare(weights_empirical, weights_expected)


