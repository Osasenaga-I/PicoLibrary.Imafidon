# Implementation Plan: MicroPython Dynamic Nameplate

This plan outlines the architecture, file organization, class responsibilities, and build order for implementing the digital office nameplate on the Raspberry Pi Pico based on the final UML class diagram.

---

## 1. Hardware Pin Configuration

Based on your physical wiring:
* **LCDDisplay (I2C):** SDA = GP0, SCL = GP1
* **Next Button:** GP20
* **Previous Button:** GP21
* **Availability Button:** GP22
* **Passive Buzzer:** GP16
* **LightStrip (NeoPixel):** GP2 (8 LEDs, 50% brightness)

---

## 2. File Organization

Each class resides in its own `.py` file, matching the UML diagram exactly:

| File Name | Class | Description |
| :--- | :--- | :--- |
| `Calendar.py` | `Calendar` | Holds a schedule/event list and provides automatic availability status. |
| `Employee.py` | `Employee` | Base domain model for employees; manages general attributes and manual availability cycling. |
| `Faculty.py` | `Faculty` | Subclass of `Employee`; adds courses and office hours. |
| `Staff.py` | `Staff` | Subclass of `Employee`; adds walk-in acceptance status. |
| `Administrator.py` | `Administrator` | Subclass of `Employee`; composes `Calendar` to provide automatic availability. |
| `StudentWorker.py` | `StudentWorker` | Subclass of `Employee`; adds major, degree level, and supervisor. |
| `NamePlateView.py` | `NamePlateView` | Aggregates `LCDDisplay`, `PassiveBuzzer`, and `LightStrip`; manages hardware rendering and feedback. |
| `NamePlate.py` | `NamePlate` | Controller coordinating the current employee, button input callbacks, and view updates. |
| `main.py` | *(Script)* | Instantiates all hardware, models, view, and controller, then runs the main event loop. |

---

## 3. Class Specifications & UML Alignment

### A. Model Layer

#### `Calendar` (`Calendar.py`)
* **Attributes:**
  * `-events : list` — List of calendar entries/events.
* **Methods:**
  * `+getStatus() : string` — Evaluates current events and returns `"available"`, `"away"`, or `"busy"`.

#### `Employee` (`Employee.py`)
* **Attributes:**
  * `+name : string`
  * `+position : string`
  * `+department : string`
  * `+email : string`
  * `+phoneNumber : string`
  * `-available : string` — Holds `"available"`, `"away"`, or `"busy"`. Default: `"available"`.
* **Methods:**
  * `+getAvailability() : string` — Returns current availability string.
  * `+showInfo() : list` — Returns list of text strings formatted for display lines.
  * `+cycleAvailability() : bool` — Cycles through `"available" -> "away" -> "busy" -> "available"` and returns `True`.

#### `Faculty` (`Faculty.py` inherits `Employee`)
* **Attributes:**
  * `+courseID : list`
  * `+officeHours : dict`
* **Methods:**
  * `+showInfo() : list` — Overrides to include course/faculty details.

#### `Staff` (`Staff.py` inherits `Employee`)
* **Attributes:**
  * `-walkInAcceptance : bool`
* **Methods:**
  * `+showInfo() : list` — Overrides to include walk-in acceptance status.

#### `Administrator` (`Administrator.py` inherits `Employee`)
* **Composition:**
  * Owns 1 `Calendar` instance (`self._calendar`).
* **Methods:**
  * `+getAvailability() : string` — Queries `self._calendar.getStatus()`.
  * `+showInfo() : list` — Overrides to show administrator office details.
  * `+cycleAvailability() : bool` — Returns `False` because availability is automatic.

#### `StudentWorker` (`StudentWorker.py` inherits `Employee`)
* **Attributes:**
  * `+major : string`
  * `+degreeLevel : string`
  * `+supervisor : string`
* **Methods:**
  * `+showInfo() : list` — Overrides to display major and supervisor details.

---

### B. View Layer

#### `NamePlateView` (`NamePlateView.py`)
* **Attributes:**
  * `-display : LCDDisplay`
  * `-buzzer : PassiveBuzzer`
  * `-lightStrip : LightStrip`
* **Methods:**
  * `+render(lines : list)` — Clears and displays lines of text on the LCD.
  * `+showAvailability(status : string)` — Sets `LightStrip` color based on status:
    * `"available"` -> Green
    * `"away"` -> Yellow / Orange
    * `"busy"` -> Red
  * `+playSound()` — Beeps the passive buzzer (short chime for button navigation).

---

### C. Controller Layer

#### `NamePlate` (`NamePlate.py`)
* **Attributes:**
  * `-employees : Employee[]` (list of `Employee` instances)
  * `-currentEmployee : int` (current index)
  * `-buttons : Button[]` (list of 3 `Button` instances)
  * `-view : NamePlateView`
* **Methods:**
  * `+previousEmployee()` — Decrements index (wraps around), updates view, plays sound.
  * `+nextEmployee()` — Increments index (wraps around), updates view, plays sound.
  * `+cycleAvailability()` — Invokes `cycleAvailability()` on the current employee. If `True`, updates view availability; if `False`, can trigger rejection sound.
  * `+buttonPressed(name : string)` — Dispatches to `nextEmployee()`, `previousEmployee()`, or `cycleAvailability()` based on the button's name.
  * `+buttonReleased(name : string)` — Optional release handler hook.

---

### D. Main Program (`main.py`)
* Initializes:
  * `LCDDisplay(sda=0, scl=1)`
  * `PassiveBuzzer(pin=16, name="NavBuzzer")`
  * `LightStrip(pin=2, name="StatusStrip", numleds=8, brightness=0.5)`
  * `NamePlateView(display, buzzer, lightstrip)`
  * Sample domain instances: `Faculty`, `Staff`, `Administrator` (with `Calendar`), and `StudentWorker`.
  * `Button` instances for Next (GP20, name="next"), Previous (GP21, name="previous"), and Availability (GP22, name="availability").
  * `NamePlate(employees, buttons, view)`.
* Triggers initial display of employee 0.
* Runs the event loop keeping interrupts active.

---

## 4. Build Order

1. **`Calendar.py`** — Independent domain utility.
2. **`Employee.py`** — Base class for all employees.
3. **`Faculty.py`**, **`Staff.py`**, **`Administrator.py`**, **`StudentWorker.py`** — Subclasses of `Employee`.
4. **`NamePlateView.py`** — Presentation layer interfacing with `LCDDisplay`, `PassiveBuzzer`, and `LightStrip`.
5. **`NamePlate.py`** — Controller coordinating models, view, and button callbacks.
6. **`main.py`** — Setup script wiring all components together.
