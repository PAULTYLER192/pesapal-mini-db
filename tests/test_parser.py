"""
Unit tests for QueryParser class.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.parser import QueryParser


def test_parse_create_table():
    """Test parsing CREATE TABLE query."""
    parser = QueryParser()
    
    result = parser.parse("CREATE TABLE users (id, name, email)")
    assert result['type'] == 'CREATE_TABLE'
    assert result['table'] == 'users'
    assert result['columns'] == ['id', 'name', 'email']
    
    # With semicolon
    result = parser.parse("CREATE TABLE products (id, title, price);")
    assert result['type'] == 'CREATE_TABLE'
    assert result['table'] == 'products'


def test_parse_drop_table():
    """Test parsing DROP TABLE query."""
    parser = QueryParser()
    
    result = parser.parse("DROP TABLE users")
    assert result['type'] == 'DROP_TABLE'
    assert result['table'] == 'users'
    
    result = parser.parse("DROP TABLE users;")
    assert result['type'] == 'DROP_TABLE'


def test_parse_insert():
    """Test parsing INSERT query."""
    parser = QueryParser()
    
    # Integer values
    result = parser.parse("INSERT INTO users (id, name, age) VALUES (1, 'John', 30)")
    assert result['type'] == 'INSERT'
    assert result['table'] == 'users'
    assert result['values'] == {'id': 1, 'name': 'John', 'age': 30}
    
    # String with double quotes
    result = parser.parse('INSERT INTO users (id, name) VALUES (2, "Jane")')
    assert result['values'] == {'id': 2, 'name': 'Jane'}


def test_parse_select_all():
    """Test parsing SELECT * query."""
    parser = QueryParser()
    
    result = parser.parse("SELECT * FROM users")
    assert result['type'] == 'SELECT'
    assert result['table'] == 'users'
    assert result['columns'] is None
    assert result['where'] is None


def test_parse_select_columns():
    """Test parsing SELECT with specific columns."""
    parser = QueryParser()
    
    result = parser.parse("SELECT id, name, email FROM users")
    assert result['type'] == 'SELECT'
    assert result['table'] == 'users'
    assert result['columns'] == ['id', 'name', 'email']


def test_parse_select_with_where():
    """Test parsing SELECT with WHERE clause."""
    parser = QueryParser()
    
    # Equality
    result = parser.parse("SELECT * FROM users WHERE age = 30")
    assert result['type'] == 'SELECT'
    assert result['where'] == {'column': 'age', 'operator': '=', 'value': 30}
    
    # Greater than
    result = parser.parse("SELECT * FROM users WHERE age > 25")
    assert result['where']['operator'] == '>'
    assert result['where']['value'] == 25
    
    # String value
    result = parser.parse("SELECT * FROM users WHERE name = 'John'")
    assert result['where']['value'] == 'John'


def test_parse_select_columns_with_where():
    """Test parsing SELECT with columns and WHERE."""
    parser = QueryParser()
    
    result = parser.parse("SELECT name, email FROM users WHERE id = 1")
    assert result['columns'] == ['name', 'email']
    assert result['where'] == {'column': 'id', 'operator': '=', 'value': 1}


def test_parse_update():
    """Test parsing UPDATE query."""
    parser = QueryParser()
    
    # Single column
    result = parser.parse("UPDATE users SET age = 31 WHERE id = 1")
    assert result['type'] == 'UPDATE'
    assert result['table'] == 'users'
    assert result['values'] == {'age': 31}
    assert result['where'] == {'column': 'id', 'operator': '=', 'value': 1}
    
    # Multiple columns
    result = parser.parse("UPDATE users SET name = 'Jane', age = 26 WHERE id = 2")
    assert result['values'] == {'name': 'Jane', 'age': 26}


def test_parse_update_without_where():
    """Test parsing UPDATE without WHERE."""
    parser = QueryParser()
    
    result = parser.parse("UPDATE users SET status = 'active'")
    assert result['type'] == 'UPDATE'
    assert result['values'] == {'status': 'active'}
    assert result['where'] is None


def test_parse_delete():
    """Test parsing DELETE query."""
    parser = QueryParser()
    
    result = parser.parse("DELETE FROM users WHERE id = 1")
    assert result['type'] == 'DELETE'
    assert result['table'] == 'users'
    assert result['where'] == {'column': 'id', 'operator': '=', 'value': 1}


def test_parse_delete_without_where():
    """Test parsing DELETE without WHERE."""
    parser = QueryParser()
    
    result = parser.parse("DELETE FROM users")
    assert result['type'] == 'DELETE'
    assert result['table'] == 'users'
    assert result['where'] is None


def test_parse_case_insensitive():
    """Test that parsing is case insensitive."""
    parser = QueryParser()
    
    result = parser.parse("select * from users")
    assert result['type'] == 'SELECT'
    
    result = parser.parse("SELECT * FROM users")
    assert result['type'] == 'SELECT'
    
    result = parser.parse("SeLeCt * FrOm users")
    assert result['type'] == 'SELECT'


def test_parse_with_extra_spaces():
    """Test parsing with extra spaces."""
    parser = QueryParser()
    
    result = parser.parse("SELECT   *   FROM   users")
    assert result['type'] == 'SELECT'
    
    result = parser.parse("SELECT id,   name,   email FROM users")
    assert result['columns'] == ['id', 'name', 'email']


def test_parse_invalid_query():
    """Test parsing invalid queries."""
    parser = QueryParser()
    
    with pytest.raises(ValueError):
        parser.parse("INVALID QUERY")
    
    with pytest.raises(ValueError):
        parser.parse("SELECT")
    
    with pytest.raises(ValueError):
        parser.parse("")


def test_parse_where_operators():
    """Test parsing different WHERE operators."""
    parser = QueryParser()
    
    operators = ['=', '!=', '<', '>', '<=', '>=']
    for op in operators:
        result = parser.parse(f"SELECT * FROM users WHERE age {op} 30")
        assert result['where']['operator'] == op


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
