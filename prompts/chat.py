from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from prompts.templates import template


class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


@dataclass
class Message:
    role: Role
    content: str


class Chat:
    history: List[Message]

    def __init__(self, model_name: str, system_msg: Optional[str] = None):
        self.history = []
        if system_msg is not None:
            self.history.append(Message(Role.system, system_msg))

    def __str__(self):
        """Render the prompt that corresponds to the chat history in the format
        that `model_name` expects.

        In order to be compatible with any library we choose to append the
        token that corresponds to the beginning of the assistant's response
        when the last message is from a `user`.

        How is not adding this token useful anyway?

        This needs to be properly documented.

        I think correctness, i.e. alternation between user and assistant, should
        be checked after filtering the history.

        """
        history = self.filter()
        if not self._is_history_valid(history):
            raise ValueError("History not valid")

        prompt = chat_template[self.model_name](history)

        return prompt

    def filter(self):
        """Filter the messages before building the prompt.

        The `Chat` class should be subclassed by users who want to filter
        messages before building the prompt, and override this method. This
        can for instance use a RAG step.

        (Document)

        """
        return self.history

    def _is_history_valid(self, history):
        raise NotImplementedError

    def __getitem__(self, index: int):
        return self.history[index]

    def __getattribute__(self, role: str):
        """Returns all messages for the role `role`"""
        return [message for message in self.history if message.role == role]

    def user(self, msg: str):
        """Add a new user message."""
        self.history.append(Message(Role.user, msg))

    def assistant(self, msg: str):
        """Add a new assistant message."""

        self.history.append(Message(Role.assistant, msg))


@template
def chat_template(messages):
    """
    {% for message in messages %}
      {%- if loop.index == 0 %}
        {%- if message.role == 'system' %}
          {{- message.content + bos }}\n
        {%- else %}
          {{- bos + user.bein + message.content + user.end }}
        {%- endif %}
      {%- else %}
        {%- if message.role == 'user' %}
            \n{{- user.begin + message.content + user.end }}
        {%- else %}
            \n{{- assistant.begin + message.content + assistant.end }}
        {%- endif %}
      {%- endif %}
    {% endfor %}
    {%- if messages[-1].role == 'user'}
       \n{{ assistant.begin }}
    {% endif %}"""
