"""Harness failure paths without Docker, providers, or notification sends."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("native_verifier", SCRIPTS / "verify_notification_integration.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def test_docker_has_explicit_bound(monkeypatch):
    def run(args, **kwargs):
        assert kwargs["timeout"] == 7
        raise subprocess.TimeoutExpired(args, 7)
    monkeypatch.setattr(verifier.subprocess, "run", run)
    with pytest.raises(subprocess.TimeoutExpired):
        verifier.docker("exec", "isolated", timeout=7)


def test_docker_error_exposes_code_without_printing_stderr(monkeypatch):
    result = subprocess.CompletedProcess(["docker"], 137, "", "private configuration")
    monkeypatch.setattr(verifier.subprocess, "run", lambda *args, **kwargs: result)
    with pytest.raises(verifier.DockerCommandError) as caught:
        verifier.docker("exec", "isolated")
    assert caught.value.returncode == 137
    assert "private configuration" not in str(caught.value)


@pytest.mark.parametrize("error", [subprocess.TimeoutExpired("docker", 120), KeyboardInterrupt()])
def test_import_failure_keeps_safe_diagnostic(monkeypatch, tmp_path, error):
    def docker(*args, **kwargs):
        if "cat" in args:
            return "secret=DO_NOT_RETAIN\nSuccessfully imported 1 workflow.\n"
        raise error
    monkeypatch.setattr(verifier, "docker", docker)
    report = {"started_monotonic": verifier.time.monotonic()}
    with pytest.raises(type(error)):
        verifier.import_workflow(report, tmp_path, "public")
    diagnostic = (tmp_path / "public_import_diagnostic.json").read_text()
    assert "DO_NOT_RETAIN" not in diagnostic
    assert report["import_diagnostic"]["markers"] == ["Successfully imported 1 workflow."]


def test_import_zero_exit_without_success_is_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(verifier, "docker", lambda *args, **kwargs: "")
    with pytest.raises(RuntimeError, match="IMPORT_FAILED"):
        verifier.import_workflow({"started_monotonic": verifier.time.monotonic()}, tmp_path, "public")


@pytest.mark.parametrize("error,markers,expected", [
    (KeyboardInterrupt(), "", "INTERRUPTED"),
    (subprocess.TimeoutExpired("docker", 120), "", "IMPORT_TIMEOUT"),
    (subprocess.TimeoutExpired("docker", 120), "Successfully imported 1 workflow.", "PROCESS_EXIT_TIMEOUT"),
    (RuntimeError("Docker failed"), "", "IMPORT_FAILED"),
])
def test_failure_cleans_container_and_replaces_pass_explicitly(monkeypatch, tmp_path, error, markers, expected):
    workflow = tmp_path / "workflows/n8n/urbaneats_live.json"
    workflow.parent.mkdir(parents=True)
    workflow.write_bytes((verifier.ROOT / "workflows/n8n/urbaneats_live.json").read_bytes())
    target = tmp_path / "evaluation/results/phase3c3_native_verification.json"
    target.parent.mkdir(parents=True)
    target.write_text('{"result":"PASS"}')
    commands = []
    def docker(*args, **kwargs):
        commands.append(args)
        if "cat" in args:
            return markers
        if "python" in args:
            return "True"
        if any("n8n import:workflow" in arg for arg in args):
            raise error
        return ""
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    monkeypatch.setattr(verifier, "health", lambda: {"status": "READY"})
    monkeypatch.setattr(verifier, "docker", docker)
    with pytest.raises(type(error)):
        verifier.main()
    report = json.loads(target.read_text())
    assert report["result"] == ("INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "FAIL")
    assert report["failure_stage"] == "public workflow import"
    assert report["failure_category"] == expected
    assert "public_workflow_import" not in report
    assert ("rm", "-f", verifier.N8N_TEST) in commands
    assert report["cleanup"]["result"] == "PASS"


def test_unsafe_api_stops_before_disposable_container(monkeypatch, tmp_path):
    monkeypatch.setattr(verifier, "prepare", lambda: (tmp_path, []))
    monkeypatch.setattr(verifier, "health", lambda: {"status": "READY"})
    commands = []
    def docker(*args, **kwargs):
        commands.append(args)
        return "False"
    monkeypatch.setattr(verifier, "docker", docker)
    target = tmp_path / "final.json"
    with pytest.raises(RuntimeError, match="requires API TEST_MODE"):
        verifier.main(target)
    report = json.loads(target.read_text())
    assert report["result"] == "FAIL"
    assert report["failure_stage"] == "API TEST_MODE safety"
    assert all(args[0] != "run" for args in commands)


def test_explicit_result_preserves_historical_pass(monkeypatch, tmp_path):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    historical = tmp_path / "evaluation/results/phase3c3_native_verification.json"
    historical.parent.mkdir(parents=True)
    historical.write_bytes(b'{"result":"PASS"}')
    def interrupt():
        raise KeyboardInterrupt()
    monkeypatch.setattr(verifier, "prepare", interrupt)
    target = historical.with_name("final_native_verification.json")
    with pytest.raises(KeyboardInterrupt):
        verifier.main(target)
    assert historical.read_bytes() == b'{"result":"PASS"}'
    report = json.loads(target.read_text())
    assert report["result"] == "INTERRUPTED"
    assert report["cleanup"]["result"] == "PASS"
