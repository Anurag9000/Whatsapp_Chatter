from __future__ import annotations

import time
from typing import List, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def build_driver(headless: bool = False, user_data_dir: str | None = None):
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
    driver = webdriver.Chrome(options=options)
    return driver


def open_whatsapp(driver) -> None:
    driver.get("https://web.whatsapp.com/")
    # Wait for either the search box or the chat composer to appear
    WebDriverWait(driver, 180).until(
        EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[title='Search input textbox']")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']")),
        )
    )


def select_contact(driver, name: str) -> None:
    # Try multiple selectors for the search box
    search_selectors = [
        "[title='Search input textbox']",
        "div[contenteditable='true'][data-tab='3']",
        "div[contenteditable='true'][data-tab='4']",
        "div[contenteditable='true'][role='textbox']",
        "header [contenteditable='true']",
    ]
    search = None
    for sel in search_selectors:
        try:
            search = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            if search:
                break
        except Exception:
            continue
    if not search:
        raise RuntimeError("Could not find WhatsApp search box. UI may have changed.")

    try:
        search.clear()
    except Exception:
        pass
    search.send_keys(name)
    time.sleep(1.2)
    search.send_keys(Keys.ENTER)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"))
    )


def read_recent_messages(driver, limit: int = 10) -> List[str]:
    msgs = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    texts: List[str] = []
    for m in msgs[-limit:]:
        # Nested text spans vary over time; get visible text is robust.
        txt = m.text.strip()
        if txt:
            texts.append(txt)
    return texts


def read_all_messages(driver) -> List[str]:
    msgs = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    texts: List[str] = []
    for m in msgs:
        txt = m.text.strip()
        if txt:
            texts.append(txt)
    return texts


def read_last_message(driver) -> Tuple[str, str] | None:
    """Return (direction, text) for the last message.

    direction: 'in' for received, 'out' for sent. Returns None if not found.
    """
    msgs = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    if not msgs:
        return None
    last = msgs[-1]
    txt = last.text.strip()
    if not txt:
        return None
    direction = 'in' if 'message-in' in last.get_attribute('class') else 'out'
    return (direction, txt)


def _find_composer(driver):
    selectors = [
        "footer div[contenteditable='true'][role='textbox']",
        "div[role='textbox'][contenteditable='true']",
        "div.selectable-text.copyable-text[contenteditable='true']",
        "div[contenteditable='true'][data-tab='10']",
    ]
    for sel in selectors:
        try:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            if el:
                return el
        except Exception:
            continue
    raise RuntimeError("Could not find message composer. UI may have changed.")


def send_message(driver, text: str) -> None:
    # Ensure chat pane is active
    try:
        chat_pane = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-viewport-element='chat']"))
        )
        chat_pane.click()
    except Exception:
        pass

    box = _find_composer(driver)
    box.click()
    box.clear() if hasattr(box, 'clear') else None
    box.send_keys(text)
    box.send_keys(Keys.ENTER)
