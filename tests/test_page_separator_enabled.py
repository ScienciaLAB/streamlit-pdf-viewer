import os
from math import ceil, floor
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_page_separator_enabled.py")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {
            "pdfjs.disabled": False,
        }
    }


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def test_should_render_with_page_separators_enabled(page: Page):
    expect(page.get_by_text("Test PDF Viewer with page separators enabled")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    expect(iframe_component).to_be_visible()

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    # Verify PDF viewer is present and has content
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

    canvas_list = pdf_viewer.locator("canvas").all()
    assert len(canvas_list) > 0
    for canvas in canvas_list:
        expect(canvas).to_be_visible()


def test_page_separators_are_visible(page: Page):
    """
    Verify that page separators are present when the viewer is configured with page separators.
    
    This test:
    - Locates the first PDF viewer iframe and the page divs within it.
    - Asserts at least one page div is visible.
    - Reads the computed `margin-bottom` style of the first page div and asserts it is not "0px", indicating a visible separator between pages.
    
    Parameters:
        page (playwright.sync_api.Page): Playwright page instance pointing at the running app.
    """
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    
    # Look for page elements with border styles
    # Page separators are implemented as CSS borders on page divs
    page_divs = iframe_frame.locator('div.page')
    
    # With show_page_separator=True, page divs should have border-bottom styles
    # Check that at least one page div exists
    expect(page_divs.first).to_be_visible()
    
    # Get the first page div and check its computed style
    first_page = page_divs.first
    border_bottom = first_page.evaluate("el => getComputedStyle(el).marginBottom")
    
    # The border should be set (not '0px')
    assert border_bottom != '0px', f"Expected border-bottom to be set, but got: {border_bottom}" 