import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from facefusion.jobs.job_manager import init_jobs

os.environ['OMP_NUM_THREADS'] = '1'

app = FastAPI()

ROOT_PATH = Path(__file__).resolve().parent.parent
CLI_PATH = ROOT_PATH / 'facefusion.py'


@app.post('/swap')
def swap_face(source: UploadFile = File(...), target: UploadFile = File(...)) -> FileResponse:
        with tempfile.TemporaryDirectory() as workdir:
                source_path = os.path.join(workdir, f"source{os.path.splitext(source.filename or '')[1]}")
                target_path = os.path.join(workdir, f"target{os.path.splitext(target.filename or '')[1]}")
                output_ext = '.mp4' if (target.filename or '').lower().endswith('.mp4') else '.jpg'
                output_path = os.path.join(workdir, f"output{output_ext}")

                with open(source_path, 'wb') as source_file:
                        source_file.write(source.file.read())
                with open(target_path, 'wb') as target_file:
                        target_file.write(target.file.read())

                jobs_path = os.path.join(workdir, 'jobs')
                init_jobs(jobs_path)

                commands = [
                        sys.executable,
                        str(CLI_PATH),
                        'headless-run',
                        '--jobs-path', jobs_path,
                        '--processors', 'face_swapper',
                        '-s', source_path,
                        '-t', target_path,
                        '-o', output_path
                ]
                result = subprocess.run(commands, cwd=ROOT_PATH)
                if result.returncode != 0 or not os.path.exists(output_path):
                        raise HTTPException(status_code=500, detail='Face swap failed')

                media_type = 'video/mp4' if output_ext == '.mp4' else 'image/jpeg'
                return FileResponse(output_path, media_type=media_type, filename=f'swapped{output_ext}')

