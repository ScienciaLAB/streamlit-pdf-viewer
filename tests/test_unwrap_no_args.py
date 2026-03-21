import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_unwrap_no_args.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    expect(page.get_by_role("img", name="Running...")).not_to_be_visible()


def test_should_render_template_check_container_size(page: Page):
    expect(page.get_by_text("Test PDF Viewer with no args")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    pdf_container.wait_for(timeout=5000, state='visible')
    expect(pdf_container).to_be_visible()

    b_box = pdf_container.bounding_box()
    # Since we do not specify the width, we occupy all the available space, which should correspond to the
    # parent element's width of the pdfContainer.
    assert b_box['width'] == iframe_box['width']
    assert b_box['height'] > 0

    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

    canvas_locator = pdf_viewer.locator("canvas")
    expect(canvas_locator).to_have_count(8)
    for canvas in canvas_locator.all():
        expect(canvas).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()

def test_should_render_multiple_pages(page: Page):
    """Test that PDF viewer renders all pages correctly"""
    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    pdf_viewer.wait_for(timeout=5000, state='visible')

    canvas_locator = pdf_viewer.locator("canvas")
    expect(canvas_locator).to_have_count(8)

    # All canvases should be visible
    for i, canvas in enumerate(canvas_locator.all()):
        expect(canvas).to_be_visible()
        # Each canvas should have reasonable dimensions
        canvas_box = canvas.bounding_box()
        assert canvas_box['width'] > 0
        assert canvas_box['height'] > 0


def test_should_responsive_to_viewport_changes(page: Page):
    """Test that PDF viewer responds correctly to viewport size changes"""
    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')

    # Get initial dimensions
    initial_frame_box = iframe_component.bounding_box()
    initial_width = initial_frame_box['width']
    initial_height = initial_frame_box['height']

    # Change viewport size
    page.set_viewport_size({"width": 600, "height": 400})
    page.wait_for_timeout(500)  # Wait for responsive adjustment

    # Get dimensions after viewport change
    new_frame_box = iframe_component.bounding_box()

    # The viewer should adjust to viewport changes
    assert new_frame_box['width'] != initial_width or new_frame_box['height'] != initial_height

    # PDF content should still be visible
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
