from .._db.repositories.conversations_memory_repo import ConversationsRepository


class ConversationsMemory:
    def __init__(self):
        self._conversations_repo = ConversationsRepository
        self._conversations = self._fetch_conversations()
        
    def get_conversations(self) -> dict:
        return self._conversations
    
    def add_conversation(self, title: str) -> dict:
        result = self._conversations_repo.add_conversation(title)
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
    