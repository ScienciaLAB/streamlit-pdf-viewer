import pytest
from playwright.sync_api import Page, expect


@pytest.mark.interactive
def test_zoom_controls_visibility(page: Page):
    """Test that zoom controls are visible and functional."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()

    # Check that all three PDF viewers are present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Test the first viewer (with zoom controls)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)

    # Check zoom button is visible
    zoom_button = iframe_frame.locator('button.zoom-button')
    expect(zoom_button).to_be_visible()

    # Click to open zoom panel and verify controls
    zoom_button.click()
    zoom_panel = iframe_frame.locator('div.zoom-panel')
    expect(zoom_panel).to_be_visible()

    zoom_in_button = iframe_frame.locator('button').filter(has_text="Zoom In")
    zoom_out_button = iframe_frame.locator('button').filter(has_text="Zoom Out")
    expect(zoom_in_button).to_be_visible()
    expect(zoom_out_button).to_be_visible()
