from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Final


__title__: Final[str] = 'veribot'
__author__: Final[str] = 'The Master'
__license__: Final[str] = 'MIT'
__copyright__: Final[str] = 'Copyright 2022-present The Master'
__version__: Final[str] = '1.0.4'


from .bot import VeriBot


del TYPE_CHECKING
