import subprocess
import shutil
from pathlib import Path
import pytest


@pytest.mark.skipif(shutil.which('kubeval') is None, reason='kubeval not installed in test env')
def test_k8s_manifests_kubeval(tmp_path: Path):
    # Validate non-Helm raw manifests
    manifests = [
        Path('deploy/k8s/external-secret.yaml'),
        Path('deploy/k8s/networkpolicy.yaml'),
    ]
    for m in manifests:
        assert m.exists()
        res = subprocess.run(['kubeval', str(m)], capture_output=True)
        assert res.returncode == 0, res.stderr.decode()