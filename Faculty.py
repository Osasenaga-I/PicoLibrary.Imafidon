"""
Faculty.py
Faculty employee model with course assignments and office hours.
"""
from Employee import Employee
from Log import Log

class Faculty(Employee):
    """
    Represents a faculty member.
    """
    def __init__(self, name: str, position: str, department: str, email: str, phoneNumber: str,
                 courseID: list = None, officeHours: dict = None, available: str = "available"):
        super().__init__(name, position, department, email, phoneNumber, available)
        self.courseID = courseID if courseID is not None else []
        self.officeHours = officeHours if officeHours is not None else {}
        Log.i(f"Faculty created: {self.name}, courses: {self.courseID}")

    def showInfo(self) -> list:
        """
        Returns display lines for faculty:
        Line 1: Name and title
        Line 2: Courses list or office hours summary
        """
        line1 = f"{self.name}"
        if self.courseID:
            line2 = f"Courses:{','.join(str(c) for c in self.courseID)}"
        else:
            line2 = f"{self.position}"
        return [line1, line2]
