from __future__ import annotations

from typing import (
    TypeVar,
    overload,
    Optional,
    Union,
    Any,
    Dict,
    Callable,
)

from collections.abc import Hashable

try:
    from typing import Mapping, Iterable, Iterator, Tuple, Type
except ImportError:
    from collections.abc import Mapping, Iterable, Iterator
    Tuple = tuple
    Type = type

K = TypeVar("K")
V = TypeVar("V", covariant=True)
K2 = TypeVar("K2")
V2 = TypeVar("V2", covariant=True)
SelfT = TypeVar("SelfT", bound=frozendict[K, V])

# noinspection PyPep8Naming
class frozendict(Mapping[K, V]):
    @overload
    def __new__(cls: Type[SelfT]) -> SelfT: ...
    @overload
    def __new__(cls: Type[SelfT], **kwargs: V) -> frozendict[str, V]: ...
    @overload
    def __new__(cls: Type[SelfT], mapping: Mapping[K, V]) -> SelfT: ...
    @overload
    def __new__(cls: Type[SelfT], iterable: Iterable[Tuple[K, V]]) -> SelfT: ...
    
    def __getitem__(self: SelfT, key: K) -> V: ...
    def __len__(self: SelfT) -> int: ...
    def __iter__(self: SelfT) -> Iterator[K]: ...
    def __hash__(self: SelfT) -> int: ...
    def __reversed__(self: SelfT) -> Iterator[K]: ...
    def copy(self: SelfT) -> SelfT: ...
    def __copy__(self: SelfT) -> SelfT: ...
    def __deepcopy__(self: SelfT) -> SelfT: ...
    def delete(self: SelfT, key: K) -> SelfT: ...
    @overload
    def key(self: SelfT, index: int) -> K: ...
    @overload
    def key(self: SelfT) -> K: ...
    @overload
    def value(self: SelfT, index: int) -> V: ...
    @overload
    def value(self: SelfT) -> V: ...
    @overload
    def item(self: SelfT, index: int) -> Tuple[K, V]: ...
    @overload
    def item(self: SelfT) -> Tuple[K, V]: ...
    @overload
    def __or__(self: SelfT, other: Mapping[K, V]) -> SelfT: ...
    @overload
    def __or__(self: SelfT, other: Mapping[K2, V]) -> frozendict[Union[K, K2], V]: ...
    @overload
    def __or__(self: SelfT, other: Mapping[K, V2]) -> frozendict[K, Union[V, V2]]: ...
    @overload
    def __or__(self: SelfT, other: Mapping[K2, V2]) -> frozendict[Union[K, K2], Union[V, V2]]: ...
    @overload
    def set(self: SelfT, key: K, value: V) -> SelfT: ...
    @overload
    def set(self: SelfT, key: K2, value: V) -> frozendict[Union[K, K2], V]: ...
    @overload
    def set(self: SelfT, key: K, value: V2) -> frozendict[K, Union[V, V2]]: ...
    @overload
    def set(self: SelfT, key: K2, value: V2) -> frozendict[Union[K, K2], Union[V, V2]]: ...
    @overload
    def setdefault(self: SelfT, key: K) -> SelfT: ...
    @overload
    def setdefault(self: SelfT, key: K2) -> SelfT: ...
    @overload
    def setdefault(self: SelfT, key: K, default: V) -> SelfT: ...
    @overload
    def setdefault(self: SelfT, key: K2, default: V) -> frozendict[Union[K, K2], V]: ...
    @overload
    def setdefault(self: SelfT, key: K, default: V2) -> frozendict[K, Union[V, V2]]: ...
    @overload
    def setdefault(self: SelfT, key: K2, default: V2) -> frozendict[Union[K, K2], Union[V, V2]]: ...
    
    @classmethod
    def fromkeys(
        cls: Type[SelfT], 
        seq: Iterable[K], 
        value: Optional[V] = None
    ) -> SelfT: ...


FrozenOrderedDict = frozendict
c_ext: bool

class FreezeError(Exception):  pass


class FreezeWarning(UserWarning):  pass

# PyCharm complains about returning Hashable, because
# it's not subscriptable
def deepfreeze(
        o: Any,
        custom_converters: Optional[Dict[Any, Callable[[Any], Hashable]]] = None,
        custom_inverse_converters: Optional[Dict[Any, Callable[[Any], Any]]] = None
) -> Any: ...

def register(
    to_convert: Any,
    converter: Callable[[Any], Any],
    *,
    inverse: bool = False
) -> None: ...

def unregister(
    type: Any,
    inverse: bool = False
) -> None: ...
