"""SQL Parser for Mini Database.

Parses simple SQL commands like:
- CREATE TABLE table_name (column1 type1, column2 type2, ...)
- INSERT INTO table_name VALUES (val1, val2, ...)
- SELECT * FROM table_name [WHERE condition]
- UPDATE table_name SET column=value [WHERE condition]
- DELETE FROM table_name [WHERE condition]
- DROP TABLE table_name
"""

import re
from typing import Dict, List, Any, Optional


class SQLParser:
    """Parse SQL statements into structured commands."""
    
    def __init__(self):
        self.patterns = {
            'create': re.compile(
                r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)',
                re.IGNORECASE | re.DOTALL
            ),
            'insert': re.compile(
                r'INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.*?)\)',
                re.IGNORECASE | re.DOTALL
            ),
            'select': re.compile(
                r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
                re.IGNORECASE | re.DOTALL
            ),
            'update': re.compile(
                r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?',
                re.IGNORECASE | re.DOTALL
            ),
            'delete': re.compile(
                r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
                re.IGNORECASE | re.DOTALL
            ),
            'drop': re.compile(
                r'DROP\s+TABLE\s+(\w+)',
                re.IGNORECASE
            ),
        }
    
    def parse(self, sql: str) -> Dict[str, Any]:
        """Parse SQL statement and return structured command.
        
        Args:
            sql: SQL statement string
            
        Returns:
            Dictionary with parsed command structure
            
        Raises:
            ValueError: If SQL statement is invalid
        """
        sql = sql.strip()
        
        if not sql:
            raise ValueError("Empty SQL statement")
        
        # Try to match each pattern
        for cmd_type, pattern in self.patterns.items():
            match = pattern.match(sql)
            if match:
                parser_method = getattr(self, f'_parse_{cmd_type}')
                return parser_method(match)
        
        raise ValueError(f"Invalid SQL statement: {sql}")
    
    def _parse_create(self, match) -> Dict[str, Any]:
        """Parse CREATE TABLE statement."""
        table_name = match.group(1)
        columns_str = match.group(2)
        
        # Parse column definitions
        columns = {}
        for col_def in columns_str.split(','):
            col_def = col_def.strip()
            if not col_def:
                continue
            
            parts = col_def.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = parts[0]
            col_type = parts[1].upper()
            
            if col_type not in ['TEXT', 'INTEGER', 'FLOAT', 'BOOLEAN']:
                raise ValueError(f"Unsupported column type: {col_type}")
            
            columns[col_name] = col_type
        
        return {
            'type': 'CREATE',
            'table': table_name,
            'columns': columns
        }
    
    def _parse_insert(self, match) -> Dict[str, Any]:
        """Parse INSERT INTO statement."""
        table_name = match.group(1)
        values_str = match.group(2)
        
        # Parse values
        values = []
        for value in values_str.split(','):
            value = value.strip()
            values.append(self._parse_value(value))
        
        return {
            'type': 'INSERT',
            'table': table_name,
            'values': values
        }
    
    def _parse_select(self, match) -> Dict[str, Any]:
        """Parse SELECT statement."""
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_clause = match.group(3)
        
        # Parse columns
        if columns_str == '*':
            columns = ['*']
        else:
            columns = [col.strip() for col in columns_str.split(',')]
        
        result = {
            'type': 'SELECT',
            'table': table_name,
            'columns': columns
        }
        
        if where_clause:
            result['where'] = self._parse_where(where_clause)
        
        return result
    
    def _parse_update(self, match) -> Dict[str, Any]:
        """Parse UPDATE statement."""
        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        # Parse SET clause
        updates = {}
        for assignment in set_clause.split(','):
            assignment = assignment.strip()
            if '=' not in assignment:
                raise ValueError(f"Invalid SET clause: {assignment}")
            
            col_name, value = assignment.split('=', 1)
            col_name = col_name.strip()
            value = value.strip()
            updates[col_name] = self._parse_value(value)
        
        result = {
            'type': 'UPDATE',
            'table': table_name,
            'updates': updates
        }
        
        if where_clause:
            result['where'] = self._parse_where(where_clause)
        
        return result
    
    def _parse_delete(self, match) -> Dict[str, Any]:
        """Parse DELETE statement."""
        table_name = match.group(1)
        where_clause = match.group(2)
        
        result = {
            'type': 'DELETE',
            'table': table_name
        }
        
        if where_clause:
            result['where'] = self._parse_where(where_clause)
        
        return result
    
    def _parse_drop(self, match) -> Dict[str, Any]:
        """Parse DROP TABLE statement."""
        table_name = match.group(1)
        
        return {
            'type': 'DROP',
            'table': table_name
        }
    
    def _parse_where(self, where_clause: str) -> Dict[str, Any]:
        """Parse WHERE clause (simple conditions only).
        
        Supports: column=value, column>value, column<value, column!=value
        """
        where_clause = where_clause.strip()
        
        # Try to find operator
        for op in ['!=', '>=', '<=', '=', '>', '<']:
            if op in where_clause:
                parts = where_clause.split(op, 1)
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip()
                    return {
                        'column': column,
                        'operator': op,
                        'value': self._parse_value(value)
                    }
        
        raise ValueError(f"Invalid WHERE clause: {where_clause}")
    
    def _parse_value(self, value: str) -> Any:
        """Parse a value from SQL string.
        
        Handles:
        - Strings in quotes ('text' or "text")
        - Numbers (integers and floats)
        - Booleans (TRUE/FALSE)
        - NULL
        """
        value = value.strip()
        
        # NULL
        if value.upper() == 'NULL':
            return None
        
        # Boolean
        if value.upper() == 'TRUE':
            return True
        if value.upper() == 'FALSE':
            return False
        
        # String (quoted)
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return value[1:-1]
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # If not a number, treat as unquoted string
            return value
