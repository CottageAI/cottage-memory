# src/cottage_memory/__init__.py
from .memory.chat_memory import ChatMemory
from .memory.core_memory import CoreMemory
from .memory.contextual_memory import ContextualMemory, Memory
from .memory.conversations_memory import ConversationsMemory
from importlib.metadata import version, PackageNotFoundError

__all__ = [
    "ChatMemory", 
    "CoreMemory", 
    "ContextualMemory",
    "Memory",
    "ConversationsMemory"
]

try:
    __version__ = version("cottage-memory")
except PackageNotFoundError:
    __version__ = "0.0.0"
    
    