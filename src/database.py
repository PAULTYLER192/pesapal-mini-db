import os
import json
from typing import Any, Dict, List, Optional

from table import Table
from parser import parse_sql


class Database:
    """Database manager for JSONL tables and JSON metadata schemas.
    
    Manages multiple tables with optional primary key support.
    Automatically loads existing tables from metadata/ on startup.
    Maintains in-memory cache of Table objects for efficient access.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.meta_dir = os.path.join(self.base_dir, "metadata")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)
        
        # In-memory table cache: table_name -> Table object
        self._tables: Dict[str, Table] = {}
        
        # Auto-load existing tables from metadata folder
        self._load_existing_tables()

    def _load_existing_tables(self) -> None:
        """Scan metadata/ folder and auto-load existing tables into cache."""
        if not os.path.exists(self.meta_dir):
            return
        
        for filename in os.listdir(self.meta_dir):
            if filename.endswith(".json"):
                table_name = os.path.splitext(filename)[0]
                try:
                    schema_path = os.path.join(self.meta_dir, filename)
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)
                    
                    # Determine primary key from schema if present
                    primary_key = schema.get("primary_key")
                    
                    # Load table with primary key support
                    table = Table(table_name, schema, self.data_dir, primary_key=primary_key)
                    self._tables[table_name] = table
                except Exception as e:
                    # Log but don't fail on individual table load issues
                    print(f"Warning: Failed to load table '{table_name}': {e}")

    def list_tables(self) -> List[str]:
        names: List[str] = []
        if not os.path.exists(self.meta_dir):
            return names
        for fn in os.listdir(self.meta_dir):
            if fn.endswith(".json"):
                names.append(os.path.splitext(fn)[0])
        return sorted(names)

    def get_table(self, name: str) -> Table:
        """Get a table object by name. Returns cached instance if available.
        
        Args:
            name: The name of the table to retrieve.
            
        Returns:
            A Table object for the specified table.
            
        Raises:
            FileNotFoundError: If the table schema does not exist.
        """
        # Return cached instance if available
        if name in self._tables:
            return self._tables[name]
        
        # Otherwise load from metadata and cache it
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Table '{name}' does not exist")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Determine primary key from schema if present
        primary_key = schema.get("primary_key")
        
        # Create and cache table instance
        table = Table(name, schema, self.data_dir, primary_key=primary_key)
        self._tables[name] = table
        return table

    def create_table(self, name: str, columns: List[Dict[str, str]], primary_key: Optional[str] = None) -> Dict[str, Any]:
        """Create a new table with optional primary key support.
        
        Args:
            name: The name of the table to create.
            columns: List of column definitions with 'name' and 'type'.
            primary_key: Optional column name to use as primary key.
            
        Returns:
            The created schema dictionary.
            
        Raises:
            FileExistsError: If table already exists.
        """
        schema = {"name": name, "columns": columns}
        
        # Add primary key to schema if specified
        if primary_key:
            schema["primary_key"] = primary_key
        
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        if os.path.exists(schema_path):
            raise FileExistsError(f"Table '{name}' already exists")
        
        # Save schema to metadata file
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        
        # Create table instance and cache it
        table = Table(name, schema, self.data_dir, primary_key=primary_key)
        self._tables[name] = table
        
        return schema

    def drop_table(self, name: str) -> None:
        """Drop a table and remove it from cache.
        
        Args:
            name: The name of the table to drop.
        """
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        data_path = os.path.join(self.data_dir, f"{name}.jsonl")
        if os.path.exists(schema_path):
            os.remove(schema_path)
        if os.path.exists(data_path):
            os.remove(data_path)
        # Remove from cache
        if name in self._tables:
            del self._tables[name]

    def describe(self, name: str) -> Dict[str, Any]:
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Table '{name}' does not exist")
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def execute(self, sql: str) -> Any:
        ast = parse_sql(sql)
        stype = ast.get("type")
        if stype == "create_table":
            return self.create_table(ast["name"], ast["columns"])
        elif stype == "drop_table":
            self.drop_table(ast["name"]) 
            return {"ok": True}
        elif stype == "show_tables":
            return self.list_tables()
        elif stype == "describe":
            return self.describe(ast["name"])
        elif stype == "insert":
            table = self.get_table(ast["name"])
            return table.insert(ast["values"])
        elif stype == "select":
            table = self.get_table(ast["name"])
            return table.select(where=ast.get("where"), columns=ast.get("columns"), limit=ast.get("limit"))
        elif stype == "update":
            table = self.get_table(ast["name"])
            n = table.update(set_values=ast["set"], where=ast.get("where"))
            return {"updated": n}
        elif stype == "delete":
            table = self.get_table(ast["name"])
            n = table.delete(where=ast.get("where"))
            return {"deleted": n}
        else:
            raise ValueError(f"Unsupported SQL statement type: {stype}")
