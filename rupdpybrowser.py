# -----------------------------------------------------------------------------------------------------------------------------------
# winget install --id=eloston.ungoogled-chromium -e
# pip install playwright
# playwright install
# -----------------------------------------------------------------------------------------------------------------------------------
# session = BrowserSession()                                            # Playwright's Chromium | Non-Persistent
# session = BrowserSession(userprofile='rupdpybrowser')                 # Playwright's Chromium | 
# session = BrowserSession(chromium_path='..\location\chrome.exe')      # External Chromium | Non-Persistent
# session = BrowserSession(chromium_path,cookiebox)                     # External Chromium | Persistent 
# session = BrowserSession(**parameters)                                # External Chromium | Persistent | USE DICTIONARY
# -----------------------------------------------------------------------------------------------------------------------------------


import os
import time
import socket
import subprocess
import requests
import psutil
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
import nest_asyncio

import psutil
import win32gui
import win32con
import win32process
nest_asyncio.apply()


class BrowserSessionStart:
    def _is_cdp_alive(self):
        try:
            with socket.create_connection(("localhost", self.port), timeout=1):
                return True
        except:
            return False

    def __init__(
        self,
        headlessmethod=False,
        userprofile=None,
        cdp_url=None,
        cdp_port=None,
        chromium_path=None
    ):
        self.page = None
        self.browser = None
        self.context = None
        self.port = int(cdp_port) if cdp_port else 9222
        self.cdp_url = cdp_url or f"http://localhost:{self.port}"
        self.chromium_path = chromium_path
        self.userprofile = str(Path(__file__).parent / userprofile) if userprofile else None

        self.playwright = sync_playwright().start()
        self.launcher = self.playwright.chromium

        if chromium_path:
            if not self._is_cdp_alive():
                self._launch_real_chromium()
                self._wait_for_cdp()
            else:
                print(f"#. Reusing Chromium at {self.cdp_url}")
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()

        elif self.userprofile and self.chromium_path:
            print(f"#. Connecting to external Chromium with profile: {self.userprofile}")

            if not self._is_cdp_alive():
                self._launch_real_chromium()
                self._wait_for_cdp()

            self.browser = self.launcher.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()


        else:
            print("#. Start Default Chromium (non-persistent)")
            self.browser = self.launcher.launch(headless=headlessmethod)
            self.context = self.browser.new_context(ignore_https_errors=True)

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

        print(f"#. Session ID: {id(self)}")
        print(f"#. CDP Port: {self.port}")
        print(f"#. CDP URL: {self.cdp_url}")
        print(f"#. Profile: {self.userprofile or 'None'}")

    def _launch_real_chromium(self):
            print(f"Launching external Chromium: {self.chromium_path} --remote-debugging-port={self.port}")
            user_data_dir = self.userprofile or "C:/Temp/ExternalChromeProfile"

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6  # 6 = SW_MINIMIZE

            subprocess.Popen([
                self.chromium_path,
                f"--remote-debugging-port={self.port}",
                "--no-first-run",
                "--no-default-browser-check",
                f"--user-data-dir={user_data_dir}",
                "--app=data:text/html,<title>Ready</title>",
                "--disable-background-mode"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
               startupinfo=si)

    def _wait_for_cdp(self, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.create_connection(("localhost", self.port), timeout=1):
                    print("CDP connection available.")
                    return
            except:
                time.sleep(0.5)
        raise TimeoutError(f"CDP port {self.port} not available after {timeout} seconds.")

    def proc_readtext(self, element_id=None):
        if not self.page:
            raise Exception("No active page. Use proc_goto() or proc_start() first.")
        selector = f"#{element_id}" if element_id else "body"
        return self.page.inner_text(selector)

    def proc_goto(self, url):
            if self.context:
                    new_page = self.context.new_page()
                    new_page.goto(url)
                    self.page = new_page
                    return new_page
            else:
                    raise Exception("Session not started. Call proc_start() first.")

    def proc_click(self, selector_or_text):
            if not self.page:
                    raise Exception("No active page found. Call proc_goto() first.")
            
            if not selector_or_text.startswith(('#', '.', '[', 'text=', 'button', '//')):
                    selector_or_text = f"text={selector_or_text.strip()}"
            
            self.page.click(selector_or_text)

    def proc_edit(self, selector, text):
            if not self.page:
                    print("Error: Page is not initialized")
                    return
            try:
                    self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    tag_name = self.page.evaluate("el => el.tagName.toLowerCase()", self.page.locator(selector).element_handle())
                    
                    if tag_name in ["input", "textarea"]:
                            self.page.click(selector)
                            self.page.fill(selector, text)
                    
                    elif tag_name == "select":
                            # First, get all options
                            options = self.page.query_selector_all(f"{selector} option")
                            value_matched = None
                            label_matched = None
                            for option in options:
                                    value = self.page.evaluate("(el) => el.value", option)
                                    label = self.page.evaluate("(el) => el.textContent.trim()", option)
                                    if value == text:
                                            value_matched = value
                                            break
                                    if label == text:
                                            label_matched = label

                            if value_matched:
                                    self.page.select_option(selector, value=value_matched)
                            elif label_matched:
                                    self.page.select_option(selector, label=label_matched)
                            else:
                                    print(f"Error: No matching option found for '{text}' in {selector}")

                    else:
                            self.page.click(selector)
                            option_selector = f"{selector} ~ div, {selector} + div, {selector} ul li, div[role='option']:text('{text}')"
                            self.page.wait_for_selector(option_selector, state="visible", timeout=2000)
                            self.page.click(option_selector)

            except Exception as e:
                    print(f"Error updating element {selector}: {e}")


    def close(self):
            if self.browser:
                    self.browser.close()
            if self.playwright:
                    self.playwright.stop()
                    
    def proc_getoptions(self, text=None):
            if not self.page:
                    raise Exception("No active page found. Call proc_goto() first.")

            results = []
            export_lines = []

            def get_css_selector(element):
                    try:
                            selector = element.evaluate("""
                                    (el) => {
                                            function getNthChildIndex(node) {
                                                    let index = 1;
                                                    while (node.previousElementSibling) {
                                                            node = node.previousElementSibling;
                                                            index++;
                                                    }
                                                    return index;
                                            }

                                            function getPath(el) {
                                                    let path = [];
                                                    while (el && el.tagName.toLowerCase() !== 'body') {
                                                            let tag = el.tagName.toLowerCase();
                                                            let index = getNthChildIndex(el);
                                                            let selectorPart = index > 1 || el.nextElementSibling || el.previousElementSibling
                                                                    ? tag + ":nth-child(" + index + ")"
                                                                    : tag;
                                                            path.unshift(selectorPart);
                                                            el = el.parentElement;
                                                    }
                                                    path.unshift('body');
                                                    return path.join(' > ');
                                            }

                                            return getPath(el) || 'body';
                                    }
                            """)
                            return selector or 'body'
                    except Exception as e:
                            print(f"Error generating selector: {e}")
                            return None

            # BUTTONS
            buttons = self.page.query_selector_all("button")
            for btn in buttons:
                    btn_text = btn.inner_text().strip() if btn else ""
                    btn_id = btn.get_attribute("id") or ""
                    if text is None or (text.lower() in btn_text.lower()) or (text.lower() in btn_id.lower()):
                            selector = get_css_selector(btn)
                            if selector:
                                    results.append(("BUTTON", btn_text, selector))
                                    export_lines.append(f"BUTTON: TEXT='{btn_text}' SELECTOR='{selector}'")

            # TEXTBOXES
            inputs = self.page.query_selector_all("input[type='text'], textarea")
            for inp in inputs:
                    value = inp.get_attribute("value") or ""
                    placeholder = inp.get_attribute("placeholder") or ""
                    inp_id = inp.get_attribute("id") or ""
                    label = placeholder or value or inp_id
                    if text is None or (text.lower() in label.lower()):
                            selector = get_css_selector(inp)
                            if selector:
                                    results.append(("TEXTBOX", label, selector))
                                    export_lines.append(f"TEXTBOX: PLACEHOLDER='{placeholder}' VALUE='{value}' SELECTOR='{selector}'")

            # LINKS
            links = self.page.query_selector_all("a")
            for a in links:
                    link_text = a.inner_text().strip()
                    href = a.get_attribute("href") or ""
                    if text is not None and (text.lower() in link_text.lower() or text.lower() in href.lower()):
                            selector = get_css_selector(a)
                            if selector:
                                    results.append(("LINK", link_text or href, selector))
                                    export_lines.append(f"LINK: TEXT='{link_text}' HREF='{href}' SELECTOR='{selector}'")

            # Print and export
            # with open("clickable_elements.txt", "w", encoding="utf-8") as f:
                    # f.write("\n".join(export_lines))

            return results
            
 

def BrowserSessionClose(target_port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline'] or []
            if any('chrome' in part.lower() for part in cmdline):
                for arg in cmdline:
                    if f'--remote-debugging-port={target_port}' in arg and '--type=renderer' not in cmdline:
                        print(f"#. Killing main Chromium PID {proc.pid} on port {target_port}")
                        proc.kill()
                        return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    print("#. No Chromium main process found with given port.")


def BrowserSessionInfo():
    results = []
    pattern = re.compile(r"--remote-debugging-port=(\d+)")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'] or ''
            cmdline = proc.info['cmdline'] or []
            if 'chrome' in name.lower():
                cmd_str = ' '.join(cmdline)
                match = pattern.search(cmd_str)
                if match:
                    port = int(match.group(1))
                    results.append((proc.pid, port, cmd_str))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    for pid, port, cmd in results:
        print(f"#. PID: {pid} | Port: {port} | CMD: {cmd}\n\n")
    


def BrowserSessionSetVisibility(target_port, hide=True):
    target_pids = []

    # Gather all PIDs using the target port
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline'] or []
            if any('chrome' in part.lower() for part in cmdline):
                for arg in cmdline:
                    if f'--remote-debugging-port={target_port}' in arg:
                        target_pids.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not target_pids:
        print("#. No Chromium processes found with that port.")
        return

    print(f"#. Found Chromium PIDs on port {target_port}: {target_pids}")

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in target_pids:
            title = win32gui.GetWindowText(hwnd)
            if not title.strip():
                return
            if hide:
                print(f"#. Hiding window: {title} (PID: {pid})")
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            else:
                print(f"#. Restoring window: {title} (PID: {pid})")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.BringWindowToTop(hwnd)

    win32gui.EnumWindows(enum_handler, None)