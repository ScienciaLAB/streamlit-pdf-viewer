import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY, wait_for_canvases
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_unwrap_height.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app and wait until the app's "Running..." image is hidden.
    
    This performs a page.goto to the runner's server_url and waits for the app to finish loading by checking that the role="img" element with name "Running..." is no longer visible.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def test_should_render_template_check_container_size(page: Page):
    expect(page.get_by_text("Test PDF Viewer with specified height")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    b_box = pdf_container.bounding_box()
    # Since we do not specify the width, we occupy all the available space, which should correspond to the
    # parent element's width of the pdfContainer.
    # LF: This was changed with #58, where the proportions are maintained, or at least we try to
    assert b_box['width'] <= iframe_box['width']
    assert b_box['height'] == 300

    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    pdf_viewer.wait_for(timeout=5000, state='visible')
    expect(pdf_viewer).to_be_visible()

    canvas_locator = pdf_viewer.locator("canvas")
    canvas_list = wait_for_canvases(canvas_locator)

    # Should have 8 pages total for the test PDF
    assert len(canvas_list) == 8
    for canvas in canvas_list:
        expect(canvas).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()
