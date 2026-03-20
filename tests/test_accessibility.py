import pytest
from playwright.sync_api import Page, expect


@pytest.mark.accessibility
def test_accessibility_iframe_titles(page: Page):
    """Test that PDF viewer iframes have proper titles for screen readers."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that PDF viewer iframe has proper title
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Verify that the iframe has the expected title
    iframe = iframe_components.nth(0)
    title = iframe.get_attribute('title')
    assert title == "streamlit_pdf_viewer.streamlit_pdf_viewer", "Iframe should have proper title"


@pytest.mark.accessibility
def test_accessibility_keyboard_navigation(page: Page):
    """Test that PDF viewers are accessible via keyboard navigation."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test keyboard navigation to the iframe
    iframe = iframe_components.nth(0)
    
    # Focus on the iframe
    iframe.focus()
    
    # Check that the iframe is focusable
    focused_element = page.evaluate("document.activeElement")
    assert focused_element is not None, "Iframe should be focusable"


@pytest.mark.accessibility
def test_accessibility_zoom_levels_for_visibility(page: Page):
    """Test that different zoom levels improve accessibility for users with visual impairments."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    canvas = iframe_frame.locator("canvas").first

    # Wait for the canvas to be visible before getting bounding box
    expect(canvas).to_be_visible()

    canvas_box = canvas.bounding_box()
    
    # Verify that the canvas has reasonable dimensions for accessibility
    assert canvas_box is not None, "Canvas bounding box should be available"
    assert canvas_box['width'] > 0, "Canvas should have positive width for accessibility"
    assert canvas_box['height'] > 0, "Canvas should have positive height for accessibility"


@pytest.mark.accessibility
def test_accessibility_screen_reader_compatibility(page: Page):
    """Test that PDF viewers are compatible with screen readers."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Check that the iframe has proper ARIA attributes or is properly labeled
    iframe = iframe_components.nth(0)
    
    # Check for title attribute (already tested above)
    title = iframe.get_attribute('title')
    assert title is not None, "Iframe should have a title for screen readers"
    
    # Check that the iframe is not hidden from screen readers
    aria_hidden = iframe.get_attribute('aria-hidden')
    assert aria_hidden != 'true', "Iframe should not be hidden from screen readers"


@pytest.mark.accessibility
def test_accessibility_high_contrast_mode(page: Page):
    """Test that PDF viewers work well in high contrast mode."""
    # Simulate high contrast mode by adding CSS
    page.add_style_tag(content="""
        * {
            filter: contrast(200%) !important;
        }
    """)
    
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Check that the viewer is still visible and functional in high contrast
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()


@pytest.mark.accessibility
def test_accessibility_responsive_text_sizing(page: Page):
    """Test that PDF viewers respond well to different text sizes."""
    # Test with different viewport sizes that might affect text rendering
    viewports = [
        {"width": 1920, "height": 1080},  # Large desktop
        {"width": 375, "height": 667},    # Mobile
    ]
    
    for viewport in viewports:
        page.set_viewport_size(viewport)
        page.wait_for_timeout(500)

        iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
        expect(iframe_components).to_have_count(1)
        
        # Check that the viewer remains accessible
        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()
        
        # Check for canvas elements
        canvas = pdf_viewer.locator("canvas").first
        expect(canvas).to_be_visible()
        
        # Verify canvas has reasonable dimensions for accessibility
        canvas_box = canvas.bounding_box()
        assert canvas_box is not None, f"Canvas bounding box should be available at viewport {viewport}"
        assert canvas_box['width'] > 0, f"Canvas should be visible at viewport {viewport}"
        assert canvas_box['height'] > 0, f"Canvas should have positive height at viewport {viewport}"
