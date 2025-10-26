from whatsapp_chatter.contexts import resolve_context_path, load_context


def test_resolve_default_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = resolve_context_path("alice")
    assert p.name == "alice.txt"
    assert p.parent.name == "contexts"


def test_load_missing_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    text = load_context("bob")
    assert text == ""

