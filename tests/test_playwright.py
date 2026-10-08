import pytest
import subprocess
import time
import requests
import os
import sys
from playwright.sync_api import Page, expect

@pytest.fixture(scope="module", autouse=True)
def live_server():
    # Get python executable to ensure we use the venv
    python_exe = sys.executable
    process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", "8080"],
    )
    # Wait for the server to be ready
    for _ in range(30):
        try:
            response = requests.get("http://localhost:8080/")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("Live server did not start.")

    yield "http://localhost:8080"

    process.terminate()
    process.wait()

def test_certificate_generation_ui(page: Page, live_server):
    page.goto(f"{live_server}/ui/")
    
    page.fill("#event_name", "Playwright Test Event")
    page.fill("#issue_date", "2026-10-08")
    page.fill("#recipients", "Playwright Tester, tester@example.com, Playwright")
    
    page.click("#submit-btn")
    
    expect(page.locator("#status-card")).to_be_visible()
    expect(page.locator("#job-status-text")).to_have_text("COMPLETED", timeout=10000)
    
    expect(page.locator("#results-card")).to_be_visible()
    expect(page.locator("#job-succeeded")).to_have_text("1")
    
    expect(page.locator("#download-all-btn")).to_be_visible()

