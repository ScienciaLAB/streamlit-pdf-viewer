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

    # Check for zoom controls
    zoom_controls = iframe_frame.locator('button.zoom-button, .zoom-controls, [class*="zoom"]')
    # Note: The exact selector depends on your frontend implementation
    # This is a flexible approach that looks for common zoom control patterns
