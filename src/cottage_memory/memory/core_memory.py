import json

from .._db.repositories.core_memory_repo import CoreMemoryRepository


class CoreMemory:
    def __init__(self):
        self._core_memory_repo = CoreMemoryRepository
        self._memories = self._fetch_memories()
        
    def add_memory(self, role: str, key: str, value: str) -> None:
        if not role in ['user', 'agent']:
            raise ValueError(f'Invalid role "{role}"')
        
        result = self._core_memory_repo.add_memory(role, key, value)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._memories = self._fetch_memories()
    
    def get_memories(self) -> dict:
        return self._memories
    
    def delete_memory(self, role: str, key: str) -> None:
        result = self._core_memory_repo.delete_memory(role, key)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._memories = self._fetch_memories()
    
    def undelete_memory(self, role: str, key: str) -> None:
        result = self._core_memory_repo.undelete_memory(role, key)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._memories = self._fetch_memories()
    
    def _fetch_memories(self) -> dict:
        result = self._core_memory_repo.get_memories()
        if result['error'] is not None:
            raise Exception(result['error'])
        
        memories = {role: {} for role in ['user', 'agent']}
        for item in result['data']:
            memories[item['role']][item['key']] = item['value']
            
        return memories
            
