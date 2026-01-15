// Pesapal Mini Database Web App JavaScript

// Load tables on page load
document.addEventListener('DOMContentLoaded', function() {
    refreshTables();
});

// Refresh the tables list
async function refreshTables() {
    const tablesList = document.getElementById('tables-list');
    tablesList.innerHTML = '<p class="loading">Loading tables...</p>';
    
    try {
        const response = await fetch('/api/tables');
        const data = await response.json();
        
        if (data.success) {
            if (data.tables.length === 0) {
                tablesList.innerHTML = '<p class="placeholder">No tables yet. Create one using SQL!</p>';
            } else {
                tablesList.innerHTML = '';
                data.tables.forEach(table => {
                    const tableItem = document.createElement('div');
                    tableItem.className = 'table-item';
                    tableItem.onclick = () => viewTable(table.name);
                    
                    tableItem.innerHTML = `
                        <div class="table-name">${table.name}</div>
                        <div class="table-info">
                            Columns: ${table.columns.join(', ')}<br>
                            Rows: ${table.row_count}
                        </div>
                    `;
                    
                    tablesList.appendChild(tableItem);
                });
            }
        } else {
            tablesList.innerHTML = `<p class="error-message">Error: ${data.error}</p>`;
        }
    } catch (error) {
        tablesList.innerHTML = `<p class="error-message">Error loading tables: ${error.message}</p>`;
    }
}

// View table data
async function viewTable(tableName) {
    setQuery(`SELECT * FROM ${tableName}`);
    executeQuery();
}

// Set query in the input
function setQuery(query) {
    document.getElementById('query-input').value = query;
}

// Execute the SQL query
async function executeQuery() {
    const queryInput = document.getElementById('query-input');
    const resultsDiv = document.getElementById('results');
    const query = queryInput.value.trim();
    
    if (!query) {
        resultsDiv.innerHTML = '<p class="error-message">Please enter a query</p>';
        return;
    }
    
    resultsDiv.innerHTML = '<p class="loading">Executing query...</p>';
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            
            // Refresh tables list if it was a CREATE/DROP/INSERT/UPDATE/DELETE
            if (['CREATE_TABLE', 'DROP_TABLE', 'INSERT', 'UPDATE', 'DELETE'].includes(data.type)) {
                refreshTables();
            }
        } else {
            resultsDiv.innerHTML = `<div class="error-message"><strong>Error:</strong> ${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message"><strong>Error:</strong> ${error.message}</div>`;
    }
}

// Display query results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    if (data.type === 'SELECT') {
        if (data.data.length === 0) {
            resultsDiv.innerHTML = `
                <div class="success-message">Query executed successfully</div>
                <p class="result-info">No rows returned</p>
            `;
        } else {
            // Get columns from first row
            const columns = Object.keys(data.data[0]);
            
            let html = `
                <div class="success-message">Query executed successfully</div>
                <p class="result-info">Returned ${data.count} row(s)</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.data.forEach(row => {
                html += '<tr>';
                columns.forEach(col => {
                    const value = row[col];
                    const displayValue = value === null ? 'NULL' : value;
                    html += `<td>${displayValue}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            resultsDiv.innerHTML = html;
        }
    } else {
        resultsDiv.innerHTML = `
            <div class="success-message">
                <strong>Success!</strong> ${data.message}
            </div>
        `;
    }
}

// Allow Enter key to execute query (with Ctrl/Cmd)
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        executeQuery();
    }
});
