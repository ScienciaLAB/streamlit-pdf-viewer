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

"""E2E regression test for streamlit/streamlit#14917.

When an ``st.dialog`` opened from a custom component is closed, the parent page
scroll (``section[data-testid="stMain"]``) must be preserved.

Measured behaviour of this exact scenario (click a page-2 annotation, which scrolls
the page down, then close the dialog) across Streamlit versions:
 - <= 1.40.2        : preserved (pre-regression)
 - 1.41.0 - 1.58.0  : parent scroll resets to 0 on dialog close (the #14917 bug)
 - >= 1.59.0        : preserved (fixed upstream)

The test asserts the desired invariant (scroll preserved), so it PASSES on fixed
Streamlit (>= 1.59) and FAILS on the affected range, acting as a compatibility guard.
Skipped where ``st.dialog`` is unavailable (Streamlit < 1.37).
"""

import os
from pathlib import Path

import pytest
import streamlit as st
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

APP_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_dialog_scroll.py")

pytestmark = pytest.mark.skipif(
    not hasattr(st, "dialog"),
    reason="st.dialog (required to reproduce #14917) is unavailable on this Streamlit",
)

STMAIN = 'section[data-testid="stMain"]'
IFRAME = 'iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]'
DIALOG = '[data-testid="stDialog"]'

# "reset to 0" vs "preserved" is a wide gap; allow small layout jitter.
TOLERANCE_PX = 50


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {"pdfjs.disabled": False},
    }


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(APP_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def _scroll_top(page: Page) -> float:
    return page.evaluate(f"document.querySelector('{STMAIN}').scrollTop")


def test_parent_scroll_preserved_after_dialog_close(page: Page):
    # Wait for the component to render. The component iframe starts hidden until
    # ready, so wait for it to be attached and for the PDF canvas + a page-2
    # annotation to render rather than asserting outer-iframe visibility.
    page.locator(IFRAME).nth(0).wait_for(state="attached", timeout=30000)
    frame = page.frame_locator(IFRAME).nth(0)
    expect(frame.locator('div[id="pdfViewer"] canvas').nth(0)).to_be_visible(timeout=30000)
    # data-index "2" is the first page-2 annotation; clicking it scrolls the page
    # down (giving a non-zero reference) and opens the dialog.
    annotation = frame.locator('div[data-index="2"]')
    expect(annotation).to_be_visible(timeout=15000)

    annotation.click()
    dialog = page.locator(DIALOG)
    expect(dialog).to_be_visible(timeout=15000)
    page.wait_for_timeout(400)

    # Scroll position at the moment the dialog is open is the reference the page
    # must return to after the dialog closes.
    scroll_when_open = _scroll_top(page)
    assert scroll_when_open > TOLERANCE_PX, (
        f"Precondition failed: page did not scroll on annotation click "
        f"({scroll_when_open}px); cannot detect a reset."
    )

    # Close the dialog -> triggers the rerun that resets the scroll on affected builds.
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible(timeout=15000)
    page.wait_for_timeout(700)

    after = _scroll_top(page)
    delta = abs(after - scroll_when_open)
    assert delta <= TOLERANCE_PX, (
        f"Parent scroll not preserved after dialog close (#14917): "
        f"open={scroll_when_open}px, after={after}px, delta={delta}px"
    )
