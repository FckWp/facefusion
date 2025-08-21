import subprocess

import pytest
from fastapi.testclient import TestClient

from facefusion.api import app
from facefusion.download import conditional_download
from .helper import get_test_example_file, get_test_examples_directory

client = TestClient(app)


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
        conditional_download(get_test_examples_directory(),
        [
                'https://github.com/facefusion/facefusion-assets/releases/download/examples-3.0.0/source.jpg',
                'https://github.com/facefusion/facefusion-assets/releases/download/examples-3.0.0/target-240p.mp4'
        ])
        subprocess.run([ 'ffmpeg', '-i', get_test_example_file('target-240p.mp4'), '-vframes', '1', get_test_example_file('target-240p.jpg') ])


def test_swap_face() -> None:
        with open(get_test_example_file('source.jpg'), 'rb') as source, open(get_test_example_file('target-240p.jpg'), 'rb') as target:
                files = {
                        'source': ('source.jpg', source, 'image/jpeg'),
                        'target': ('target-240p.jpg', target, 'image/jpeg')
                }
                response = client.post('/swap', files = files)
        assert response.status_code == 200
        assert response.content


def test_preview_face() -> None:
        with open(get_test_example_file('source.jpg'), 'rb') as source, open(get_test_example_file('target-240p.mp4'), 'rb') as target:
                files = {
                        'source': ('source.jpg', source, 'image/jpeg'),
                        'target': ('target-240p.mp4', target, 'video/mp4')
                }
                response = client.post('/preview', params = { 'frame': 0 }, files = files)
        assert response.status_code == 200
        assert response.content

