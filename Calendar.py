"""
Calendar.py
Calendar class representing an automated schedule for an administrator.
"""
from Log import Log

class Calendar:
    """
    Manages calendar events and provides automatic availability status.
    """
    def __init__(self, events=None):
        self._events = events if events is not None else []
        Log.i(f"Calendar initialized with {len(self._events)} events")

    def getStatus(self) -> str:
        """
        Determines current availability status based on events.
        Returns 'busy' if an active event exists; otherwise 'available'.
        """
        if self._events:
            first = self._events[0]
            if isinstance(first, dict) and "status" in first:
                return first["status"]
            elif isinstance(first, str):
                return first
            return "busy"
        return "available"

    def addEvent(self, event):
        """Adds an event to the calendar."""
        self._events.append(event)
