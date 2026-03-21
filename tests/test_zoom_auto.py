import os
from math import ceil, floor
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_zoom_auto.py")


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


def test_should_render_with_auto_zoom(page: Page):
    """
    Verify the PDF viewer renders inside an iframe with auto-zoom controls and visible page canvases.
    
    This test checks that:
    - The app title "Test PDF Viewer with auto zoom (fit to width)" is visible.
    - The PDF viewer iframe is present and becomes visible (waits up to 5s).
    - Inside the iframe, the PDF container and a zoom control button are visible.
    - The PDF viewer element contains at least one canvas, and every canvas is visible.
    """
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    # Check that zoom controls are present
    zoom_button = iframe_frame.locator('button.zoom-button')
    expect(zoom_button).to_be_visible()

    # Verify PDF viewer is present and has content
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

    canvas_list = pdf_viewer.locator("canvas").all()
    assert len(canvas_list) > 0
    for canvas in canvas_list:
        expect(canvas).to_be_visible()


def test_auto_zoom_fits_to_width(page: Page):
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    
    # Get the container width
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    container_box = pdf_container.bounding_box()
    
    # Get the first page canvas
    first_canvas = iframe_frame.locator('div[id="pdfViewer"] canvas').first
    canvas_box = first_canvas.bounding_box()
    
    # With auto zoom, the canvas width should approximately match the container width
    # (allowing for some margin of error due to rendering)
    assert abs(canvas_box['width'] - container_box['width']) < 50 