"""Table CRUD Engine for Mini Database.

Handles table operations including:
- Creating and dropping tables
- Inserting, selecting, updating, and deleting records
- Schema validation
- Data persistence to .jsonl files
"""

import json
import os
from typing import Dict, List, Any, Optional


class Table:
    """Represents a database table with CRUD operations."""
    
    def __init__(self, name: str, schema: Dict[str, str], 
                 data_dir: str, metadata_dir: str):
        """Initialize a table.
        
        Args:
            name: Table name
            schema: Dictionary mapping column names to types
            data_dir: Directory for .jsonl data files
            metadata_dir: Directory for schema JSON files
        """
        self.name = name
        self.schema = schema
        self.data_dir = data_dir
        self.metadata_dir = metadata_dir
        
        self.data_file = os.path.join(data_dir, f"{name}.jsonl")
        self.metadata_file = os.path.join(metadata_dir, f"{name}.json")
    
    @classmethod
    def create(cls, name: str, schema: Dict[str, str],
               data_dir: str, metadata_dir: str) -> 'Table':
        """Create a new table.
        
        Args:
            name: Table name
            schema: Dictionary mapping column names to types
            data_dir: Directory for .jsonl data files
            metadata_dir: Directory for schema JSON files
            
        Returns:
            New Table instance
        """
        table = cls(name, schema, data_dir, metadata_dir)
        table._save_metadata()
        
        # Create empty data file
        with open(table.data_file, 'w') as f:
            pass
        
        return table
    
    @classmethod
    def load(cls, name: str, data_dir: str, metadata_dir: str) -> 'Table':
        """Load an existing table.
        
        Args:
            name: Table name
            data_dir: Directory for .jsonl data files
            metadata_dir: Directory for schema JSON files
            
        Returns:
            Loaded Table instance
            
        Raises:
            FileNotFoundError: If table doesn't exist
        """
        metadata_file = os.path.join(metadata_dir, f"{name}.json")
        
        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"Table '{name}' does not exist")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        return cls(name, metadata['schema'], data_dir, metadata_dir)
    
    def drop(self):
        """Drop the table (delete data and metadata files)."""
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        if os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)
    
    def insert(self, values: List[Any]) -> Dict[str, Any]:
        """Insert a new row into the table.
        
        Args:
            values: List of values matching schema columns in order
            
        Returns:
            The inserted row as a dictionary
            
        Raises:
            ValueError: If values don't match schema
        """
        if len(values) != len(self.schema):
            raise ValueError(
                f"Expected {len(self.schema)} values, got {len(values)}"
            )
        
        # Create row dictionary
        row = {}
        for (col_name, col_type), value in zip(self.schema.items(), values):
            # Validate and convert type
            validated_value = self._validate_type(value, col_type)
            row[col_name] = validated_value
        
        # Append to data file
        with open(self.data_file, 'a') as f:
            f.write(json.dumps(row) + '\n')
        
        return row
    
    def select(self, columns: List[str] = None, 
               where: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select rows from the table.
        
        Args:
            columns: List of column names to select, or ['*'] for all
            where: WHERE clause dictionary with column, operator, value
            
        Returns:
            List of matching rows as dictionaries
        """
        if columns is None or columns == ['*']:
            columns = list(self.schema.keys())
        
        # Validate columns exist
        for col in columns:
            if col not in self.schema:
                raise ValueError(f"Column '{col}' does not exist in table")
        
        results = []
        
        # Read all rows from data file
        if not os.path.exists(self.data_file):
            return results
        
        with open(self.data_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                row = json.loads(line)
                
                # Apply WHERE clause if specified
                if where and not self._evaluate_where(row, where):
                    continue
                
                # Select only requested columns
                selected_row = {col: row.get(col) for col in columns}
                results.append(selected_row)
        
        return results
    
    def update(self, updates: Dict[str, Any], 
               where: Dict[str, Any] = None) -> int:
        """Update rows in the table.
        
        Args:
            updates: Dictionary of column names to new values
            where: WHERE clause dictionary with column, operator, value
            
        Returns:
            Number of rows updated
        """
        # Validate update columns
        for col_name, value in updates.items():
            if col_name not in self.schema:
                raise ValueError(f"Column '{col_name}' does not exist")
            # Validate type
            col_type = self.schema[col_name]
            updates[col_name] = self._validate_type(value, col_type)
        
        # Read all rows
        rows = []
        updated_count = 0
        
        if not os.path.exists(self.data_file):
            return 0
        
        with open(self.data_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                row = json.loads(line)
                
                # Check if row matches WHERE clause
                if where is None or self._evaluate_where(row, where):
                    # Update the row
                    row.update(updates)
                    updated_count += 1
                
                rows.append(row)
        
        # Write all rows back
        with open(self.data_file, 'w') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        
        return updated_count
    
    def delete(self, where: Dict[str, Any] = None) -> int:
        """Delete rows from the table.
        
        Args:
            where: WHERE clause dictionary with column, operator, value
            
        Returns:
            Number of rows deleted
        """
        if not os.path.exists(self.data_file):
            return 0
        
        # Read all rows
        rows = []
        deleted_count = 0
        
        with open(self.data_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                row = json.loads(line)
                
                # Check if row should be deleted
                if where is None or self._evaluate_where(row, where):
                    deleted_count += 1
                else:
                    rows.append(row)
        
        # Write remaining rows back
        with open(self.data_file, 'w') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        
        return deleted_count
    
    def _save_metadata(self):
        """Save table metadata (schema) to JSON file."""
        metadata = {
            'name': self.name,
            'schema': self.schema
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _validate_type(self, value: Any, expected_type: str) -> Any:
        """Validate and convert value to expected type.
        
        Args:
            value: Value to validate
            expected_type: Expected type (TEXT, INTEGER, FLOAT, BOOLEAN)
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If value cannot be converted to expected type
        """
        if value is None:
            return None
        
        try:
            if expected_type == 'TEXT':
                return str(value)
            elif expected_type == 'INTEGER':
                return int(value)
            elif expected_type == 'FLOAT':
                return float(value)
            elif expected_type == 'BOOLEAN':
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    if value.upper() == 'TRUE':
                        return True
                    elif value.upper() == 'FALSE':
                        return False
                raise ValueError(f"Cannot convert '{value}' to BOOLEAN")
            else:
                raise ValueError(f"Unsupported type: {expected_type}")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert '{value}' to {expected_type}: {e}"
            )
    
    def _evaluate_where(self, row: Dict[str, Any], 
                       where: Dict[str, Any]) -> bool:
        """Evaluate WHERE clause against a row.
        
        Args:
            row: Row dictionary
            where: WHERE clause with column, operator, value
            
        Returns:
            True if row matches condition
        """
        column = where['column']
        operator = where['operator']
        value = where['value']
        
        if column not in row:
            return False
        
        row_value = row[column]
        
        # Handle NULL comparisons
        if row_value is None or value is None:
            if operator == '=':
                return row_value == value
            elif operator == '!=':
                return row_value != value
            else:
                return False
        
        # Perform comparison
        if operator == '=':
            return row_value == value
        elif operator == '!=':
            return row_value != value
        elif operator == '>':
            return row_value > value
        elif operator == '<':
            return row_value < value
        elif operator == '>=':
            return row_value >= value
        elif operator == '<=':
            return row_value <= value
        else:
            raise ValueError(f"Unsupported operator: {operator}")
