import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

# Run the same commands as in your GitHub Actions file
commands = [
    "pip install -r requirements.txt -r requirements-dev.txt",
    "coverage erase",
    "coverage run -m pytest tests/ -v",
    "coverage report -m",
    "coverage xml"
]

for cmd in commands:
    if not run_command(cmd):
        print("Failed!")
        sys.exit(1)

print("All tests passed locally!")