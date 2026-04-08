from .._db.repositories.conversations_memory_repo import ConversationsRepository


class ConversationsMemory:
    def __init__(self):
        self._conversations_repo = ConversationsRepository
        self._conversations = self._fetch_conversations()
        
    def get_conversations(self) -> list[dict]:
        return self._conversations
    
    def get_title(self, id: int) -> str:
        result = self._conversations_repo.get_title(id)
        if result['error'] is not None:
            raise Exception(result['error'])
        return result['data'][0]['title']
    
    def add_conversation(self, title: str) -> int:
        result = self._conversations_repo.add_conversation(title)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._conversations = self._fetch_conversations()
        return self._conversations[-1][0]
    
    def rename_conversation(self, id: int, new_title: str) -> None:
        result = self._conversations_repo.rename_conversation(id, new_title)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._conversations = self._fetch_conversations()
    
    def delete_conversation(self, id: int) -> None:
        if id == 1:
            print("Cannot delete Default Conversation")
            return
        result = self._conversations_repo.delete_conversation(id)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._conversations = self._fetch_conversations()
    
    def undelete_conversation(self, id: int) -> None:
        result = self._conversations_repo.undelete_conversation(id)
        if result['error'] is not None:
            raise Exception(result['error'])
        self._conversations = self._fetch_conversations()
    
    def _fetch_conversations(self) -> list[dict]:
        result = self._conversations_repo.get_conversations()
        if result['error'] is not None:
            raise Exception(result['error'])
        return result['data']
    