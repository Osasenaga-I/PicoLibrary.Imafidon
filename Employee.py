"""
Employee.py
Base domain model for all employee types.
"""
from Log import Log

class Employee:
    """
    Represents a general employee with contact info and manual availability state.
    """
    AVAILABILITY_STATES = ["available", "away", "busy"]

    def __init__(self, name: str, position: str, department: str, email: str, phoneNumber: str, available: str = "available"):
        self.name = name
        self.position = position
        self.department = department
        self.email = email
        self.phoneNumber = phoneNumber
        self._available = available if available in self.AVAILABILITY_STATES else "available"

    def getAvailability(self) -> str:
        """Returns the current availability status string."""
        return self._available

    def showInfo(self) -> list:
        """
        Returns a list of strings formatted for the nameplate display lines.
        """
        return [self.name, self.position]

    def cycleAvailability(self) -> bool:
        """
        Cycles availability through 'available' -> 'away' -> 'busy' -> 'available'.
        Returns True indicating manual cycling succeeded.
        """
        idx = self.AVAILABILITY_STATES.index(self._available) if self._available in self.AVAILABILITY_STATES else 0
        next_idx = (idx + 1) % len(self.AVAILABILITY_STATES)
        self._available = self.AVAILABILITY_STATES[next_idx]
        Log.i(f"Employee {self.name}: availability cycled to {self._available}")
        return True
