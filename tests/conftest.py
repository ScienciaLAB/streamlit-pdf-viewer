# Copyright 2025 Streamlit PDF Component
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from pathlib import Path
from typing import Generator, Any, Dict
from playwright.sync_api import Browser, BrowserContext, Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context with custom settings."""
    # Browser-specific context options
    context_options: Dict[str, Any] = {
        "accept_downloads": True,
        "service_workers": "block"
        if browser.browser_type.name == "chromium"
        else "allow",
    }

    context = browser.new_context(**context_options)

    # Set default timeout for all operations
    context.set_default_timeout(30000)

    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page with error handling."""
    page = context.new_page()

    # Add console message listener for debugging
    def handle_console(msg):
        # Also log console messages from iframes
        if msg.type == "error":
            print(f"[CONSOLE ERROR] {msg.text}")
            if msg.location:
                print(f"  at {msg.location}")
        elif msg.type == "warning":
            print(f"[CONSOLE WARNING] {msg.text}")
        else:
            print(f"[{msg.type}] {msg.text}")

    page.on("console", handle_console)

    # Add page error listener
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    yield page
    page.close()


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "accessibility: marks tests as accessibility tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add extra information to test reports on failure."""
    outcome = yield
    rep = outcome.get_result()

    # Add browser name to test report
    if hasattr(item, "funcargs") and "page" in item.funcargs:
        page = item.funcargs["page"]
        browser_name = page.context.browser.browser_type.name
        rep.browser = browser_name

        # On failure, add more debugging info
        if rep.failed and call.when == "call":
            print(f"\n[FAILED in {browser_name}] Test: {item.name}")
            try:
                # Try to get page title for context
                title = page.title()
                print(f"Page title: {title}")

                # Check if there are any iframes
                frames = page.frames
                print(f"Number of frames: {len(frames)}")

                # Get page URL
                print(f"Page URL: {page.url}")
            except Exception as e:
                print(f"Could not get page info: {e}")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments for PDF testing."""
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {
            "pdfjs.disabled": False,
        }
    }


@pytest.fixture(scope="session")
def default_test_app_file():
    """Default test app file for most tests."""
    return Path(__file__).parent / "streamlit_apps" / "example_zoom_auto.py"


@pytest.fixture(scope="module")
def default_streamlit_app(default_test_app_file):
    """Default streamlit app fixture for tests that use the default test app."""
    with StreamlitRunner(default_test_app_file) as runner:
        yield runner


@pytest.fixture(scope="function")
def default_go_to_app(page: Page, default_streamlit_app: StreamlitRunner):
    """Navigate to the default streamlit app and wait for it to load."""
    page.goto(default_streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


@pytest.fixture(autouse=True, scope="module")
def streamlit_app(default_test_app_file):
    """Streamlit app fixture for tests that use the default test app.

    Tests can override this by defining their own streamlit_app fixture.
    """
    with StreamlitRunner(default_test_app_file) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """Navigate to the streamlit app and wait for it to load.

    Tests can override this by defining their own go_to_app fixture.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()
