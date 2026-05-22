from flask import Flask, render_template_string
import socket  # Identifies which scale set instance is serving traffic

# Safe import wrap for pyodbc to handle environment driver absences gracefully
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

app = Flask(__name__)

def test_db_connection():
    """Attempts to connect to the updated Azure SQL Database to verify credentials."""
    if not HAS_PYODBC:
        return "Connection Failed! Error details: The 'pyodbc' library or standard Linux compilation tools are missing from this host environment."
        
    try:
        conn = pyodbc.connect(
            Driver='{ODBC Driver 18 for SQL Server}',
            Server='tcp:ecomm-server-pb.database.windows.net,1433',
            Database='free-sql-db-8345161',
            UID='dbadmin',
            PWD='Password1234',  
            Encrypt='yes',
            TrustServerCertificate='yes',
            Timeout=15  # Decreased slightly so your webpage doesn't hang too long on load
        )
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        conn.close()
        return f"Connected Successfully! Database Version: {row[0]}"
    except Exception as e:
        return f"Connection Failed! Error details: {str(e)}"

# HTML template tracking Scale Set routing status
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>E-Commerce App Layer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #0078d4; margin-bottom: 5px; }
        .server-badge { background-color: #0078d4; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; display: inline-block; margin-bottom: 20px; }
        .status-box { padding: 15px; border-radius: 4px; margin-top: 20px; font-weight: bold; font-family: monospace; word-wrap: break-word; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { font-size: 0.9em; color: #666; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Myecomm Production Frontend</h1>
        <div class="server-badge">Served by Instance: {{ server_hostname }}</div>
        <p>Your Public Load Balancer has successfully routed traffic to this scale set instance.</p>
        <hr/>
        <h3>Backend Tier Verification</h3>
        <div class="status-box {{ status_class }}">
            {{ db_status_message }}
        </div>
        <p class="info">Architecture Status: <strong>3-Tier Verified Active via Scale Set</strong></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Check the database connectivity live on every page reload
    db_result = test_db_connection()
    
    # Dynamically grab the hostname of whichever VM is handling this execution loop
    vm_hostname = socket.gethostname()
    
    # Decide styling based on connection success
    if "Successfully" in db_result:
        status_class = "success"
    else:
        status_class = "fail"
        
    return render_template_string(
        HTML_TEMPLATE, 
        db_status_message=db_result, 
        status_class=status_class,
        server_hostname=vm_hostname
    )

if __name__ == '__main__':
    # Binds to Port 80 to catch the Load Balancer's standard HTTP traffic flow
    app.run(host='0.0.0.0', port=80)
