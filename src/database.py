import os
import json
from typing import Any, Dict, List, Optional

from table import Table
from parser import parse_sql


class Database:
    """Database manager for JSONL tables and JSON metadata schemas."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.meta_dir = os.path.join(self.base_dir, "metadata")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)

    def list_tables(self) -> List[str]:
        names: List[str] = []
        if not os.path.exists(self.meta_dir):
            return names
        for fn in os.listdir(self.meta_dir):
            if fn.endswith(".json"):
                names.append(os.path.splitext(fn)[0])
        return sorted(names)

    def get_table(self, name: str) -> Table:
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Table '{name}' does not exist")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return Table(name, schema, self.data_dir)

    def create_table(self, name: str, columns: List[Dict[str, str]]) -> Dict[str, Any]:
        schema = {"name": name, "columns": columns}
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        if os.path.exists(schema_path):
            raise FileExistsError(f"Table '{name}' already exists")
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        # Ensure data file is created
        Table(name, schema, self.data_dir)
        return schema

    def drop_table(self, name: str) -> None:
        schema_path = os.path.join(self.meta_dir, f"{name}.json")
        data_path = os.path.join(self.data_dir, f"{name}.jsonl")
        if os.path.exists(schema_path):
            os.remove(schema_path)
        if os.path.exists(data_path):
            os.remove(data_path)

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
