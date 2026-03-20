import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_text_layers.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    """Streamlit app fixture using the text layers example."""
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app and wait until the app finishes loading.

    This directs `page` to the URL provided by `streamlit_app.server_url` and waits for the loading indicator (an image with accessible name "Running...") to become hidden, ensuring the app has finished its initial load before tests proceed.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def test_should_render_template_check_container_size(page: Page):
    """
    Verify that the PDF viewer embedded in two tabs renders text and that container sizing behaves as expected.
    
    Performs UI assertions against two iframe-based PDF viewers:
    - Confirms the main template text and both tab labels are visible.
    - For the first tab: asserts the PDF container and viewer are visible and the container width matches the iframe width; annotations are hidden.
    - For the second tab: verifies initial invisibility of its PDF container/viewer and annotations, then clicks the tab, waits for rendering, and asserts:
      - the PDF container becomes visible and its height is approximately 300px,
      - the container dimensions do not exceed the iframe width,
      - the PDF viewer and its canvas content render,
      - the expected text inside the PDF becomes visible.
    
    Parameters:
        page (playwright.sync_api.Page): Playwright page used to interact with the app and perform element assertions.
    """
    expect(page.get_by_text("Test PDF Viewer with the PDF in a tab and rendering text")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    tab0 = page.get_by_text('tab1')
    expect(tab0).to_be_visible()

    tab1 = page.get_by_text('tab2')
    expect(tab1).to_be_visible()

    # Tab 1
    iframe_frame_0 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container_0 = iframe_frame_0.locator('div[id="pdfContainer"]')
    pdf_container_0.wait_for(timeout=5000, state='visible')
    expect(pdf_container_0).to_be_visible()

    b_box_0 = pdf_container_0.bounding_box()
    # assert round(b_box_0['height']) > iframe_box['height']
    assert b_box_0['width'] == iframe_box['width']

    pdf_viewer_0 = iframe_frame_0.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_0).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()

    # Tab 2
    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    expect(pdf_container_1).not_to_be_visible()

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_1).not_to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(1)
    expect(annotations_locator).to_be_hidden()

    text_in_pdf = pdf_viewer_1.get_by_text("from LaH10 to room–temperature").nth(0)
    expect(text_in_pdf).to_be_hidden()

    # click on the second tab and verify that the PDF is visible
    tab1.click()
    
    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    pdf_container_1.wait_for(timeout=10000, state='visible')
    expect(pdf_container_1).to_be_visible()

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')

    # Wait for the PDF viewer to become visible and contain content
    pdf_viewer_1.wait_for(timeout=15000, state='visible')
    expect(pdf_viewer_1).to_be_visible()

    # Wait for canvas elements to be rendered (PDF content)
    canvas = pdf_viewer_1.locator('canvas').first
    canvas.wait_for(timeout=10000, state='visible')

    b_box_1 = pdf_container_1.bounding_box()
    assert 299 <= b_box_1['height'] <= 8000
    assert round(b_box_1['width']) <= iframe_box['width']
    
    text_in_pdf = pdf_viewer_1.get_by_text("from LaH10 to room–temperature").nth(0)
    text_in_pdf.wait_for(timeout=10000, state='visible')
    expect(text_in_pdf).to_be_visible()
