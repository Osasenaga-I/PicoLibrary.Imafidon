"""
StudentWorker.py
Student worker employee model.
"""
from Employee import Employee
from Log import Log

class StudentWorker(Employee):
    """
    Represents a student employee with academic and supervisor information.
    """
    def __init__(self, name: str, position: str, department: str, email: str, phoneNumber: str,
                 major: str = "", degreeLevel: str = "", supervisor: str = "", available: str = "available"):
        super().__init__(name, position, department, email, phoneNumber, available)
        self.major = major
        self.degreeLevel = degreeLevel
        self.supervisor = supervisor
        Log.i(f"StudentWorker created: {self.name}, supervisor: {self.supervisor}")

    def showInfo(self) -> list:
        """
        Returns display lines for student worker:
        Line 1: Name
        Line 2: Supervisor or major info
        """
        line1 = f"{self.name}"
        line2 = f"Sup: {self.supervisor}" if self.supervisor else f"{self.position}"
        return [line1, line2]
