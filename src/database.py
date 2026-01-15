"""Database Manager for Mini Database.

Manages database operations including:
- Table creation and management
- SQL command execution
- Database initialization
"""

import os
from typing import Dict, List, Any
from src.parser import SQLParser
from src.table import Table


class Database:
    """Main database manager that coordinates all operations."""
    
    def __init__(self, data_dir: str = 'data', metadata_dir: str = 'metadata'):
        """Initialize database.
        
        Args:
            data_dir: Directory for .jsonl data files
            metadata_dir: Directory for schema JSON files
        """
        self.data_dir = data_dir
        self.metadata_dir = metadata_dir
        self.parser = SQLParser()
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(metadata_dir, exist_ok=True)
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """Execute a SQL command.
        
        Args:
            sql: SQL statement string
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Parse the SQL command
            parsed = self.parser.parse(sql)
            command_type = parsed['type']
            
            # Execute based on command type
            if command_type == 'CREATE':
                return self._execute_create(parsed)
            elif command_type == 'DROP':
                return self._execute_drop(parsed)
            elif command_type == 'INSERT':
                return self._execute_insert(parsed)
            elif command_type == 'SELECT':
                return self._execute_select(parsed)
            elif command_type == 'UPDATE':
                return self._execute_update(parsed)
            elif command_type == 'DELETE':
                return self._execute_delete(parsed)
            else:
                raise ValueError(f"Unsupported command type: {command_type}")
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_tables(self) -> List[str]:
        """List all tables in the database.
        
        Returns:
            List of table names
        """
        if not os.path.exists(self.metadata_dir):
            return []
        
        tables = []
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith('.json'):
                table_name = filename[:-5]  # Remove .json extension
                tables.append(table_name)
        
        return sorted(tables)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists.
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists
        """
        metadata_file = os.path.join(self.metadata_dir, f"{table_name}.json")
        return os.path.exists(metadata_file)
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get the schema of a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary mapping column names to types
            
        Raises:
            FileNotFoundError: If table doesn't exist
        """
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        return table.schema
    
    def _execute_create(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CREATE TABLE command."""
        table_name = parsed['table']
        columns = parsed['columns']
        
        if self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' already exists"
            }
        
        Table.create(table_name, columns, self.data_dir, self.metadata_dir)
        
        return {
            'success': True,
            'message': f"Table '{table_name}' created successfully",
            'table': table_name
        }
    
    def _execute_drop(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DROP TABLE command."""
        table_name = parsed['table']
        
        if not self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            }
        
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        table.drop()
        
        return {
            'success': True,
            'message': f"Table '{table_name}' dropped successfully",
            'table': table_name
        }
    
    def _execute_insert(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute INSERT INTO command."""
        table_name = parsed['table']
        values = parsed['values']
        
        if not self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            }
        
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        row = table.insert(values)
        
        return {
            'success': True,
            'message': f"Inserted 1 row into '{table_name}'",
            'table': table_name,
            'row': row
        }
    
    def _execute_select(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SELECT command."""
        table_name = parsed['table']
        columns = parsed['columns']
        where = parsed.get('where')
        
        if not self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            }
        
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        rows = table.select(columns, where)
        
        return {
            'success': True,
            'table': table_name,
            'columns': columns,
            'rows': rows,
            'count': len(rows)
        }
    
    def _execute_update(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UPDATE command."""
        table_name = parsed['table']
        updates = parsed['updates']
        where = parsed.get('where')
        
        if not self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            }
        
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        count = table.update(updates, where)
        
        return {
            'success': True,
            'message': f"Updated {count} row(s) in '{table_name}'",
            'table': table_name,
            'count': count
        }
    
    def _execute_delete(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE command."""
        table_name = parsed['table']
        where = parsed.get('where')
        
        if not self.table_exists(table_name):
            return {
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            }
        
        table = Table.load(table_name, self.data_dir, self.metadata_dir)
        count = table.delete(where)
        
        return {
            'success': True,
            'message': f"Deleted {count} row(s) from '{table_name}'",
            'table': table_name,
            'count': count
        }
