# Chat history

## Filter message

In some situation you may want to filter the messages before building the prompt, for instance to use RAG. In this case you can subclass `Chat` and override the `filter` method:


```python
from prompts import Chat

class RAGChat(Chat):

    def filter(self):
        filtered_message = []
        for message in filtered_message:
           if message.role == "user"  and "Hi" in message.content:
               filtered_message.append(message)

        return filtered_messages
```
