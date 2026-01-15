"""
Unit tests for Table class.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.table import Table


def test_table_creation():
    """Test table creation."""
    table = Table('users', ['id', 'name', 'email'])
    assert table.name == 'users'
    assert table.columns == ['id', 'name', 'email']
    assert table.count() == 0


def test_table_invalid_column():
    """Test table creation with invalid column name."""
    with pytest.raises(ValueError):
        Table('users', ['id', '123invalid', 'email'])


def test_insert():
    """Test inserting rows."""
    table = Table('users', ['id', 'name'])
    
    # Valid insert
    result = table.insert({'id': 1, 'name': 'John'})
    assert result == True
    assert table.count() == 1
    
    # Insert another row
    table.insert({'id': 2, 'name': 'Jane'})
    assert table.count() == 2


def test_insert_missing_column():
    """Test insert with missing column."""
    table = Table('users', ['id', 'name', 'email'])
    
    with pytest.raises(ValueError, match="Missing columns"):
        table.insert({'id': 1, 'name': 'John'})


def test_insert_extra_column():
    """Test insert with extra column."""
    table = Table('users', ['id', 'name'])
    
    with pytest.raises(ValueError, match="Unknown columns"):
        table.insert({'id': 1, 'name': 'John', 'extra': 'value'})


def test_select_all():
    """Test selecting all rows."""
    table = Table('users', ['id', 'name'])
    table.insert({'id': 1, 'name': 'John'})
    table.insert({'id': 2, 'name': 'Jane'})
    
    rows = table.select()
    assert len(rows) == 2
    assert rows[0] == {'id': 1, 'name': 'John'}
    assert rows[1] == {'id': 2, 'name': 'Jane'}


def test_select_columns():
    """Test selecting specific columns."""
    table = Table('users', ['id', 'name', 'email'])
    table.insert({'id': 1, 'name': 'John', 'email': 'john@example.com'})
    
    rows = table.select(columns=['name', 'email'])
    assert len(rows) == 1
    assert rows[0] == {'name': 'John', 'email': 'john@example.com'}
    assert 'id' not in rows[0]


def test_select_with_where():
    """Test selecting with WHERE clause."""
    table = Table('users', ['id', 'name', 'age'])
    table.insert({'id': 1, 'name': 'John', 'age': 30})
    table.insert({'id': 2, 'name': 'Jane', 'age': 25})
    table.insert({'id': 3, 'name': 'Bob', 'age': 35})
    
    # Equal
    rows = table.select(where={'column': 'age', 'operator': '=', 'value': 30})
    assert len(rows) == 1
    assert rows[0]['name'] == 'John'
    
    # Greater than
    rows = table.select(where={'column': 'age', 'operator': '>', 'value': 25})
    assert len(rows) == 2


def test_select_unknown_column():
    """Test select with unknown column."""
    table = Table('users', ['id', 'name'])
    table.insert({'id': 1, 'name': 'John'})
    
    with pytest.raises(ValueError, match="Unknown column"):
        table.select(columns=['id', 'unknown'])


def test_update():
    """Test updating rows."""
    table = Table('users', ['id', 'name', 'age'])
    table.insert({'id': 1, 'name': 'John', 'age': 30})
    table.insert({'id': 2, 'name': 'Jane', 'age': 25})
    
    # Update with WHERE
    count = table.update({'age': 31}, where={'column': 'id', 'operator': '=', 'value': 1})
    assert count == 1
    
    rows = table.select(where={'column': 'id', 'operator': '=', 'value': 1})
    assert rows[0]['age'] == 31


def test_update_all():
    """Test updating all rows."""
    table = Table('users', ['id', 'name', 'status'])
    table.insert({'id': 1, 'name': 'John', 'status': 'active'})
    table.insert({'id': 2, 'name': 'Jane', 'status': 'active'})
    
    count = table.update({'status': 'inactive'})
    assert count == 2
    
    rows = table.select()
    assert all(row['status'] == 'inactive' for row in rows)


def test_delete():
    """Test deleting rows."""
    table = Table('users', ['id', 'name'])
    table.insert({'id': 1, 'name': 'John'})
    table.insert({'id': 2, 'name': 'Jane'})
    table.insert({'id': 3, 'name': 'Bob'})
    
    # Delete with WHERE
    count = table.delete(where={'column': 'id', 'operator': '=', 'value': 2})
    assert count == 1
    assert table.count() == 2


def test_delete_all():
    """Test deleting all rows."""
    table = Table('users', ['id', 'name'])
    table.insert({'id': 1, 'name': 'John'})
    table.insert({'id': 2, 'name': 'Jane'})
    
    count = table.delete()
    assert count == 2
    assert table.count() == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
