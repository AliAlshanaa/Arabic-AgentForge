from arabic_agentforge.core import ConversationMemory


def test_add_user_and_assistant_messages():
    memory = ConversationMemory()
    memory.add_user("مرحبا")
    memory.add_assistant("أهلا بك")

    assert memory.to_llm_messages() == [
        {"role": "user", "content": "مرحبا"},
        {"role": "assistant", "content": "أهلا بك"},
    ]


def test_max_messages_trims_oldest_entries():
    memory = ConversationMemory(max_messages=2)
    memory.add_user("one")
    memory.add_assistant("two")
    memory.add_user("three")

    messages = memory.to_llm_messages()
    assert len(messages) == 2
    assert messages[0]["content"] == "two"
    assert messages[1]["content"] == "three"


def test_clear_removes_all_messages():
    memory = ConversationMemory()
    memory.add_user("hello")
    memory.clear()

    assert memory.to_llm_messages() == []
