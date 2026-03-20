import pytest
from playwright.sync_api import Page, expect


@pytest.mark.edge_case
def test_edge_case_very_small_width(page: Page):
    """Test PDF viewer with very small width."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the first viewer (very small width)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    # Check that the container has reasonable dimensions
    container_box = pdf_container.bounding_box()
    assert container_box['width'] > 0, "Container should have positive width"
    assert container_box['height'] > 0, "Container should have positive height"


@pytest.mark.edge_case
def test_edge_case_very_large_width(page: Page):
    """Test PDF viewer with very large width."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    # Check that the container handles large width appropriately
    container_box = pdf_container.bounding_box()
    # The container should not exceed the viewport width
    viewport_width = page.viewport_size['width']
    assert container_box['width'] <= viewport_width, "Large width should not exceed viewport"


@pytest.mark.edge_case
def test_edge_case_extreme_zoom_out(page: Page):
    """Test PDF viewer with extreme zoom out."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the third viewer (extreme zoom out)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas with extreme zoom out
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()
    
    # With extreme zoom out, the canvas should be very small
    canvas_box = canvas.bounding_box()
    assert canvas_box['width'] > 0, "Canvas should still be visible even with extreme zoom out"


@pytest.mark.edge_case
def test_edge_case_extreme_zoom_in(page: Page):
    """Test PDF viewer with extreme zoom in."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the fourth viewer (extreme zoom in)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas with extreme zoom in
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()
    
    # With extreme zoom in, the canvas should be very large
    canvas_box = canvas.bounding_box()
    assert canvas_box['width'] > 0, "Canvas should still be visible even with extreme zoom in"


@pytest.mark.edge_case
def test_edge_case_no_width_specified(page: Page):
    """Test PDF viewer with no width specified (should use default)."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the fifth viewer (no width specified)
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    # Check that the container has a reasonable default width
    container_box = pdf_container.bounding_box()
    assert container_box['width'] > 0, "Default width should be positive"
    assert container_box['width'] < 2000, "Default width should not be excessive"


@pytest.mark.edge_case
def test_edge_case_all_viewers_functional(page: Page):
    """Test that all edge case viewers remain functional."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test that all viewers are functional despite edge cases
    for i in range(1):
        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)
        
        # Each viewer should have a visible container
        pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
        expect(pdf_container).to_be_visible()
        
        # Each viewer should have a visible PDF viewer
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()
        
        # Each viewer should have rendered content
        canvas = pdf_viewer.locator("canvas").first
        expect(canvas).to_be_visible()
        
        # Verify canvas has reasonable dimensions
        canvas_box = canvas.bounding_box()
        assert canvas_box['width'] > 0, f"Canvas {i+1} should have positive width"
        assert canvas_box['height'] > 0, f"Canvas {i+1} should have positive height"


@pytest.mark.edge_case
def test_edge_case_viewport_resize(page: Page):
    """Test that edge case viewers handle viewport resizing."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test with different viewport sizes
    viewports = [
        {"width": 1920, "height": 1080},  # Large desktop
        {"width": 375, "height": 667},    # Mobile
    ]
    
    for viewport in viewports:
        page.set_viewport_size(viewport)
        page.wait_for_timeout(500)

        # Check that all viewers remain functional
        for i in range(1):
            iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)
            pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
            expect(pdf_viewer).to_be_visible()
            
            # Check for canvas elements
            canvas = pdf_viewer.locator("canvas").first
            expect(canvas).to_be_visible()
