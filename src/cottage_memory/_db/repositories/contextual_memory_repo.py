import json

from ..db.cottage_db import CottageDB


class ContextualMemoryRepository:
    dbn = CottageDB()
    distance = 'COSINE'
    embed_fn = None
    DIM = 384

    @classmethod
    def _make_vec_blob(cls, text: str):
        emb = cls.embed_fn.encode([text])[0]
        return emb.astype("float32").tobytes()

    @classmethod
    def init_memory(cls, distance='COSINE'):
        cls.distance = distance
        from sentence_transformers import SentenceTransformer
        cls.embed_fn = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        sql = "SELECT vector_quantize('memory_items', 'embedding')"
        result = cls.dbn.execute_sql(sql, use_vectors=True)
        if result['error'] is not None:
            raise Exception(f"Unable to initialize: {result['error']}")
    
    @classmethod
    def add_memory(cls, text: str, conv_id: int | str='all', kind: str="note", source: str=None, 
                   meta: str=None) -> dict:
        if cls.embed_fn is None:
            return {
                'error': 'Contextual memory not initialized. Run init_memory() method.',
                'data': []
            }

        blob = cls._make_vec_blob(text)
        if meta is None:
            meta_json = None
        else:
            meta_json = json.dumps(meta, ensure_ascii=False)

        sql = '''
INSERT INTO memory_items (conversation_id, kind, text, source, meta_json, embedding)
VALUES (?, ?, ?, ?, ?, ?);
'''
        conv_id = None if conv_id == 'all' else conv_id
        params = (conv_id, kind, text, source, meta_json, blob)

        sql_batch = [
            ('BEGIN TRANSACTION;', None),
            (sql, params),
            ("SELECT vector_quantize('memory_items', 'embedding')", None),
            ('COMMIT;', None)
        ]

        result = cls.dbn.execute_sql(
            sql_batch,
            use_vectors=True,
            distance = cls.distance
        )
        return result
    
    @classmethod
    def get_memories(cls, conv_id: int=1, k: int=5):
        if cls.embed_fn is None:
            return {
                'error': 'Contextual memory not initialized. Run init_memory() method.',
                'data': []
            }
            
        sql = '''
SELECT id, text, created_at, meta_json
FROM memory_items
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT ?
'''
        params = (conv_id, k)
        return cls.dbn.execute_sql(sql, params, returns_data=True)
        

    @classmethod
    def query_memories(cls, query: str, k: int=5, kind: str='all', conv_id: int | str='all') -> dict:
        if cls.embed_fn is None:
            return {
                'error': 'Contextual memory not initialized. Run init_memory() method.',
                'data': []
            }

        q_blob = cls._make_vec_blob(query)

        params = [q_blob, k, '%']
        params[2] = '%' if kind == 'all' else kind
        
        where = ''
        if conv_id != 'all':
            where = "AND m.conversation_id = ?"
            params.append(conv_id)

        sql = f'''
SELECT m.id, m.text, m.kind, m.created_at, m.source, m.meta_json, v.distance
FROM memory_items AS m
JOIN vector_quantize_scan('memory_items','embedding', ?, ?) AS v
    ON m.id = v.rowid
WHERE m.kind LIKE ? {where}
ORDER BY v.distance ASC
'''
        result = cls.dbn.execute_sql(
            sql,
            params=tuple(params),
            returns_data=True,
            use_vectors=True,
            distance=cls.distance
        )
        return result
    