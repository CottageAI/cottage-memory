import json

from ..db.cottage_db import CottageDB


class CoreMemoryRepository:
    dbn = CottageDB()

    @classmethod
    def get_memories(cls) -> dict:
        sql = f'''
SELECT id, role, key, value FROM core_memories
WHERE deleted = 0
ORDER BY role, id;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_memory(cls, role: str, key: str, value: str) -> dict:
        sql = f'''
INSERT INTO core_memories (role, key, value)
VALUES (?, ?, ?)
ON CONFLICT(role, key)
DO UPDATE SET
    value = excluded.value,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now');
'''
        params = (role, key, value)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def delete_memory(cls, role: str, key: str) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 1
WHERE role = ? AND key = ?;
'''
        params = (role, key)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def undelete_memory(cls, role: str, key: str) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 0
WHERE role = ? AND key = ?;
'''
        params = (role, key)
        return cls.dbn.execute_sql(sql, params)
    
    