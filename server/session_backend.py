from django.contrib.sessions.backends.db import SessionStore as DbSessionStore
from contextlib import contextmanager

class SessionStore(DbSessionStore):
    def __init__(self, session_key: str | None = ...) -> None:
        super().__init__(session_key)
        self.enable_flush = True

    def cycle_key(self):
        pass

    def flush(self):
        if self.enable_flush:
            super().flush()


@contextmanager
def no_flushing_section(session: SessionStore):
    try:
        session.enable_flush = False
        yield
    finally:
        session.enable_flush = True