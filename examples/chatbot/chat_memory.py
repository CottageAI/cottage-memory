from ollama import chat
import json

from cottage_memory import ChatMemory, ContextualMemory, Memory


class ChatMemoryWrapper:
    def __init__(self, max_messages: int=40, evict_messages: int=10):
        # Instantiate the ChatMemory class and inject parameters, including function
        # to summarize and store older messages in contextual memory
        self.chat_memory = ChatMemory(max_messages, evict_messages, summarize_func=self._summarize_messages)

        self.context_memory = ContextualMemory()

        # Needs to be run before ContextualMemory object can be used
        self.context_memory.init_memory()

    def get_messages(self) -> list[dict]:
        return self.chat_memory.get_messages()
    
    def query_memories(self, query:str, k:int = 5) -> str:
        # Query contextual memories
        memories = self.context_memory.query_memories(query, k=k, kind=None)
        return '\n\n'.join([item['data'].text for item in memories])
    
    def append(self, message) -> None:
        self.chat_memory.add_message(message)

    def _summarize_messages(self, messages: list[dict]) -> None:
        # This is the function called from ChatMemory before evicting older messages
        summary = self._generate_summary(messages)
        self.context_memory.add_memory(Memory(summary, kind='summary'))

    def _generate_summary(self, messages: list[dict]) -> str:
        # Has the LLM summarize the messages marked for eviction
        messages_text = '\n'.join(f"{msg['role']}: {msg['content']}" for msg in messages)
        prompt = f"""
    Summarize the following conversation:

    ```{messages_text}```

    Be detailed, but return only the summary text.
    """ 
        response = chat(
            model="llama3.2:1b", 
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            keep_alive=-1,
            options={'temperature': 0.7}
        )
        return response.message.content


