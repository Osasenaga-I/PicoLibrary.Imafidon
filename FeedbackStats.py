"""
FeedbackStats.py
Tracks customer satisfaction feedback counts and calculates satisfaction statistics
for the Restaurant Satisfaction Kiosk.
"""

class FeedbackStats:
    """
    Manages customer response counters and calculates satisfaction percentages
    and corresponding light strip levels.
    """

    def __init__(self):
        self._happy_count = 0
        self._unhappy_count = 0

    def get_total_count(self) -> int:
        """Returns the total number of feedback responses received."""
        return self._happy_count + self._unhappy_count

    def calculate_percentage(self) -> float:
        """
        Calculates the satisfaction percentage: (happy_count / total_count) * 100.
        Returns 100.0 if no responses have been logged yet to avoid division by zero.
        """
        total = self.get_total_count()
        if total == 0:
            return 100.0
        return (self._happy_count / total) * 100.0

    def get_light_level(self, max_leds: int = 8) -> int:
        """
        Returns the number of LEDs to illuminate on the LightStrip
        proportional to the current satisfaction percentage.
        """
        pct = self.calculate_percentage()
        return round((pct / 100.0) * max_leds)

    def add_happy(self) -> None:
        """Increments the happy customer counter by 1."""
        self._happy_count += 1

    def add_unhappy(self) -> None:
        """Increments the unhappy customer counter by 1."""
        self._unhappy_count += 1

    def reset(self) -> None:
        """Resets both happy and unhappy feedback counters to 0."""
        self._happy_count = 0
        self._unhappy_count = 0
