"""
Database class for the mini database.
"""
from src.table import Table
from src.utils import validate_table_name


class Database:
    """
    Represents an in-memory database.
    """
    
    def __init__(self, name="minidb"):
        """
        Initialize a database.
        
        Args:
            name (str): Database name
        """
        self.name = name
        self.tables = {}
    
    def create_table(self, table_name, columns):
        """
        Create a new table.
        
        Args:
            table_name (str): Name of the table
            columns (list): List of column names
            
        Returns:
            Table: The created table
        """
        if not validate_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        if table_name in self.tables:
            raise ValueError(f"Table already exists: {table_name}")
        
        if not columns or len(columns) == 0:
            raise ValueError("Table must have at least one column")
        
        table = Table(table_name, columns)
        self.tables[table_name] = table
        return table
    
    def drop_table(self, table_name):
        """
        Drop a table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            bool: True if successful
        """
        if table_name not in self.tables:
            raise ValueError(f"Table does not exist: {table_name}")
        
        del self.tables[table_name]
        return True
    
    def get_table(self, table_name):
        """
        Get a table by name.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Table: The table
        """
        if table_name not in self.tables:
            raise ValueError(f"Table does not exist: {table_name}")
        
        return self.tables[table_name]
    
    def list_tables(self):
        """
        List all table names.
        
        Returns:
            list: List of table names
        """
        return list(self.tables.keys())
    
    def insert(self, table_name, values):
        """
        Insert a row into a table.
        
        Args:
            table_name (str): Name of the table
            values (dict): Dictionary mapping column names to values
            
        Returns:
            bool: True if successful
        """
        table = self.get_table(table_name)
        return table.insert(values)
    
    def select(self, table_name, columns=None, where=None):
        """
        Select rows from a table.
        
        Args:
            table_name (str): Name of the table
            columns (list): List of column names to return (None for all)
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            list: List of matching rows
        """
        table = self.get_table(table_name)
        return table.select(columns, where)
    
    def update(self, table_name, values, where=None):
        """
        Update rows in a table.
        
        Args:
            table_name (str): Name of the table
            values (dict): Dictionary mapping column names to new values
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            int: Number of rows updated
        """
        table = self.get_table(table_name)
        return table.update(values, where)
    
    def delete(self, table_name, where=None):
        """
        Delete rows from a table.
        
        Args:
            table_name (str): Name of the table
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            int: Number of rows deleted
        """
        table = self.get_table(table_name)
        return table.delete(where)
