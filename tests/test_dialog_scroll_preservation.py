import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_dialog_scroll.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def test_scroll_position_preserved_after_annotation_dialog_close(page: Page):
    """Regression test for issue #107: clicking an annotation that opens a
    st.dialog should not reset the PDF scroll position once the dialog closes.
    """
    iframe_locator = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    iframe_locator.wait_for(timeout=10000, state='visible')

    iframe = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    scrolling_container = iframe.locator('.scrolling-container')
    scrolling_container.wait_for(state='visible', timeout=10000)

    iframe.locator('canvas#canvas_page_1').wait_for(state='visible', timeout=10000)

    target_scroll = 300
    scrolling_container.evaluate(f"el => {{ el.scrollTop = {target_scroll}; }}")
    page.wait_for_timeout(300)

    scroll_before = scrolling_container.evaluate("el => el.scrollTop")
    assert scroll_before >= target_scroll - 5, (
        f"Could not scroll internal container to {target_scroll} (got {scroll_before})"
    )

    # Click the middle annotation — at PDF y=400 it sits near viewer y~393,
    # which is at viewport y~93 once the container is scrolled to 300.
    annotation = iframe.locator('[id^="annotation-"]').nth(1)
    annotation.wait_for(state='visible', timeout=5000)
    annotation.click()

    expect(page.get_by_text("annotation popup")).to_be_visible(timeout=5000)

    page.keyboard.press("Escape")
    expect(page.get_by_text("annotation popup")).not_to_be_visible(timeout=5000)

    # Allow Streamlit to process the close-triggered rerun (iframe may remount
    # on Streamlit >= 1.41). Re-acquire the scroller in case the iframe changed.
    page.wait_for_timeout(800)
    iframe = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    iframe.locator('canvas#canvas_page_1').wait_for(state='visible', timeout=10000)
    scrolling_container = iframe.locator('.scrolling-container')

    scroll_after = scrolling_container.evaluate("el => el.scrollTop")
    assert abs(scroll_after - scroll_before) < 30, (
        f"Scroll position lost after dialog close: before={scroll_before}, after={scroll_after}"
    )
