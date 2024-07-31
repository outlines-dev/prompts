import pytest

from prompts.chat import Chat


def test_simple():
    chat = Chat("gpt2", "system message")
    chat.user("new user message")
    chat.assistant("new assistant message")
    print(chat)

    assert chat["assistant"][0].content == "new assistant message"
    assert chat["user"][0].content == "new user message"
    assert chat[1].content == "new user message"


def test_error():
    with pytest.raises(ValueError):
        chat = Chat("gpt2", "system message")
        chat.user("new user message")
        chat.user("new user message")
        print(chat)
