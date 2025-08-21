#!/usr/bin/env python3

import os

os.environ['OMP_NUM_THREADS'] = '1'

from facefusion.api import app

if __name__ == '__main__':
        import uvicorn
        uvicorn.run(app, host = '0.0.0.0', port = 8000)

