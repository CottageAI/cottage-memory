import json

from ..db.cottage_db import CottageDB


class ChatMemoryRepository:
    dbn = CottageDB()

    @classmethod
    def get_messages(cls, conv_id: int) -> dict:
        sql = f'''
SELECT role, content, meta_json FROM messages
WHERE conversation_id = ?
AND evicted = 0;
'''
        params = (conv_id,)
        results = cls.dbn.execute_sql(sql, params, returns_data=True)
        for result in results['data']:
            if result['meta_json'] is not None:
                result['meta_json'] = json.loads(result['meta_json'])
        return results

    @classmethod
    def add_message(cls, conv_id: int, message: dict) -> dict:
        role = message['role']
        content = message['content']
        if role == 'user' and isinstance(content, dict):
            try:
                meta_json = json.dumps(content['metadata'])
                content = content['text']
            except KeyError:
                return {'error': 'Invalid metadata', 'data': []}
        else:
            meta_json = None

        sql = f'''
INSERT INTO messages (conversation_id, role, content, meta_json)
VALUES (?, ?, ?, ?);
'''
        params = (conv_id, role, content, meta_json)
        return cls.dbn.execute_sql(sql, params)

    @classmethod
    def evict_messages(cls, conv_id: int, count: int) -> dict:
        if count == 0:
            return {'error': None, 'data': []}
        
        sql = f'''
UPDATE messages
SET evicted = 1
WHERE id in (
    SELECT id FROM messages
    WHERE conversation_id = ? 
        AND evicted = 0
        AND role != 'system'
    ORDER BY id ASC
    LIMIT ?
);
''' 
        params = (conv_id, count)
        return cls.dbn.execute_sql(sql, params)
