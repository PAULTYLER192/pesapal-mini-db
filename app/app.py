"""Flask Web Application for Mini Database.

Provides a web interface for executing SQL commands and viewing results.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import Database

app = Flask(__name__)
db = Database()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/execute', methods=['POST'])
def execute_sql():
    """Execute SQL command via API.
    
    Expects JSON with 'sql' field.
    Returns execution results as JSON.
    """
    data = request.get_json()
    sql = data.get('sql', '').strip()
    
    if not sql:
        return jsonify({
            'success': False,
            'error': 'No SQL command provided'
        })
    
    # Handle special commands
    if sql.upper() == 'SHOW TABLES':
        tables = db.list_tables()
        return jsonify({
            'success': True,
            'special': 'show_tables',
            'tables': tables
        })
    
    if sql.upper().startswith('DESCRIBE '):
        table_name = sql.split(maxsplit=1)[1].strip()
        try:
            schema = db.get_table_schema(table_name)
            return jsonify({
                'success': True,
                'special': 'describe',
                'table': table_name,
                'schema': schema
            })
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': f"Table '{table_name}' does not exist"
            })
    
    # Execute SQL command
    result = db.execute(sql)
    return jsonify(result)


@app.route('/api/tables', methods=['GET'])
def list_tables():
    """List all tables via API."""
    tables = db.list_tables()
    return jsonify({
        'success': True,
        'tables': tables
    })


@app.route('/api/table/<table_name>/schema', methods=['GET'])
def get_table_schema(table_name):
    """Get table schema via API."""
    try:
        schema = db.get_table_schema(table_name)
        return jsonify({
            'success': True,
            'table': table_name,
            'schema': schema
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': f"Table '{table_name}' does not exist"
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
