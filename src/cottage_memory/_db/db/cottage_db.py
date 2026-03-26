from contextlib import contextmanager
import sqlite3
import importlib.resources

from ..util.db_path_config import read_db_path

class CottageDB:
    def __init__(self):
        db = read_db_path()
        self.db_path = db
        self.ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"

    @contextmanager
    def _conn(self, use_vectors: bool=False, distance: str='COSINE'):
        conn = sqlite3.connect(self.db_path)  # default check_same_thread=True is fine here
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")  # wait for locks instead of instantly failing
            conn.execute("PRAGMA journal_mode = WAL;")   # better concurrency (one writer, many readers)

            if use_vectors:
                conn.enable_load_extension(True)
                conn.load_extension(str(self.ext_path))
                conn.enable_load_extension(False)
                
                opts = f"distance={distance},type=FLOAT32,dimension=384"
                conn.execute(
                    "SELECT vector_init('memory_items', 'embedding', ?)",
                    (opts,)
                )

            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_sql(self, sql_batch: str | list[str], params: tuple=None, 
                    returns_data: bool=False, use_vectors: bool=False, 
                    distance: str='COSINE') -> dict:
        if self.db_path is None:
            raise NotImplementedError('DB has not been initialized')
        if not isinstance(sql_batch, list):
            sql_batch = [(sql_batch, params)]

        data = []
        error = None

        with self._conn(use_vectors=use_vectors, distance=distance) as CONN:
            CONN.row_factory = sqlite3.Row
            cursor = CONN.cursor()

            try:
                for sql, params in sql_batch:
                    if params is None:
                        result = cursor.execute(sql)
                    else:
                        result = cursor.execute(sql, params)
        
            except Exception as err:
                error = str(err)
                CONN.rollback()
                return {'error': error, 'data': []}

            if returns_data:
                if len(sql_batch) > 1:
                    error = 'SELECT statements must be singular'
                else:
                    rows = result.fetchall()
                    data = [dict(row) for row in rows]
        return {'data': data, 'error': error}
    