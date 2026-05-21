from flask import Flask, render_template_string
import pyodbc
import sys

app = Flask(__name__)

# =========================================================================
# STEP 1: PASTE YOUR EXACT AZURE SQL CONNECTION STRING HERE FROM NOTEPAD
# Make sure to replace your real username (e.g. dbadmin) and your password!
# =========================================================================
def test_db_connection():
    """Attempts to connect to the Azure SQL Database to verify credentials."""
    try:
        conn = pyodbc.connect(
            Driver='{ODBC Driver 18 for SQL Server}',
            Server='tcp:myecomm-server.database.windows.net,1433',
            Database='ecomm-db-pb',
            UID='dbadmin',
            PWD='Password1234',
            Encrypt='yes',
            TrustServerCertificate='yes',
            Timeout=30
        )
        cursor = conn.cursor()
        # Run a simple built-in query to prove the database is responding
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        conn.close()
        return f"Connected Successfully! Database Version: {row[0]}"
    except Exception as e:
        return f"Connection Failed! Error details: {str(e)}"



# HTML Template layout for your web browser interface
HTML_TEMPLATE = """
<!hidden>
<html>
<head>
    <title>E-Commerce App Layer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #0078d4; }
        .status-box { padding: 15px; border-radius: 4px; margin-top: 20px; font-weight: bold; font-family: monospace; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { font-size: 0.9em; color: #666; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Myecomm Production Frontend</h1>
        <p>Your Public Load Balancer has successfully routed traffic to this VM instance.</p>
        <hr/>
        <h3>Backend Tier Verification</h3>
        <div class="status-box {{ status_class }}">
            {{ db_status_message }}
        </div>
        <p class="info">Architecture Status: <strong>3-Tier Verified Active</strong></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Check the database connectivity live on every page reload
    db_result = test_db_connection()
    
    # Decide styling based on connection success
    if "Successfully" in db_result:
        status_class = "success"
    else:
        status_class = "fail"
        
    return render_template_string(HTML_TEMPLATE, db_status_message=db_result, status_class=status_class)

if __name__ == '__main__':
    # Binds to Port 80 to catch the Load Balancer's standard HTTP probes
    app.run(host='0.0.0.0', port=80)
