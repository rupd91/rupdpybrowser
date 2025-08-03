# rupdpybrowser

A lightweight Python wrapper for controlling Chromium browsers using Playwright and the Chrome DevTools Protocol (CDP). Supports both Playwright’s built-in Chromium and external Chromium instances with persistent profiles.

## Installation

```bash
# Install Chromium (ungoogleled)
winget install --id=eloston.ungoogled-chromium -e

# Install dependencies
pip install playwright
playwright install
pip install psutil pywin32
```

## Usage

### Starting a Session

```python
from rupdpybrowser import BrowserSessionStart

# 1. Playwright's Chromium | Non-Persistent
session = BrowserSessionStart()

# 2. External Chromium with profile
session = BrowserSessionStart(
    chromium_path='C:/Path/To/Chromium/chrome.exe',
    userprofile='rupdpybrowser'
)

# 3. Connect using dictionary
params = {
    'chromium_path': 'C:/Path/To/Chromium/chrome.exe',
    'userprofile': 'rupdpybrowser'
}
session = BrowserSessionStart(**params)
```

## Functions

### Page Navigation

```python
session.proc_goto("https://example.com")
```

### Text Reading

```python
text = session.proc_readtext()               # Reads full body
text = session.proc_readtext("elementID")    # Reads specific element
```

### Click / Edit Elements

```python
session.proc_click("Submit")        # Click by text
session.proc_click("#submitBtn")    # Click by selector

session.proc_edit("#username", "rahul")
session.proc_edit("select#state", "Michigan")
```

### Option Extraction

```python
options = session.proc_getoptions("Login")
for opt in options:
    print(opt)
```

## Managing Browser Sessions

### Check Running Chromium Instances

```python
from rupdpybrowser import BrowserSessionInfo
BrowserSessionInfo()
```

### Close a Chromium Session

```python
from rupdpybrowser import BrowserSessionClose
BrowserSessionClose(9225)
```

### Hide or Show Chromium Windows

```python
from rupdpybrowser import BrowserSessionSetVisibility

# Hide
BrowserSessionSetVisibility(9225, hide=True)

# Show
BrowserSessionSetVisibility(9225, hide=False)
```

## Notes

- External Chromium must be launched with `--remote-debugging-port` enabled.
- Persistent profiles allow login sessions and browser state to be retained.
- Set `headlessmethod=True` if using default Playwright mode and want background execution.

