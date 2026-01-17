import os
import json
from typing import Any, Dict, List, Optional, Iterable


class DuplicateKeyError(Exception):
    """Raised when attempting to insert a row with a duplicate primary key."""
    pass


_TYPE_MAP = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "double": float,
    "bool": bool,
    "boolean": bool,
}


def _convert_type(value: Any, type_name: str) -> Any:
    if value is None:
        return None
    py_type = _TYPE_MAP.get(type_name.lower())
    if py_type is None:
        # Unknown types default to string
        return str(value)
    if py_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("true", "1", "yes", "y"): return True
            if v in ("false", "0", "no", "n"): return False
            # Fallback: non-empty string -> True
            return bool(v)
        return bool(value)
    try:
        if py_type is str:
            return str(value)
        if py_type is int:
            if isinstance(value, bool):
                return 1 if value else 0
            return int(value)
        if py_type is float:
            return float(value)
    except (ValueError, TypeError):
        # If conversion fails, keep original
        return value
    return value


def _validate_type(value: Any, type_name: str, column_name: str) -> Any:
    """Validate and convert value to the specified type.
    
    Raises:
        TypeError: If value cannot be converted to the expected type.
    """
    if value is None:
        return None
    
    py_type = _TYPE_MAP.get(type_name.lower())
    if py_type is None:
        # Unknown types default to string
        return str(value)
    
    if py_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("true", "1", "yes", "y"): return True
            if v in ("false", "0", "no", "n"): return False
            raise TypeError(f"Column '{column_name}' expects type '{type_name}', cannot convert '{value}' to bool")
        return bool(value)
    
    try:
        if py_type is str:
            return str(value)
        if py_type is int:
            if isinstance(value, bool):
                return 1 if value else 0
            return int(value)
        if py_type is float:
            return float(value)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Column '{column_name}' expects type '{type_name}', cannot convert '{value}': {e}")
    
    return value


class Table:
    """JSONL-backed heap table with a simple schema and optional primary key indexing.

    Data is stored in `data/<name>.jsonl` as one JSON document per line.
    Schema is a dict: {"name": ..., "columns": [{"name": ..., "type": ...}, ...]}.
    Primary keys are enforced using an in-memory index for O(1) lookups.
    """

    def __init__(self, name: str, schema: Dict[str, Any], data_dir: str, primary_key: Optional[str] = None):
        self.name = name
        self.schema = schema
        self.data_path = os.path.join(data_dir, f"{name}.jsonl")
        self.primary_key = primary_key
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # Create file automatically if it doesn't exist
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w", encoding="utf-8") as f:
                pass

        # Build column map for quick type checks
        self.columns = {c["name"]: c.get("type", "str") for c in schema.get("columns", [])}
        
        # Initialize primary key index: maps primary_key_value -> row_dict
        self.index: Dict[Any, Dict[str, Any]] = {}
        
        # Load and build index if primary key is defined
        if self.primary_key:
            self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild the primary key index from the JSONL file."""
        self.index.clear()
        if not self.primary_key:
            return
        
        rows = self._load_rows()
        for row in rows:
            pk_value = row.get(self.primary_key)
            if pk_value is not None:
                self.index[pk_value] = row

    def _load_rows(self) -> List[Dict[str, Any]]:
        """Read line-by-line from data/{name}.jsonl."""
        rows: List[Dict[str, Any]] = []
        if not os.path.exists(self.data_path):
            return rows
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip corrupted lines
                    continue
        return rows

    def _save_row(self, row_dict: Dict[str, Any]) -> None:
        """Append a JSON string to data/{name}.jsonl."""
        with open(self.data_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row_dict, ensure_ascii=False) + "\n")

    def _write_all(self, rows: Iterable[Dict[str, Any]]) -> None:
        """Rewrite entire file with given rows."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def insert(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a row with data validation and primary key uniqueness check.
        
        Raises:
            ValueError: If required columns are missing from input.
            TypeError: If data types cannot be converted to schema types.
            DuplicateKeyError: If primary key value already exists in table.
        """
        # Validate that all required columns are present
        missing_columns = [col for col in self.columns.keys() if col not in values]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate and convert types based on schema
        converted: Dict[str, Any] = {}
        for col, type_name in self.columns.items():
            v = values.get(col)
            converted[col] = _validate_type(v, type_name, col)
        
        # Include any extra columns provided (not in schema)
        for k, v in values.items():
            if k not in converted:
                converted[k] = v
        
        # Check for duplicate primary key
        if self.primary_key:
            pk_value = converted.get(self.primary_key)
            if pk_value in self.index:
                raise DuplicateKeyError(f"Duplicate primary key '{self.primary_key}={pk_value}' already exists")
        
        self._save_row(converted)
        
        # Update index if primary key is defined
        if self.primary_key:
            pk_value = converted.get(self.primary_key)
            self.index[pk_value] = converted
        
        return converted

    def select_by_id(self, pk_value: Any) -> Optional[Dict[str, Any]]:
        """Get a row by primary key in O(1) time using index.
        
        Args:
            pk_value: The primary key value to look up.
            
        Returns:
            The row dictionary if found, None otherwise.
            
        Raises:
            ValueError: If table has no primary key defined.
        """
        if not self.primary_key:
            raise ValueError("Table has no primary key defined")
        
        return self.index.get(pk_value)

    def select(
        self,
        where: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        rows = self._load_rows()
        res: List[Dict[str, Any]] = []
        for row in rows:
            if where:
                match = True
                for k, v in where.items():
                    if row.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            if columns:
                projected = {c: row.get(c) for c in columns}
            else:
                projected = row
            res.append(projected)
            if limit is not None and len(res) >= limit:
                break
        return res

    def update(self, set_values: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> int:
        rows = self._load_rows()
        updated = 0
        for row in rows:
            if where:
                match = True
                for k, v in where.items():
                    if row.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            # Store old primary key value if updating primary key
            old_pk_value = None
            if self.primary_key and self.primary_key in set_values:
                old_pk_value = row.get(self.primary_key)
            
            for k, v in set_values.items():
                type_name = self.columns.get(k, "str")
                row[k] = _convert_type(v, type_name)
            
            # Update index if primary key was modified
            if self.primary_key and old_pk_value is not None:
                new_pk_value = row.get(self.primary_key)
                if old_pk_value in self.index:
                    del self.index[old_pk_value]
                self.index[new_pk_value] = row
            elif self.primary_key:
                pk_value = row.get(self.primary_key)
                self.index[pk_value] = row
            
            updated += 1
        self._write_all(rows)
        return updated

    def delete(self, where: Optional[Dict[str, Any]] = None) -> int:
        rows = self._load_rows()
        kept: List[Dict[str, Any]] = []
        deleted = 0
        for row in rows:
            if where:
                match = True
                for k, v in where.items():
                    if row.get(k) != v:
                        match = False
                        break
                if match:
                    # Remove from index before deleting
                    if self.primary_key:
                        pk_value = row.get(self.primary_key)
                        if pk_value in self.index:
                            del self.index[pk_value]
                    deleted += 1
                    continue
            kept.append(row)
        self._write_all(kept)
        return deleted

    def count(self) -> int:
        return sum(1 for _ in self._load_rows())
