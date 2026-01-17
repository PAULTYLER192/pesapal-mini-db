import os
import sys
from typing import Any

# Allow running from repo root
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import Database  # type: ignore

BANNER = """
Mini DB REPL
Commands: CREATE TABLE, INSERT INTO, SELECT, UPDATE, DELETE, DROP TABLE, SHOW TABLES, DESCRIBE
Type 'exit' or Ctrl+C to quit.
"""


def pretty(obj: Any) -> str:
    try:
        import json
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)


def main() -> None:
    db = Database(base_dir=os.path.dirname(__file__))
    print(BANNER)
    while True:
        try:
            line = input("db> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        try:
            result = db.execute(line)
            if isinstance(result, (list, dict)):
                print(pretty(result))
            else:
                print(result)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
