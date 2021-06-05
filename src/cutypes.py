from typing import TypeVar, Union

from DataClasses import Error

_T = TypeVar('_T')
MayError = Union[Error, _T]
