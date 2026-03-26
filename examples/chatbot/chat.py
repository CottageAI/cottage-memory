from ollama import chat

from chat_memory import ChatMemoryWrapper


class Chat:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.history = ChatMemoryWrapper()

    def generate_response(self, message: str) -> None:
        full_response = ''

        # Add user message to the chat memory
        self.history.append({
            'role': 'user',
            'content': message
        })

        # Build the context with system prompt, retrieved memories, and current chat
        context = self._build_context(message)
        
        response = chat(
            model=self.model_name, 
            messages=context,
            keep_alive=-1,
            options={'temperature': 0.7},
            stream=True
        )
       
        print('Bot: ', end='')
        for chunk in response:
            full_response += chunk.message.content
            print(chunk.message.content, end='', flush=True)
        print('')

        # Add assistant's response to chat memory
        self.history.append({
            'role': 'assistant',
            'content': full_response
        })

    def _build_context(self, message: str) -> list[dict]:
        with open('system_prompt.txt', 'r') as f:
            system_prompt = f.read()

        # This where we inject queried contextual memories into the system prompt
        context = [{
            'role': 'system',
            'content': system_prompt.format(summaries=self.history.query_memories(message)) 
        }]

        # And the current chat context
        context.extend(self.history.get_messages())
        return context


def main():
    model = "llama3.2:1b"
    chat_instance = Chat(model)

    user_message = ''
    while user_message.lower() not in ['goodbye', 'bye']:
        user_message = input('User: ')
        chat_instance.generate_response(user_message)

if __name__ == '__main__':
    main()
