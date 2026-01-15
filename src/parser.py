"""
SQL-like query parser for the mini database.
"""
import re
from src.utils import parse_value


class QueryParser:
    """
    Parser for SQL-like queries.
    """
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def parse(self, query):
        """
        Parse a SQL-like query string.
        
        Args:
            query (str): SQL-like query string
            
        Returns:
            dict: Parsed query as dictionary
        """
        query = query.strip()
        
        # Remove trailing semicolon
        if query.endswith(';'):
            query = query[:-1].strip()
        
        # Determine query type
        query_upper = query.upper()
        
        if query_upper.startswith('CREATE TABLE'):
            return self._parse_create_table(query)
        elif query_upper.startswith('DROP TABLE'):
            return self._parse_drop_table(query)
        elif query_upper.startswith('INSERT INTO'):
            return self._parse_insert(query)
        elif query_upper.startswith('SELECT'):
            return self._parse_select(query)
        elif query_upper.startswith('UPDATE'):
            return self._parse_update(query)
        elif query_upper.startswith('DELETE FROM'):
            return self._parse_delete(query)
        else:
            raise ValueError(f"Unknown query type: {query}")
    
    def _parse_create_table(self, query):
        """Parse CREATE TABLE query."""
        # CREATE TABLE table_name (col1, col2, col3)
        match = re.match(r'CREATE\s+TABLE\s+(\w+)\s*\((.*)\)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        columns = [col.strip() for col in columns_str.split(',')]
        
        return {
            'type': 'CREATE_TABLE',
            'table': table_name,
            'columns': columns
        }
    
    def _parse_drop_table(self, query):
        """Parse DROP TABLE query."""
        # DROP TABLE table_name
        match = re.match(r'DROP\s+TABLE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        return {
            'type': 'DROP_TABLE',
            'table': match.group(1)
        }
    
    def _parse_insert(self, query):
        """Parse INSERT INTO query."""
        # INSERT INTO table_name (col1, col2) VALUES (val1, val2)
        match = re.match(
            r'INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)',
            query,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)
        
        columns = [col.strip() for col in columns_str.split(',')]
        values_list = self._parse_values_list(values_str)
        
        if len(columns) != len(values_list):
            raise ValueError("Number of columns and values must match")
        
        values = dict(zip(columns, values_list))
        
        return {
            'type': 'INSERT',
            'table': table_name,
            'values': values
        }
    
    def _parse_select(self, query):
        """Parse SELECT query."""
        # SELECT col1, col2 FROM table_name WHERE col = value
        match = re.match(
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
            query,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_str = match.group(3)
        
        # Parse columns
        if columns_str == '*':
            columns = None
        else:
            columns = [col.strip() for col in columns_str.split(',')]
        
        # Parse WHERE clause
        where = self._parse_where(where_str) if where_str else None
        
        return {
            'type': 'SELECT',
            'table': table_name,
            'columns': columns,
            'where': where
        }
    
    def _parse_update(self, query):
        """Parse UPDATE query."""
        # UPDATE table_name SET col1=val1, col2=val2 WHERE col = value
        match = re.match(
            r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?$',
            query,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_str = match.group(2)
        where_str = match.group(3)
        
        # Parse SET clause
        values = {}
        for assignment in set_str.split(','):
            parts = assignment.split('=')
            if len(parts) != 2:
                raise ValueError(f"Invalid SET clause: {assignment}")
            col = parts[0].strip()
            val = parse_value(parts[1].strip())
            values[col] = val
        
        # Parse WHERE clause
        where = self._parse_where(where_str) if where_str else None
        
        return {
            'type': 'UPDATE',
            'table': table_name,
            'values': values,
            'where': where
        }
    
    def _parse_delete(self, query):
        """Parse DELETE FROM query."""
        # DELETE FROM table_name WHERE col = value
        match = re.match(
            r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
            query,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_str = match.group(2)
        
        # Parse WHERE clause
        where = self._parse_where(where_str) if where_str else None
        
        return {
            'type': 'DELETE',
            'table': table_name,
            'where': where
        }
    
    def _parse_where(self, where_str):
        """Parse WHERE clause."""
        if not where_str:
            return None
        
        # WHERE col operator value (order matters: <= and >= before < and >)
        match = re.match(r'(\w+)\s*(<=|>=|!=|=|<|>)\s*(.+)', where_str.strip())
        if not match:
            raise ValueError(f"Invalid WHERE clause: {where_str}")
        
        return {
            'column': match.group(1),
            'operator': match.group(2),
            'value': parse_value(match.group(3).strip())
        }
    
    def _parse_values_list(self, values_str):
        """Parse comma-separated values list."""
        values = []
        current = ''
        in_quotes = False
        quote_char = None
        
        for char in values_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == ',' and not in_quotes:
                values.append(parse_value(current.strip()))
                current = ''
            else:
                current += char
        
        if current:
            values.append(parse_value(current.strip()))
        
        return values
