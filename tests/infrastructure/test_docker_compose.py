import yaml
from pathlib import Path


def test_docker_compose_parses():
    p = Path('config/docker-compose.yml')
    data = yaml.safe_load(p.read_text(encoding='utf-8'))
    assert 'services' in data and isinstance(data['services'], dict)