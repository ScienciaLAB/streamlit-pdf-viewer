import pytest
from playwright.sync_api import Page, expect


@pytest.mark.compatibility
def test_basic_pdf_viewer_compatibility(page: Page):
    """Test basic PDF viewer functionality across browsers."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that the basic PDF viewer iframe is present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)  # Just one PDF viewer
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements (rendered PDF content)
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()


@pytest.mark.compatibility
def test_pdf_viewer_renders_correctly(page: Page):
    """Test that PDF viewer renders correctly across browsers."""
    # Check that the PDF viewer is present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements (rendered PDF content)
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()
    
    # Verify canvas has reasonable dimensions
    canvas_box = canvas.bounding_box()
    assert canvas_box['width'] > 0, "Canvas should have positive width"
    assert canvas_box['height'] > 0, "Canvas should have positive height"
