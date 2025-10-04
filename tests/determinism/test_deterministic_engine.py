from src.cli_multi_rapid.deterministic_engine import DeterministicEngine


def test_analyze_deterministic_step():
    engine = DeterministicEngine(mode="strict")
    step = {"actor": "code_fixers", "with": {"files": "src/**/*.py"}}
    analysis = engine.analyze_step(step, {"adapter_type": "deterministic"})
    assert analysis.deterministic is True
    assert analysis.issues == []


def test_detect_nondeterministic_params():
    engine = DeterministicEngine(mode="strict")
    step = {"actor": "shell", "with": {"random": True, "cmd": "echo hello"}}
    analysis = engine.analyze_step(step, {"adapter_type": "deterministic"})
    assert analysis.deterministic is False
    assert any("param:random" in i for i in analysis.issues)


def test_detect_time_entropy_in_command():
    engine = DeterministicEngine(mode="strict")
    step = {"actor": "shell", "with": {"command": "date && openssl rand -hex 4"}}
    analysis = engine.analyze_step(step, {"adapter_type": "deterministic"})
    assert analysis.deterministic is False
    assert any("command:time_entropy" in i for i in analysis.issues)
