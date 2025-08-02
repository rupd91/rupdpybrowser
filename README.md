# 🧠 `rupdpybrowser`

A flexible Python module built on **Playwright** that allows you to control Chromium (Playwright's bundled or external Chrome/Chromium) with options for persistent profiles, CDP debugging, and human-like automation.

## 📦 Features

- Use **Playwright's bundled Chromium** or specify your **own Chrome/Chromium binary**.
- Support for **persistent browser profiles** (cookie-saving, login-persistent).
- Can **attach to running browser sessions** via CDP (`chrome.exe --remote-debugging-port=9222`).
- Offers utility methods for:
  - Navigating to pages
  - Reading text from page
  - Clicking elements by text or selector
  - Filling inputs and selecting dropdowns
  - Listing interactable elements (buttons, textboxes, links)

---

## 🛠 Installation

### Step 1: Install dependencies

```bash
pip install playwright nest_asyncio
playwright install
```

### Step 2: Install module (editable/development mode)

```bash
git clone https://github.com/yourusername/rupdpybrowser.git
cd rupdpybrowser
pip install -e .
```

> You can also just copy `rupdpybrowser.py` into your working directory if you're not using Git.

---

## 🚀 Quick Start

```python
from rupdpybrowser import BrowserSession

session = BrowserSession()
session.proc_goto("https://example.com")
text = session.proc_readpage()
print(text)
session.close()
```

---

## 🔄 Usage Modes

### 1. **Playwright's Chromium (non-persistent)**

```python
session = BrowserSession()
```

### 2. **Playwright's Chromium (persistent profile)**

```python
session = BrowserSession(userprofile="myprofile")
```

### 3. **External Chrome/Chromium (non-persistent)**

```python
session = BrowserSession(chromium_path=r"C:\Path\To\chrome.exe")
```

### 4. **External Chrome/Chromium with persistent profile**

```python
session = BrowserSession(
    chromium_path=r"C:\Path\To\chrome.exe",
    userprofile="myprofile"
)
```

### 5. **Connect to an existing Chromium session via CDP**

Run Chromium first:

```bash
chrome.exe --remote-debugging-port=9222
```

Then connect:

```python
session = BrowserSession(cdp_url="http://localhost:9222")
```

---

## 🧩 Dictionary-Based Instantiation

```python
params = {
    "chromium_path": r"C:\Path\To\chrome.exe",
    "userprofile": "sessiondata"
}
session = BrowserSession(**params)
```

---

## 🧪 Utilities

### Navigate to URL

```python
session.proc_goto("https://example.com")
```

### Read Page Text

```python
text = session.proc_readpage()
```

### Click an Element

```python
session.proc_click("Login")
session.proc_click("#submit-btn")
```

### Fill an Input or Dropdown

```python
session.proc_edit("input[name='email']", "test@example.com")
session.proc_edit("select#country", "India")
```

### Get Interactable Elements

```python
options = session.proc_getoptions()
for typ, label, selector in options:
    print(f"{typ}: {label} → {selector}")
```

---

## 🧼 Clean Exit

Always close sessions after use:

```python
session.close()
```

---

## 📍 Notes

- Playwright downloads its own Chromium:  
  `%USERPROFILE%\AppData\Local\ms-playwright\`
  
- External Chromium must support CDP (`--remote-debugging-port`).

- You can use `nest_asyncio` to run this inside Jupyter/IPython:
  
  ```python
  import nest_asyncio
  nest_asyncio.apply()
  ```

---

## 📄 License

MIT License