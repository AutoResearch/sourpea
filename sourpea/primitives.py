from __future__ import annotations
from typing import Callable, List
from scipy.stats import chisquare


class Level:
    """
    A discrete value that a :class:`.Factor` can hold.
    """
    name: str
    weight: float = 1

    def __init__(self, name: str, weight: float = 1):
        self.name = name
        self.weight = weight


class DerivedLevel(Level):
    window: DerivationWindow

    def __init__(self, name: str, window: DerivationWindow, weight: float = 1):
        super().__init__(name, weight)
        self.window = window


class Factor:
    """"An independent variable in a factorial experiment. Factors are composed
    of :class:`Levels <.Level>` and come in two flavors:
    """
    name: str
    levels: List[Level]

    def __init__(self, name: str, initial_levels: list):
        self.name = name
        self.levels = []
        for level in initial_levels:
            if type(level) == str:
                self.levels.append(Level(level))
            elif isinstance(level, Level):
                self.levels.append(level)


class DerivationWindow:
    predicate: Callable
    factors: List[Factor]
    width: int

    def __init__(self, predicate: Callable, factors: List[Factor], width: int = 1):
        self.predicate = predicate
        self.factors = factors
        self.width = width


class WithinTrialDerivationWindow(DerivationWindow):

    def __init__(self, predicate: Callable, factors: List[Factor]):
        super().__init__(predicate, factors)
        self.width = 1


class TransitionDerivationWindow(DerivationWindow):

    def __init__(self, predicate: Callable, factors: List[Factor]):
        super().__init__(predicate, factors)
        self.width = 2


class Block:
    design: List[Factor]
    crossing: List[Factor]
    _counter_balanced_levels: List[Level]
    _counter_balanced_names_weights: List

    def __init__(self, design: List[Factor] = None, crossing: List[Factor] = None):
        self.design = design
        self.crossing = crossing
        if not crossing:
            return
        levels = [[lvl] for lvl in self.crossing[0].levels]
        i = 1
        while i < len(self.crossing):
            list_2 = self.crossing[i].levels
            tmp = [x + [y] for x in levels for y in list_2]
            levels = tmp
            i += 1
        self._counter_balanced_levels = levels
        self._counter_balanced_names_weights = []
        for level in levels:
            name = [lvl.name for lvl in level]
            weight = 1
            for lvl in level:
                weight *= lvl.weight
            res = {'name': name, 'weight': weight}
            self._counter_balanced_names_weights.append(res)

    def test(self, sequence: List):
        chi_2 = self._test_crossing(sequence)
        derived_test = self._test_levels(sequence)
        return {'pValue': chi_2.pvalue, 'levels': derived_test}

    def _test_crossing(self, sequence: List):
        if not self.crossing:
            return chisquare([1, 1], [1, 1])
        weights_empirical = [0 for _ in self._counter_balanced_names_weights]
        for t in sequence:
            level = []
            for factor in self.crossing:
                level.append(t[factor.name])
            i = 0
            for lvl in self._counter_balanced_names_weights:
                if level == lvl['name']:
                    weights_empirical[i] += 1
                else:
                    i += 1
        weights_expected = [lvl['weight'] for lvl in self._counter_balanced_names_weights]

        # normalize weights
        # adjusting for the first trials if there is a transition window in crossing
        max_width = 0
        for factor in self.crossing:
            for lvl in factor.levels:
                if isinstance(lvl, DerivedLevel):
                    if lvl.window.width > 1:
                        max_width = max(lvl.window.width-1, max_width)

        total_expected = sum(weights_expected) + max_width
        weights_expected = [w / total_expected * len(sequence) for w in weights_expected]

        return chisquare(weights_empirical, weights_expected)

    def _test_levels(self, sequence: List):
        test = {}
        for factor in self.design:
            test[factor.name] = True
            is_derived = False
            for lvl in factor.levels:
                if isinstance(lvl, DerivedLevel):
                    is_derived = True
            if is_derived:
                for i in range(len(sequence)):
                    trial = sequence[i]
                    for lvl in factor.levels:
                        if isinstance(lvl, DerivedLevel):
                            window = lvl.window
                            if window.width == 1:
                                args = [trial[factor_w.name] for factor_w in window.factors]
                                lvl_t = trial[factor.name]
                                if window.predicate(*args):
                                    test[factor.name] = (lvl_t == lvl.name) and test[factor.name]
                            elif i >= (window.width - 1):
                                s = i - (window.width - 1)
                                e = i + 1
                                sequence_ = sequence[s:e]
                                args = [[trial[factor_w.name] for trial in sequence_] for factor_w in window.factors]
                                lvl_t = sequence_[-1][factor.name]
                                if window.predicate(*args):
                                    test[factor.name] = (lvl_t == lvl.name) and test[factor.name]
        return test
