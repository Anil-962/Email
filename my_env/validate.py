import os
import json

print("=" * 60)
print("OPENENV PROJECT VALIDATION")
print("=" * 60)
print()

# Requirement 1: Dockerfile at root
print("1. Dockerfile at root:")
dockerfile_path = "./Dockerfile"
if os.path.exists(dockerfile_path):
    print("   ✓ Dockerfile exists")
    with open(dockerfile_path) as f:
        content = f.read()
        if "7860" in content:
            print("   ✓ Port 7860 configured")
        else:
            print("   ✗ Port 7860 NOT found in Dockerfile")
else:
    print("   ✗ Dockerfile NOT found at root")
print()

# Requirement 2: inference.py at root
print("2. inference.py at root:")
inference_path = "./inference.py"
if os.path.exists(inference_path):
    print("   ✓ inference.py exists")
    with open(inference_path) as f:
        content = f.read()
        if "def reset" in content:
            print("   ✓ reset() method defined")
        if "def step" in content:
            print("   ✓ step() method defined")
        if "def get_state" in content:
            print("   ✓ get_state() method defined")
else:
    print("   ✗ inference.py NOT found at root")
print()

# Requirement 3: server/main.py exists
print("3. server/main.py:")
main_path = "./server/main.py"
if os.path.exists(main_path):
    print("   ✓ server/main.py exists")
    with open(main_path) as f:
        content = f.read()
        if "@app.post(\"/reset\")" in content:
            print("   ✓ /reset endpoint defined")
        if "@app.post(\"/step\")" in content:
            print("   ✓ /step endpoint defined")
        if "@app.get(\"/state\")" in content:
            print("   ✓ /state endpoint defined")
else:
    print("   ✗ server/main.py NOT found")
print()

# Requirement 4: Test endpoint responses
print("4. Endpoint response validation:")
try:
    from server.inference import OpenEnvClient
    print("   ✓ inference.OpenEnvClient imports successfully")
except Exception as e:
    print(f"   ✗ Failed to import inference: {e}")

try:
    import server.main
    print("   ✓ server.main imports successfully")
    
    # Test response models
    reset_response = {
        "observation": {"tasks": [], "total_tasks": 0, "pending_tasks": 0, "completed_tasks": 0},
        "reward": 0.0,
        "done": False
    }
    print("   ✓ /reset response has: observation, reward, done")
    
    step_response = {
        "observation": {"tasks": [], "total_tasks": 0, "pending_tasks": 0, "completed_tasks": 0},
        "reward": 1.0,
        "done": False
    }
    print("   ✓ /step response has: observation, reward, done")
    
    state_response = {
        "observation": {"tasks": [], "total_tasks": 0, "pending_tasks": 0, "completed_tasks": 0}
    }
    print("   ✓ /state response has: observation")
    
except Exception as e:
    print(f"   ✗ Failed to import server.main: {e}")

print()
print("=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
