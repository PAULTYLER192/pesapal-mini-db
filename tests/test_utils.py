"""
Unit tests for utils module.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import (
    validate_column_name,
    validate_table_name,
    parse_value,
    format_value,
    compare_values
)


def test_validate_column_name():
    """Test column name validation."""
    # Valid names
    assert validate_column_name('name') == True
    assert validate_column_name('_id') == True
    assert validate_column_name('col123') == True
    assert validate_column_name('user_name') == True
    
    # Invalid names
    assert validate_column_name('') == False
    assert validate_column_name('123col') == False
    assert validate_column_name('col-name') == False
    assert validate_column_name('col name') == False
    assert validate_column_name(None) == False
    assert validate_column_name(123) == False


def test_validate_table_name():
    """Test table name validation."""
    assert validate_table_name('users') == True
    assert validate_table_name('my_table') == True
    assert validate_table_name('') == False
    assert validate_table_name('123table') == False


def test_parse_value():
    """Test value parsing."""
    # NULL
    assert parse_value('NULL') == None
    assert parse_value('null') == None
    
    # Boolean
    assert parse_value('TRUE') == True
    assert parse_value('true') == True
    assert parse_value('FALSE') == False
    assert parse_value('false') == False
    
    # Integer
    assert parse_value('123') == 123
    assert parse_value('-456') == -456
    
    # Float
    assert parse_value('3.14') == 3.14
    assert parse_value('-2.5') == -2.5
    
    # String with quotes
    assert parse_value('"hello"') == 'hello'
    assert parse_value("'world'") == 'world'
    
    # String without quotes
    assert parse_value('test') == 'test'
    
    # Non-string input
    assert parse_value(42) == 42


def test_format_value():
    """Test value formatting."""
    assert format_value(None) == 'NULL'
    assert format_value(True) == 'TRUE'
    assert format_value(False) == 'FALSE'
    assert format_value('hello') == "'hello'"
    assert format_value(123) == '123'
    assert format_value(3.14) == '3.14'


def test_compare_values():
    """Test value comparison."""
    # Equality
    assert compare_values(5, '=', 5) == True
    assert compare_values(5, '=', 6) == False
    
    # Inequality
    assert compare_values(5, '!=', 6) == True
    assert compare_values(5, '!=', 5) == False
    
    # Less than
    assert compare_values(3, '<', 5) == True
    assert compare_values(5, '<', 3) == False
    
    # Greater than
    assert compare_values(5, '>', 3) == True
    assert compare_values(3, '>', 5) == False
    
    # Less than or equal
    assert compare_values(3, '<=', 5) == True
    assert compare_values(5, '<=', 5) == True
    assert compare_values(6, '<=', 5) == False
    
    # Greater than or equal
    assert compare_values(5, '>=', 3) == True
    assert compare_values(5, '>=', 5) == True
    assert compare_values(3, '>=', 5) == False


if __name__ == '__main__':
    test_validate_column_name()
    test_validate_table_name()
    test_parse_value()
    test_format_value()
    test_compare_values()
    print("All utils tests passed!")
