# coding: utf-8

import functools
from itertools import chain
from typing import TypeVar, Generic, Any, Callable

from owlmixin.transformers import DictTransformer, \
    DictsTransformer, \
    JsonTransformer, \
    YamlTransformer, \
    CsvTransformer, \
    TableTransformer

T = TypeVar('T')
U = TypeVar('U')
K = TypeVar('K')


class TList(list, DictsTransformer, JsonTransformer, YamlTransformer, CsvTransformer, TableTransformer, Generic[T]):
    def __add__(self, values):
        # type: (TList[T]) -> TList[T]
        return TList(values + list(self))

    def map(self, func):
        """
        :param func:
        :type func: T -> U
        :rtype: TList[U]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).map(lambda x: x+1)
            [2, 3, 4, 5, 6]
        """
        return TList(map(func, self))

    def emap(self, func):
        """
        :param func:
        :type func: T, int -> U
        :rtype: TList[U]

        Usage:

            >>> TList([10, 20, 30, 40, 50]).emap(lambda x, i: (x+1, i))
            [(11, 0), (21, 1), (31, 2), (41, 3), (51, 4)]
        """
        return TList([func(x, i) for i, x in enumerate(self)])

    def flatten(self):
        """
        :rtype: TList[U]

        Usage:

            >>> TList([[1, 2], [3, 4]]).flatten()
            [1, 2, 3, 4]
        """
        return TList(chain.from_iterable(self))

    def flat_map(self, func):
        """
        :param func:
        :type func: T -> U
        :rtype: TList[U]

        Usage:

            >>> TList([1, 2, 3]).flat_map(lambda x: [x, x+1])
            [1, 2, 2, 3, 3, 4]
        """
        return self.map(func).flatten()

    def filter(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).filter(lambda x: x > 3)
            [4, 5]
        """
        return TList([x for x in self if func(x)])

    def reject(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).reject(lambda x: x > 3)
            [1, 2, 3]
        """
        return TList([x for x in self if not func(x)])

    def head(self, size_: int) -> 'TList[T]':
        """
        :param size_:

        Usage:

            >>> TList([1, 2, 3, 4, 5]).head(3)
            [1, 2, 3]
        """
        return TList(self[:size_])

    def head_while(self, func: Callable[[T], bool] ) -> 'TList[T]':
        """
        :param func:
        :type func: T -> bool

        Usage:

            >>> TList([1, 2, 30, 4, 50]).head_while(lambda x: x < 10)
            [1, 2]
        """
        r = TList()
        for x in self:
            if not func(x):
                return r
            else:
                r.append(x)
        return r

    def tail(self, size_: int) -> 'TList[T]':
        """
        Usage:

            >>> TList([1, 2, 3, 4, 5]).tail(3)
            [3, 4, 5]
        """
        return TList(self[self.size()-size_:])

    def uniq(self) -> 'TList[T]':
        """
        Usage:

            >>> TList([1, 2, 3, 2, 1]).uniq()
            [1, 2, 3]
        """
        rs = TList()
        for e in self:
            if e not in rs:
                rs.append(e)
        return rs

    def uniq_by(self, func: Callable[[T], Any]) -> 'TList[T]':
        """
        Usage:

            >>> TList([1, 2, 3, -2, -1]).uniq_by(lambda x: x**2)
            [1, 2, 3]
        """
        rs = TList()
        for e in self:
            if func(e) not in rs.map(func):
                rs.append(e)
        return rs

    def partial(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: tuple(TList[T], TList[T])

        Usage:

            >>> TList([1, 2, 3, 4, 5]).partial(lambda x: x > 3)
            ([4, 5], [1, 2, 3])
        """
        return self.filter(func), self.reject(func)

    def group_by(self, to_key):
        """
        :param to_key:
        :type to_key: T -> unicode
        :rtype: TDict[TList[T]]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).group_by(lambda x: x % 2).to_json()
            '{"0": [2,4],"1": [1,3,5]}'
        """
        ret = TDict()
        for v in self:
            k = to_key(v)
            ret.setdefault(k, TList())
            ret[k].append(v)
        return ret

    def order_by(self, func, reverse=False):
        """
        :param func:
        :type func: T -> any
        :param reverse: Sort by descend order if True, else by ascend
        :type reverse: bool
        :rtype: TList[T]

        Usage:

            >>> TList([12, 25, 31, 40, 57]).order_by(lambda x: x % 10)
            [40, 31, 12, 25, 57]
            >>> TList([12, 25, 31, 40, 57]).order_by(lambda x: x % 10, reverse=True)
            [57, 25, 12, 31, 40]
        """
        return TList(sorted(self, key=func, reverse=reverse))

    def concat(self, values, first=False):
        """
        :param values:
        :type values: TList[T]
        :param first:
        :type first: bool
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2]).concat(TList([3, 4]))
            [1, 2, 3, 4]
            >>> TList([1, 2]).concat(TList([3, 4]), first=True)
            [3, 4, 1, 2]
        """
        return values + self if first else self + values

    def reduce(self, func, init_value):
        """
        :param func:
        :type func: (U, T) -> U
        :param init_value:
        :type init_value: U
        :rtype: U

        Usage:

            >>> TList([1, 2, 3, 4, 5]).reduce(lambda t, x: t + 2*x, 100)
            130
        """
        return functools.reduce(func, self, init_value)

    def sum(self):
        """
        :rtype: int | float

        Usage:

            >>> TList([1, 2, 3, 4, 5]).sum()
            15
        """
        return sum(self)

    def sum_by(self, func):
        """
        :param func:
        :type func: T -> int | float
        :rtype: int | float

        Usage:

            >>> TList([1, 2, 3, 4, 5]).sum_by(lambda x: x*2)
            30
        """
        return self.map(func).sum()

    def size(self):
        """
        :rtype: int

        Usage:

            >>> TList([1, 2, 3, 4, 5]).size()
            5
        """
        return len(self)

    def join(self, joint):
        """
        :param joint:
        :type joint: unicode
        :rtype: unicode

        Usage:

            >>> TList(['A', 'B', 'C']).join("-")
            'A-B-C'
        """
        return joint.join(self)

    def find(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: T

        Usage:

            >>> TList([1, 2, 3, 4, 5]).find(lambda x: x > 3)
            4
        """
        for x in self:
            if func(x):
                return x

    def all(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: T

        Usage:

            >>> TList([1, 2, 3, 4, 5]).all(lambda x: x > 0)
            True
            >>> TList([1, 2, 3, 4, 5]).all(lambda x: x > 1)
            False
        """
        return all([func(x) for x in self])

    def any(self, func):
        """
        :param func:
        :type func: T -> bool
        :rtype: T

        Usage:

            >>> TList([1, 2, 3, 4, 5]).any(lambda x: x > 4)
            True
            >>> TList([1, 2, 3, 4, 5]).any(lambda x: x > 5)
            False
        """
        return any([func(x) for x in self])

    def intersection(self, values):
        """
        :param values:
        :type values: List[T]
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).intersection([2, 4, 6])
            [2, 4]
        """
        return self.filter(lambda x: x in values)

    def not_intersection(self, values):
        """
        :param values:
        :type values: List[T]
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2, 3, 4, 5]).not_intersection([2, 4, 6])
            [1, 3, 5]
        """
        return self.reject(lambda x: x in values)

    def reverse(self) -> 'TList[T]':
        """
        :rtype: TList[T]

        Usage:

            >>> TList([1, 2, 3]).reverse()
            [3, 2, 1]
        """
        return TList(reversed(self))


class TDict(dict, DictTransformer, JsonTransformer, YamlTransformer, Generic[T]):
    @property
    def _dict(self):
        return dict(self)

    def map(self, func):
        """
        :param func:
        :type func: (K, T) -> U
        :rtype: TList[U]

        Usage:

            >>> sorted(TDict(k1=1, k2=2, k3=3).map(lambda k, v: v*2))
            [2, 4, 6]
        """
        return TList([func(k, v) for k, v in self.items()])

    def map_values(self, func):
        """
        :param func:
        :type func: T -> U
        :rtype: TDict[U]

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).map_values(lambda x: x*2) == {
            ...     "k1": 2,
            ...     "k2": 4,
            ...     "k3": 6
            ... }
            True
        """
        return TDict({k: func(v) for k, v in self.items()})

    def filter(self, func):
        """
        :param func:
        :type func: (K, T) -> bool
        :rtype: TList[T]

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).filter(lambda k, v: v < 2)
            [1]
        """
        return TList([v for k, v in self.items() if func(k, v)])

    def reject(self, func):
        """
        :param func:
        :type func: (K, T) -> bool
        :rtype: TList[T]

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).reject(lambda k, v: v < 3)
            [3]
        """
        return TList([v for k, v in self.items() if not func(k, v)])

    def sum(self):
        """
        :rtype: int | float

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).sum()
            6
        """
        return sum(self.values())

    def sum_by(self, func):
        """
        :param func:
        :type func: (K, T) -> (int | float)
        :rtype: int | float

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).sum_by(lambda k, v: v*2)
            12
        """
        return self.map(func).sum()

    def size(self):
        """
        :rtype: int

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).size()
            3
        """
        return len(self)

    def find(self, func):
        """
        :param func:
        :type func: (K, T) -> bool
        :rtype: T

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).find(lambda k, v: v == 2)
            2
        """
        for k, v in self.items():
            if func(k, v):
                return v

    def to_values(self):
        """
        :rtype: TList[T]

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).to_values().order_by(lambda x: x)
            [1, 2, 3]
        """
        return TList(self.values())

    def all(self, func):
        """
        :param func:
        :type func: (K, T) -> bool
        :rtype: bool

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).all(lambda k, v: v > 0)
            True
            >>> TDict(k1=1, k2=2, k3=3).all(lambda k, v: v > 1)
            False
        """
        return all([func(k, v) for k, v in self.items()])

    def any(self, func):
        """
        :param func:
        :type func: (K, T) -> bool
        :rtype: bool

        Usage:

            >>> TDict(k1=1, k2=2, k3=3).any(lambda k, v: v > 2)
            True
            >>> TDict(k1=1, k2=2, k3=3).any(lambda k, v: v > 3)
            False
        """
        return any([func(k, v) for k, v in self.items()])
