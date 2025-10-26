from whatsapp_chatter.llm import build_system_prompt, build_user_prompt


def test_build_system_prompt_includes_person_and_context():
    out = build_system_prompt("Charlie", "Loves brief emoji replies.")
    assert "Charlie" in out
    assert "Loves brief emoji replies." in out


def test_build_user_prompt_structure():
    out = build_user_prompt(["hi", "how are you?"])
    assert "Recent chat messages" in out
    assert "hi\nhow are you?" in out
    assert "Respond with one message." in out

