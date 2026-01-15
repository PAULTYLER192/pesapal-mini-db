"""Main CLI REPL for Mini Database.

Provides an interactive command-line interface for executing SQL commands.
"""

import sys
from src.database import Database


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print(" Mini Database - SQL REPL")
    print("=" * 60)
    print(" Type SQL commands or 'help' for help.")
    print(" Type 'exit' or 'quit' to exit.")
    print("=" * 60)
    print()


def print_help():
    """Print help information."""
    print("\nAvailable SQL Commands:")
    print("-" * 60)
    print("  CREATE TABLE name (col1 TYPE1, col2 TYPE2, ...)")
    print("    Types: TEXT, INTEGER, FLOAT, BOOLEAN")
    print()
    print("  INSERT INTO table VALUES (val1, val2, ...)")
    print()
    print("  SELECT * FROM table [WHERE col=value]")
    print("  SELECT col1, col2 FROM table [WHERE col>value]")
    print()
    print("  UPDATE table SET col=value [WHERE col=value]")
    print()
    print("  DELETE FROM table [WHERE col=value]")
    print()
    print("  DROP TABLE table")
    print()
    print("Special Commands:")
    print("-" * 60)
    print("  SHOW TABLES  - List all tables")
    print("  DESCRIBE table - Show table schema")
    print("  help         - Show this help message")
    print("  exit/quit    - Exit the REPL")
    print()


def format_table(columns, rows):
    """Format query results as a table.
    
    Args:
        columns: List of column names
        rows: List of row dictionaries
    """
    if not rows:
        print("(empty result set)")
        return
    
    # Calculate column widths
    widths = {}
    for col in columns:
        widths[col] = len(col)
        for row in rows:
            value = str(row.get(col, ''))
            widths[col] = max(widths[col], len(value))
    
    # Print header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        values = [str(row.get(col, '')).ljust(widths[col]) for col in columns]
        print(" | ".join(values))
    
    print(f"\n({len(rows)} row(s))")


def handle_special_command(db, command):
    """Handle special commands (non-SQL).
    
    Args:
        db: Database instance
        command: Command string
        
    Returns:
        True if command was handled, False otherwise
    """
    command_upper = command.upper().strip()
    
    if command_upper == 'SHOW TABLES':
        tables = db.list_tables()
        if tables:
            print("\nTables:")
            for table in tables:
                print(f"  - {table}")
            print(f"\n({len(tables)} table(s))")
        else:
            print("\n(no tables)")
        return True
    
    if command_upper.startswith('DESCRIBE '):
        table_name = command.split(maxsplit=1)[1].strip()
        try:
            schema = db.get_table_schema(table_name)
            print(f"\nTable: {table_name}")
            print("-" * 40)
            print(f"{'Column':<20} {'Type':<15}")
            print("-" * 40)
            for col_name, col_type in schema.items():
                print(f"{col_name:<20} {col_type:<15}")
            print()
        except FileNotFoundError:
            print(f"Error: Table '{table_name}' does not exist")
        return True
    
    return False


def repl():
    """Run the REPL (Read-Eval-Print Loop)."""
    db = Database()
    print_banner()
    
    while True:
        try:
            # Read input
            sql = input("minidb> ").strip()
            
            if not sql:
                continue
            
            # Check for exit commands
            if sql.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            # Check for help command
            if sql.lower() == 'help':
                print_help()
                continue
            
            # Check for special commands
            if handle_special_command(db, sql):
                continue
            
            # Execute SQL command
            result = db.execute(sql)
            
            # Display results
            if result['success']:
                if result.get('rows') is not None:
                    # SELECT query
                    columns = result['columns']
                    if columns == ['*']:
                        # Get actual columns from first row
                        if result['rows']:
                            columns = list(result['rows'][0].keys())
                        else:
                            columns = []
                    
                    format_table(columns, result['rows'])
                else:
                    # Other commands
                    print(result.get('message', 'Success'))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' or 'quit' to exit.")
            continue
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    repl()
