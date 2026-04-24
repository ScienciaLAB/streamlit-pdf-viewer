from unittest.mock import patch

import pytest

from streamlit_pdf_viewer import pdf_viewer

DUMMY_PDF = b"%PDF-1.0 dummy"


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    yield None


@pytest.fixture(autouse=True, scope="function")
def go_to_app():
    yield None


@patch("streamlit_pdf_viewer._component_func", return_value=None)
class TestScrollBehaviorValidation:
    """Unit tests for the scroll_behavior parameter validation."""

    def test_default_is_smooth(self, mock_component):
        pdf_viewer(DUMMY_PDF)
        kwargs = mock_component.call_args[1]
        assert kwargs["scroll_behavior"] == "smooth"

    def test_accepts_smooth(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_behavior="smooth")
        kwargs = mock_component.call_args[1]
        assert kwargs["scroll_behavior"] == "smooth"

    def test_accepts_instant(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_behavior="instant")
        kwargs = mock_component.call_args[1]
        assert kwargs["scroll_behavior"] == "instant"

    def test_rejects_invalid_value(self, mock_component):
        with pytest.raises(ValueError, match="scroll_behavior"):
            pdf_viewer(DUMMY_PDF, scroll_behavior="auto")

    def test_rejects_empty_string(self, mock_component):
        with pytest.raises(ValueError, match="scroll_behavior"):
            pdf_viewer(DUMMY_PDF, scroll_behavior="")


@patch("streamlit_pdf_viewer._component_func", return_value=None)
class TestScrollToAnnotationContract:
    """Python forwards scroll_to_annotation as 1-based; the frontend converts to its
    own 0-based data-position attribute. Python's job is just pass-through plus the
    pre-existing < 1 → None coercion."""

    def test_one_passes_through(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_to_annotation=1)
        assert mock_component.call_args[1]["scroll_to_annotation"] == 1

    def test_arbitrary_n_passes_through(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_to_annotation=5)
        assert mock_component.call_args[1]["scroll_to_annotation"] == 5

    def test_none_passes_through(self, mock_component):
        pdf_viewer(DUMMY_PDF)
        assert mock_component.call_args[1]["scroll_to_annotation"] is None

    def test_zero_is_coerced_to_none(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_to_annotation=0)
        assert mock_component.call_args[1]["scroll_to_annotation"] is None

    def test_negative_is_coerced_to_none(self, mock_component):
        pdf_viewer(DUMMY_PDF, scroll_to_annotation=-3)
        assert mock_component.call_args[1]["scroll_to_annotation"] is None

    def test_combined_with_scroll_to_page_raises(self, mock_component):
        with pytest.raises(ValueError, match="cannot be used together"):
            pdf_viewer(DUMMY_PDF, scroll_to_page=1, scroll_to_annotation=1)
