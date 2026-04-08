# test_env.py
import subprocess
import time
import sys
import threading
import urllib.request

# Start the server
def run_server():
    from my_env.server.app import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

print("Waiting for server to start...")
time.sleep(3) # allow uvicorn to bind

print("Testing server...")
try:
    from openenv.core.client_types import StepResult
    from openenv.core import EnvClient
    
    # Check if HTTP is up
    req = urllib.request.Request("http://127.0.0.1:8005/docs")
    try:
        urllib.request.urlopen(req)
        print("Server is UP at http://127.0.0.1:8005!")
    except Exception as e:
        print("Could not reach /docs -", e)

    # We will test the basic client logic directly
    print("Testing MyEnvironment locally...")
    from my_env.server.my_env_environment import MyEnvironment
    from my_env.models import MyAction, MyObservation
    
    env = MyEnvironment()
    obs = env.reset()
    print("Initial observation:", obs.echoed_message)
    
    action = MyAction(message="Testing OpenEnv!")
    obs = env.step(action)
    print("Action observation:", obs.echoed_message)
    print("Reward for action:", obs.reward)
    
    print("Local tests passed!")
except Exception as e:
    print("Test failed with exception:", e)
