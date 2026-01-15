// Pesapal Mini Database Web App JavaScript

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
                    
                    const tableName = document.createElement('div');
                    tableName.className = 'table-name';
                    tableName.textContent = table.name;
                    
                    const tableInfo = document.createElement('div');
                    tableInfo.className = 'table-info';
                    tableInfo.textContent = `Columns: ${table.columns.join(', ')}`;
                    
                    const rowInfo = document.createElement('br');
                    tableInfo.appendChild(rowInfo);
                    tableInfo.appendChild(document.createTextNode(`Rows: ${table.row_count}`));
                    
                    tableItem.appendChild(tableName);
                    tableItem.appendChild(tableInfo);
                    tablesList.appendChild(tableItem);
                });
            }
        } else {
            const errorMsg = document.createElement('p');
            errorMsg.className = 'error-message';
            errorMsg.textContent = `Error: ${data.error}`;
            tablesList.innerHTML = '';
            tablesList.appendChild(errorMsg);
        }
    } catch (error) {
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = `Error loading tables: ${error.message}`;
        tablesList.innerHTML = '';
        tablesList.appendChild(errorMsg);
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
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Please enter a query';
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(errorMsg);
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
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            const strong = document.createElement('strong');
            strong.textContent = 'Error: ';
            errorDiv.appendChild(strong);
            errorDiv.appendChild(document.createTextNode(data.error));
            resultsDiv.innerHTML = '';
            resultsDiv.appendChild(errorDiv);
        }
    } catch (error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        const strong = document.createElement('strong');
        strong.textContent = 'Error: ';
        errorDiv.appendChild(strong);
        errorDiv.appendChild(document.createTextNode(error.message));
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(errorDiv);
    }
}

// Display query results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    if (data.type === 'SELECT') {
        if (data.data.length === 0) {
            resultsDiv.innerHTML = '';
            
            const successDiv = document.createElement('div');
            successDiv.className = 'success-message';
            successDiv.textContent = 'Query executed successfully';
            
            const infoP = document.createElement('p');
            infoP.className = 'result-info';
            infoP.textContent = 'No rows returned';
            
            resultsDiv.appendChild(successDiv);
            resultsDiv.appendChild(infoP);
        } else {
            // Get columns from first row
            const columns = Object.keys(data.data[0]);
            
            // Create table structure safely
            resultsDiv.innerHTML = '';
            
            const successDiv = document.createElement('div');
            successDiv.className = 'success-message';
            successDiv.textContent = 'Query executed successfully';
            
            const infoP = document.createElement('p');
            infoP.className = 'result-info';
            infoP.textContent = `Returned ${data.count} row(s)`;
            
            resultsDiv.appendChild(successDiv);
            resultsDiv.appendChild(infoP);
            
            const table = document.createElement('table');
            table.className = 'data-table';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create body
            const tbody = document.createElement('tbody');
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                columns.forEach(col => {
                    const td = document.createElement('td');
                    const value = row[col];
                    td.textContent = value === null ? 'NULL' : String(value);
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            
            resultsDiv.appendChild(table);
        }
    } else {
        resultsDiv.innerHTML = '';
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        
        const strong = document.createElement('strong');
        strong.textContent = 'Success! ';
        successDiv.appendChild(strong);
        successDiv.appendChild(document.createTextNode(data.message));
        
        resultsDiv.appendChild(successDiv);
    }
}

// Allow Enter key to execute query (with Ctrl/Cmd)
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        executeQuery();
    }
});
