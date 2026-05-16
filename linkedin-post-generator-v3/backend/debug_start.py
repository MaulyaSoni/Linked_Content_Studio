
import sys
import os

with open("debug_output.txt", "w") as f:
    f.write(f"Python path: {sys.executable}\n")
    f.write(f"Current directory: {os.getcwd()}\n")

    try:
        from app.main import app
        f.write("Successfully imported FastAPI app\n")
    except Exception as e:
        f.write(f"Failed to import app: {e}\n")
        import traceback
        f.write(traceback.format_exc())
