import pytest
from playwright.sync_api import Page, expect


@pytest.mark.responsive
def test_responsive_design_desktop_view(page: Page):
    """Test PDF viewer responsiveness on desktop viewport."""
    # Set desktop viewport
    page.set_viewport_size({"width": 1200, "height": 800})
    page.wait_for_timeout(500)

    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()

    # Check that all three PDF viewers are present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Test the first viewer (desktop width)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    # Check that the container has appropriate width for desktop
    container_box = pdf_container.bounding_box()
    assert container_box['width'] <= 800, "Desktop PDF viewer should not exceed specified width"
