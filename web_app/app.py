"""
Flask web application for Pesapal Mini Database.
"""
from flask import Flask, render_template, request, jsonify, session
import sys
import os

# Add parent directory to path to import src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import Database
from src.parser import QueryParser

app = Flask(__name__)
app.secret_key = 'pesapal-mini-db-secret-key-change-in-production'

# Global database instance (in-memory)
db = Database("webapp_db")
parser = QueryParser()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/tables', methods=['GET'])
def list_tables():
    """List all tables in the database."""
    try:
        tables = db.list_tables()
        result = []
        for table_name in tables:
            table = db.get_table(table_name)
            result.append({
                'name': table_name,
                'columns': table.columns,
                'row_count': table.count()
            })
        return jsonify({'success': True, 'tables': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a SQL-like query."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        # Parse the query
        parsed = parser.parse(query)
        query_type = parsed['type']
        
        # Execute based on type
        if query_type == 'CREATE_TABLE':
            db.create_table(parsed['table'], parsed['columns'])
            return jsonify({
                'success': True,
                'message': f"Table '{parsed['table']}' created successfully",
                'type': 'CREATE_TABLE'
            })
        
        elif query_type == 'DROP_TABLE':
            db.drop_table(parsed['table'])
            return jsonify({
                'success': True,
                'message': f"Table '{parsed['table']}' dropped successfully",
                'type': 'DROP_TABLE'
            })
        
        elif query_type == 'INSERT':
            db.insert(parsed['table'], parsed['values'])
            return jsonify({
                'success': True,
                'message': f"Row inserted into '{parsed['table']}'",
                'type': 'INSERT'
            })
        
        elif query_type == 'SELECT':
            rows = db.select(parsed['table'], parsed['columns'], parsed['where'])
            return jsonify({
                'success': True,
                'data': rows,
                'count': len(rows),
                'type': 'SELECT'
            })
        
        elif query_type == 'UPDATE':
            count = db.update(parsed['table'], parsed['values'], parsed['where'])
            return jsonify({
                'success': True,
                'message': f"Updated {count} row(s) in '{parsed['table']}'",
                'count': count,
                'type': 'UPDATE'
            })
        
        elif query_type == 'DELETE':
            count = db.delete(parsed['table'], parsed['where'])
            return jsonify({
                'success': True,
                'message': f"Deleted {count} row(s) from '{parsed['table']}'",
                'count': count,
                'type': 'DELETE'
            })
        
        else:
            return jsonify({'success': False, 'error': f"Unknown query type: {query_type}"}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/table/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get all data from a specific table."""
    try:
        table = db.get_table(table_name)
        rows = table.select()
        return jsonify({
            'success': True,
            'table': table_name,
            'columns': table.columns,
            'data': rows,
            'count': len(rows)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    # Create a sample table for demonstration
    try:
        db.create_table('users', ['id', 'name', 'email', 'age'])
        db.insert('users', {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'age': 30})
        db.insert('users', {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25})
        print("Sample 'users' table created with 2 rows")
    except:
        pass
    
    print("Starting Pesapal Mini DB Web App...")
    print("Visit http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
