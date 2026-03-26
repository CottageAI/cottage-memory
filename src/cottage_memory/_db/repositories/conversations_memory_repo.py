import json

from ..db.cottage_db import CottageDB


class ConversationsRepository:
    dbn = CottageDB()
   
    @classmethod
    def get_conversations(cls) -> dict:
        sql = '''
SELECT id, title FROM conversations
WHERE deleted = 0
ORDER BY id DESC;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_conversation(cls, title: str) -> dict:
        sql = f'''
INSERT INTO conversations (title)
VALUES (?);
'''
        params = (title,)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def delete_conversation(cls, id: int) -> dict:
        sql = f'''
UPDATE conversations
SET deleted = 1
WHERE id = ?
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def undelete_conversation(cls, id: int) -> dict:
        sql = f'''
UPDATE conversations
SET deleted = 0
WHERE id = ?
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)
