"""
Table class for the mini database.
"""
from src.utils import validate_column_name, compare_values


class Table:
    """
    Represents a table in the database.
    """
    
    def __init__(self, name, columns):
        """
        Initialize a table.
        
        Args:
            name (str): Table name
            columns (list): List of column names
        """
        self.name = name
        self.columns = columns
        self.rows = []
        
        # Validate columns
        for col in columns:
            if not validate_column_name(col):
                raise ValueError(f"Invalid column name: {col}")
    
    def insert(self, values):
        """
        Insert a row into the table.
        
        Args:
            values (dict): Dictionary mapping column names to values
            
        Returns:
            bool: True if successful
        """
        # Validate all required columns are present
        if set(values.keys()) != set(self.columns):
            missing = set(self.columns) - set(values.keys())
            extra = set(values.keys()) - set(self.columns)
            if missing:
                raise ValueError(f"Missing columns: {missing}")
            if extra:
                raise ValueError(f"Unknown columns: {extra}")
        
        # Create row in the correct column order
        row = {col: values[col] for col in self.columns}
        self.rows.append(row)
        return True
    
    def select(self, columns=None, where=None):
        """
        Select rows from the table.
        
        Args:
            columns (list): List of column names to return (None for all)
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            list: List of matching rows
        """
        # Default to all columns
        if columns is None:
            columns = self.columns
        
        # Validate columns
        for col in columns:
            if col not in self.columns:
                raise ValueError(f"Unknown column: {col}")
        
        # Filter rows
        result = []
        for row in self.rows:
            # Apply where clause
            if where:
                col = where['column']
                if col not in self.columns:
                    raise ValueError(f"Unknown column in WHERE clause: {col}")
                
                if not compare_values(row[col], where['operator'], where['value']):
                    continue
            
            # Project columns
            result_row = {col: row[col] for col in columns}
            result.append(result_row)
        
        return result
    
    def update(self, values, where=None):
        """
        Update rows in the table.
        
        Args:
            values (dict): Dictionary mapping column names to new values
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            int: Number of rows updated
        """
        # Validate columns in values
        for col in values.keys():
            if col not in self.columns:
                raise ValueError(f"Unknown column: {col}")
        
        # Validate where clause
        if where and where['column'] not in self.columns:
            raise ValueError(f"Unknown column in WHERE clause: {where['column']}")
        
        count = 0
        for row in self.rows:
            # Apply where clause
            if where:
                col = where['column']
                if not compare_values(row[col], where['operator'], where['value']):
                    continue
            
            # Update row
            for col, val in values.items():
                row[col] = val
            count += 1
        
        return count
    
    def delete(self, where=None):
        """
        Delete rows from the table.
        
        Args:
            where (dict): Where clause as dict with keys 'column', 'operator', 'value'
            
        Returns:
            int: Number of rows deleted
        """
        # Validate where clause
        if where and where['column'] not in self.columns:
            raise ValueError(f"Unknown column in WHERE clause: {where['column']}")
        
        if where is None:
            count = len(self.rows)
            self.rows = []
            return count
        
        # Filter rows to keep
        new_rows = []
        count = 0
        for row in self.rows:
            col = where['column']
            if compare_values(row[col], where['operator'], where['value']):
                count += 1
            else:
                new_rows.append(row)
        
        self.rows = new_rows
        return count
    
    def count(self):
        """
        Get the number of rows in the table.
        
        Returns:
            int: Number of rows
        """
        return len(self.rows)
