"""Launch all three demo apps with one command: python start.py"""
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SERVICES=[('ResolveDesk','support.app:app',8001),('FlowForge','automations.app:app',8002),('Atlas Documents','documents.app:app',8003)]
processes=[]
try:
    print('Starting AI Engineering Portfolio...')
    for name,module,port in SERVICES:
        p=subprocess.Popen([sys.executable,'-m','uvicorn',module,'--host','127.0.0.1','--port',str(port)],cwd=ROOT)
        processes.append(p)
        print(f'  {name:<17} http://127.0.0.1:{port}')
    print('\nOpen those links in your browser. Press Ctrl+C to stop all servers.\n',flush=True)
    while all(p.poll() is None for p in processes):
        time.sleep(.5)
    raise RuntimeError('One of the app servers unexpectedly stopped.')
except KeyboardInterrupt:
    print('\nStopping apps...')
finally:
    for p in processes:
        if p.poll() is None:p.terminate()
    for p in processes:
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill()
