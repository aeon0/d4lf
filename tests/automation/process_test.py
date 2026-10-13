from src.automation import process as _process


def test_safe_exit_delegates_to_process_exit(monkeypatch) -> None:
    called = []
    monkeypatch.setattr(_process.psutil, "process_iter", lambda *_args: [])
    monkeypatch.setattr(_process.time, "sleep", lambda *_args: None)
    monkeypatch.setattr(_process.os, "_exit", called.append)
    _process.safe_exit(7)
    assert called == [7]
