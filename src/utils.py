"""
Utility functions for the mini database.
"""


def validate_column_name(name):
    """
    Validate column name.
    
    Args:
        name (str): Column name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    if not name[0].isalpha() and name[0] != '_':
        return False
    return all(c.isalnum() or c == '_' for c in name)


def validate_table_name(name):
    """
    Validate table name.
    
    Args:
        name (str): Table name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return validate_column_name(name)


def parse_value(value_str):
    """
    Parse a string value to appropriate Python type.
    
    Args:
        value_str (str): Value as string
        
    Returns:
        Appropriate Python type (int, float, str, bool, None)
    """
    if not isinstance(value_str, str):
        return value_str
    
    # Check for NULL
    if value_str.upper() == 'NULL':
        return None
    
    # Check for boolean
    if value_str.upper() == 'TRUE':
        return True
    if value_str.upper() == 'FALSE':
        return False
    
    # Try integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Remove quotes if present
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    return value_str


def format_value(value):
    """
    Format a Python value for display.
    
    Args:
        value: Value to format
        
    Returns:
        str: Formatted value
    """
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, str):
        return f"'{value}'"
    return str(value)


def compare_values(val1, operator, val2):
    """
    Compare two values using the specified operator.
    
    Args:
        val1: First value
        operator (str): Comparison operator (=, !=, <, >, <=, >=)
        val2: Second value
        
    Returns:
        bool: Result of comparison
    """
    if operator == '=':
        return val1 == val2
    elif operator == '!=':
        return val1 != val2
    elif operator == '<':
        return val1 < val2
    elif operator == '>':
        return val1 > val2
    elif operator == '<=':
        return val1 <= val2
    elif operator == '>=':
        return val1 >= val2
    else:
        raise ValueError(f"Unknown operator: {operator}")
