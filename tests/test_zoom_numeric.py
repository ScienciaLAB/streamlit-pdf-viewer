import os
from math import ceil, floor
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_zoom_numeric.py")


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


def test_should_render_with_numeric_zoom(page: Page):
    expect(page.get_by_text("Test PDF Viewer with numeric zoom level")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

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


def test_zoom_controls_functionality(page: Page):
    """
    Verify the PDF viewer's zoom controls open and all expected controls are visible.
    
    Navigates into the viewer iframe, opens the zoom panel by clicking the zoom button (waits up to 5s for the button to become visible), and asserts that the zoom panel, "Zoom In" and "Zoom Out" buttons, and the manual zoom input are visible.
    """
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    
    # Click zoom button to open panel
    zoom_button = iframe_frame.locator('button.zoom-button')
    zoom_button.wait_for(timeout=5000, state='visible')
    zoom_button.click()
    
    # Check that zoom panel is visible
    zoom_panel = iframe_frame.locator('div.zoom-panel')
    expect(zoom_panel).to_be_visible()
    
    # Check for zoom controls
    zoom_in_button = iframe_frame.locator('button').filter(has_text="Zoom In")
    zoom_out_button = iframe_frame.locator('button').filter(has_text="Zoom Out")
    manual_zoom_input = iframe_frame.locator('input.zoom-input')
    
    expect(zoom_in_button).to_be_visible()
    expect(zoom_out_button).to_be_visible()
    expect(manual_zoom_input).to_be_visible()