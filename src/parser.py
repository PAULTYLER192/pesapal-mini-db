import re
from typing import Any, Dict, List, Optional

# Very small SQL parser supporting a subset of statements
# Supported:
# - CREATE TABLE name (col type, ...)
# - DROP TABLE name
# - INSERT INTO name (a, b) VALUES (1, 'x')
# - SELECT a, b FROM name [WHERE x = 1 AND y = 'z'] [LIMIT n]
# - UPDATE name SET a = 1, b = 'z' WHERE x = 2
# - DELETE FROM name WHERE x = 3
# - SHOW TABLES
# - DESCRIBE name

_ws = re.compile(r"\s+")


def _strip_semicolon(sql: str) -> str:
    sql = sql.strip()
    if sql.endswith(";"):
        sql = sql[:-1]
    return sql.strip()


def _split_commas(s: str) -> List[str]:
    # Split by commas not inside quotes
    parts: List[str] = []
    buf = []
    in_s = False
    in_d = False
    for ch in s:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        if ch == ',' and not in_s and not in_d:
            parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append(''.join(buf).strip())
    return [p for p in parts if p]


def _parse_value(token: str) -> Any:
    t = token.strip()
    if t.lower() == "null":
        return None
    if (t.startswith("'") and t.endswith("'")) or (t.startswith('"') and t.endswith('"')):
        return t[1:-1]
    if t.lower() in ("true", "false"):
        return t.lower() == "true"
    try:
        if "." in t:
            return float(t)
        return int(t)
    except ValueError:
        return t


def parse_sql(sql: str) -> Dict[str, Any]:
    sql = _strip_semicolon(sql)
    upper = sql.upper()

    if upper.startswith("SHOW TABLES"):
        return {"type": "show_tables"}

    if upper.startswith("DESCRIBE"):
        # DESCRIBE name
        parts = _ws.split(sql, maxsplit=1)
        _, rest = parts[0], parts[1] if len(parts) > 1 else ""
        name = rest.strip()
        return {"type": "describe", "name": name}

    if upper.startswith("DROP TABLE"):
        # DROP TABLE name
        parts = _ws.split(sql, maxsplit=2)
        name = parts[2].strip()
        return {"type": "drop_table", "name": name}

    if upper.startswith("CREATE TABLE"):
        # CREATE TABLE name (col type, ...)
        m = re.match(r"CREATE\s+TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)$", sql, flags=re.IGNORECASE)
        if not m:
            raise ValueError("Invalid CREATE TABLE syntax")
        name = m.group(1)
        body = m.group(2).strip()
        cols: List[Dict[str, str]] = []
        for part in _split_commas(body):
            pieces = _ws.split(part)
            if len(pieces) < 2:
                raise ValueError(f"Invalid column spec: {part}")
            col_name = pieces[0]
            col_type = pieces[1]
            cols.append({"name": col_name, "type": col_type})
        return {"type": "create_table", "name": name, "columns": cols}

    if upper.startswith("INSERT INTO"):
        # INSERT INTO name (a,b) VALUES (1,'x')
        m = re.match(r"INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)$", sql, flags=re.IGNORECASE)
        if not m:
            raise ValueError("Invalid INSERT syntax")
        name = m.group(1)
        cols = [c.strip() for c in _split_commas(m.group(2))]
        vals = [_parse_value(v) for v in _split_commas(m.group(3))]
        if len(cols) != len(vals):
            raise ValueError("Columns and values length mismatch")
        return {"type": "insert", "name": name, "values": dict(zip(cols, vals))}

    if upper.startswith("SELECT"):
        # SELECT a,b FROM name [WHERE x = 1 AND y = 'z'] [LIMIT n]
        m = re.match(r"SELECT\s+(.*?)\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(.*)$", sql, flags=re.IGNORECASE)
        if not m:
            raise ValueError("Invalid SELECT syntax")
        cols_part = m.group(1).strip()
        name = m.group(2)
        tail = m.group(3).strip()
        columns = None if cols_part == "*" else [c.strip() for c in _split_commas(cols_part)]
        where: Optional[Dict[str, Any]] = None
        limit: Optional[int] = None
        if tail:
            # WHERE ... and/or LIMIT ... can appear in any order; handle simply
            # Extract LIMIT
            lim_m = re.search(r"\bLIMIT\s+(\d+)\b", tail, flags=re.IGNORECASE)
            if lim_m:
                limit = int(lim_m.group(1))
                tail = tail[:lim_m.start()].strip()
            # Extract WHERE
            if tail.upper().startswith("WHERE"):
                cond = tail[5:].strip()
                where = {}
                for conj in re.split(r"\bAND\b", cond, flags=re.IGNORECASE):
                    cmp_m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", conj.strip())
                    if not cmp_m:
                        raise ValueError(f"Invalid WHERE condition: {conj}")
                    where[cmp_m.group(1)] = _parse_value(cmp_m.group(2).strip())
        return {"type": "select", "name": name, "columns": columns, "where": where, "limit": limit}

    if upper.startswith("UPDATE"):
        # UPDATE name SET a=1, b='x' WHERE c=2
        m = re.match(r"UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+SET\s+(.*?)\s*(WHERE\s+.*)?$", sql, flags=re.IGNORECASE)
        if not m:
            raise ValueError("Invalid UPDATE syntax")
        name = m.group(1)
        set_part = m.group(2)
        where_part = m.group(3)
        set_vals: Dict[str, Any] = {}
        for assign in _split_commas(set_part):
            am = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", assign.strip())
            if not am:
                raise ValueError(f"Invalid SET expression: {assign}")
            set_vals[am.group(1)] = _parse_value(am.group(2).strip())
        where: Optional[Dict[str, Any]] = None
        if where_part:
            cond = where_part.strip()[5:].strip()  # remove WHERE
            where = {}
            for conj in re.split(r"\bAND\b", cond, flags=re.IGNORECASE):
                cmp_m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", conj.strip())
                if not cmp_m:
                    raise ValueError(f"Invalid WHERE condition: {conj}")
                where[cmp_m.group(1)] = _parse_value(cmp_m.group(2).strip())
        return {"type": "update", "name": name, "set": set_vals, "where": where}

    if upper.startswith("DELETE FROM"):
        # DELETE FROM name WHERE cond
        m = re.match(r"DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(WHERE\s+.*)?$", sql, flags=re.IGNORECASE)
        if not m:
            raise ValueError("Invalid DELETE syntax")
        name = m.group(1)
        where_part = m.group(2)
        where: Optional[Dict[str, Any]] = None
        if where_part:
            cond = where_part.strip()[5:].strip()
            where = {}
            for conj in re.split(r"\bAND\b", cond, flags=re.IGNORECASE):
                cmp_m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", conj.strip())
                if not cmp_m:
                    raise ValueError(f"Invalid WHERE condition: {conj}")
                where[cmp_m.group(1)] = _parse_value(cmp_m.group(2).strip())
        return {"type": "delete", "name": name, "where": where}

    raise ValueError("Unsupported or invalid SQL statement")
