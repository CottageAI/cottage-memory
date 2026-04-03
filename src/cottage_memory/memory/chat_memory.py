import json
from collections.abc import Callable
from typing import Any
from threading import Thread

from .._db.repositories.chat_memory_repo import ChatMemoryRepository


class ChatMemory:
    def __init__(self, max_messages: int, evict_messages: int, conv_id: int=1, 
                 persists: bool=True, summarize_func: Callable[..., Any] | None =None):
        assert evict_messages < max_messages, 'evict_messages must be < max_messages'
        self.max_messages = max_messages
        self.evict_messages = evict_messages
        self.conv_id = conv_id
        self.persists = persists
        self.summarize_func = summarize_func
        
        self._chat_repo = ChatMemoryRepository
        self._messages = self._fetch_messages() if self.persists else []
        
    def add_message(self, message: dict) -> None:
        if message.get('role') is None or message.get('content') is None:
            raise KeyError('Message must contain \'role\' and \'content\' keys')
        if not message['role'] in ['system', 'assistant', 'user', 'tool']:
            raise ValueError(f'"{message['role']}" is invalid role')
        
        if len(self._messages) >= self.max_messages:
            if self.persists:
                self._evict_messages()
            self._messages = self._messages[self.evict_messages:]
        
        if isinstance(message['content'], dict):
            message['content'] = json.dumps(message['content'])
        self._messages.append(message)
        
        if self.persists:
            result = self._chat_repo.add_message(self.conv_id, message)
            if result['error'] is not None:
                self._messages.pop()
                raise Exception(result['error'])
    
    def get_messages(self, filter: list=None) -> list[dict]:
        if filter is not None:
            return [msg for msg in self._messages if msg['role'] in filter]
        else:
            return self._messages
    
    def _evict_messages(self) -> None:
        if self.summarize_func is not None:
            summary_thread = Thread(
                target=self.summarize_func, 
                args=(self._messages[:self.evict_messages],),
                daemon=True
            )
            summary_thread.start()
        
        result = self._chat_repo.evict_messages(self.conv_id, self.evict_messages)
        if result['error'] is not None:
            raise Exception(result['error'])
    
    def _fetch_messages(self) -> list[dict]:
        messages = []
        
        raw_messages = self._chat_repo.get_messages(self.conv_id)
        if raw_messages['error'] is not None:
            raise Exception(raw_messages['error'])
        
        msg_data = raw_messages['data']
        for msg in msg_data:
            if msg['meta_json'] is not None:
                content = json.dumps({
                    'text': msg['content'],
                    'metadata': msg['meta_json']
                })
            else:
                content = msg['content']
                
            message = {
                'role': msg['role'],
                'content': content
            }
            messages.append(message)
        
        return messages
    