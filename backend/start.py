import sys
import os
import uvicorn

if __name__ == "__main__":
    print("Starting Code Analysis Visualizer Backend...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=9999, reload=True)
