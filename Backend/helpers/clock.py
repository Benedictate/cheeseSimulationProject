from datetime import datetime, timezone

class Clock:
    def now(self, as_string: bool = True):
        current = datetime.now(timezone.utc)
        return current.isoformat() if as_string else current