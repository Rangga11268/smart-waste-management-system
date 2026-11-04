"""Root entrypoint for Smart Waste Management System (SWMS) on Cloud Deployments (Railway Railpack)."""

import os
import sys
from pathlib import Path

# Ensure root and backend directories are in sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Expose app object for ASGI servers (uvicorn main:app)
from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
