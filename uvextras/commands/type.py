
from typing import Callable
from uvextras.context import AppContext

# the expected signature of cmd functions
type CommandType = Callable[[AppContext], None]
