"""
Pesapal Mini Database - A simple in-memory database with SQL-like query support.
"""

from src.db import Database
from src.table import Table
from src.parser import QueryParser
from src import utils

__version__ = '1.0.0'
__all__ = ['Database', 'Table', 'QueryParser', 'utils']
