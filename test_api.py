import urllib.request
import urllib.parse
import urllib.error
import json
import threading
import time
import sys
import os

# Ensure the my_env module is found in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "my_env", "server"))

# Provide a dummy API key so the OpenAI client initializes without crashing
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-local-testing"

def start_server():
    import uvicorn
    # Start the actual AI Task Manager API application
    from main import app 
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

print("Waiting for server to start up (this may take 20-40 seconds on first run due to NLP model loading)...")

base_url = "http://127.0.0.1:8000"

import urllib.error
# Poll until the server is alive
server_up = False
for i in range(30):
    try:
        req = urllib.request.Request(f"{base_url}/docs", method="GET")
        with urllib.request.urlopen(req) as response:
            server_up = True
            break
    except Exception:
        time.sleep(2)

if server_up:
    print("Server is UP! Running tests...\n")
else:
    print("Server failed to start in time. Please check the loading logs.")
    sys.exit(1)
username = "testuser"
password = "testpassword123!"

def post_json(endpoint, data, token=None):
    url = f"{base_url}{endpoint}"
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code
    except Exception as e:
        return str(e), 500

def get_json(endpoint, token=None):
    url = f"{base_url}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code
    except Exception as e:
        return str(e), 500

print("1. Registering user...")
res, status = post_json("/register", {"username": username, "password": password})
print(f"Status: {status}\nResponse: {res}\n")

print("2. Logging in...")
res, status = post_json("/login", {"username": username, "password": password})
print(f"Status: {status}\nResponse: {res}\n")

if status == 200:
    token = res.get("access_token")
    
    print("3. Adding a task...")
    task_data = {
        "id": 1,
        "text": "Review the project proposal",
        "priority": "auto",
        "status": "pending"
    }
    res, status = post_json("/tasks", task_data, token)
    print(f"Status: {status}\nResponse: {res}\n")
    
    print("4. Getting tasks...")
    res, status = get_json("/tasks", token)
    print(f"Status: {status}\nResponse: {res}\n")
else:
    print("Login failed, skipping further tests.")
