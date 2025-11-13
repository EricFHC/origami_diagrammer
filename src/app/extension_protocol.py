from typing import Protocol, runtime_checkable, Callable
from dataclasses import dataclass
from pathlib import Path
from .process_protocol import CommandProtocol

@dataclass(unsafe_hash=True)
class CommandGroup:

    image: str
    tooltip: str

@dataclass
class CommandButton:

    image: str
    tooltip: str
    command: CommandProtocol

@runtime_checkable
class ExtensionProtocol(Protocol):

    name: str

    assets: list[tuple[Path, str]]

    commands: dict[CommandGroup, list[CommandButton]]
