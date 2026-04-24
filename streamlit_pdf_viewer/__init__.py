import base64
import os
from pathlib import Path
from typing import Union, List, Optional, Callable, Dict

import streamlit.components.v1 as components
import json

# Streamlit >= 1.41 introduced a regression in custom-component iframe handling
# that resets the page scroll position after an st.dialog is closed (see
# https://github.com/lfoppiano/streamlit-pdf-viewer/issues/107). Surface this to
# users at import time so it's visible without reading release notes.
try:
    import warnings as _warnings
    import streamlit as _st
    from packaging.version import Version as _V

    if _V(_st.__version__) >= _V("1.41.0"):
        _warnings.warn(
            "streamlit-pdf-viewer: Streamlit >= 1.41 has a known regression "
            "that may reset the page scroll after an st.dialog is closed. "
            "See https://github.com/lfoppiano/streamlit-pdf-viewer/issues/107 . "
            "Pin streamlit<1.41 if this affects your app.",
            UserWarning,
            stacklevel=2,
        )
except Exception:
    pass

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        path=build_dir
    )


def pdf_viewer(
        input: Union[str, Path, bytes],
        width: Union[str, int] = "100%",
        height: Optional[int] = None,
        key=None,
        annotations: List[Dict[str, Union[str, int, float, bool]]] = [],
        pages_vertical_spacing: int = 2,
        annotation_outline_size: int = 1,
        pages_to_render: List[int] = (),
        render_text: bool = False,
        resolution_boost: int = 1,
        zoom_level: Optional[Union[float, str]] = None,
        viewer_align: str = "center",
        show_page_separator: bool = True,
        scroll_to_page: Optional[int] = None,
        scroll_to_annotation: Optional[int] = None,
        scroll_behavior: str = "smooth",
        on_annotation_click: Optional[Callable[[dict], None]] = None,
        allow_clickable_annotations_with_text_rendering: bool = False,
):
    """
    pdf_viewer function to display a PDF file in a Streamlit app.

    :param input: The source of the PDF file. Accepts a file path, URL, or binary data.
    :param width: Width of the PDF viewer in pixels. It defaults to 100%. It supports both integer (pixel, e.g. 700) and string (percentages, e.g. 90% will make the pdf render to 90% of the container/window/screen width. If the pdf width is larger than the screen width, it will horizontally scroll).
    :param height: Height of the PDF viewer in pixels. If not provided, the viewer show the whole content.
    :param key: An optional key that uniquely identifies this component. Used to preserve state in Streamlit apps.
    :param annotations: A list of annotations to be overlaid on the PDF. Each annotation should be a dictionary.
    :param pages_vertical_spacing: The vertical space (in pixels) between each page of the PDF. Defaults to 2 pixels.
    :param annotation_outline_size: Size of the outline around each annotation in pixels. Defaults to 1 pixel.
    :param pages_to_render: Optional list of page numbers to render. If None, all pages are rendered. This allows for selective rendering of pages in the PDF.
    :param render_text: Whether to enable selection of text in the PDF viewer. Defaults to False.
    :param resolution_boost: Boost the resolution by a factor from 2 to 10. Defaults to 1.
    :param zoom_level: The zoom level of the PDF viewer. Can be a float (0.1-10.0), "auto" for fit-to-width, "auto-height" for fit-to-height, or None (defaults to auto-fit to width).
    :param viewer_align: The alignment of the PDF viewer in the container. Can be "center", "left", or "right". Defaults to "center".
    :param show_page_separator: Whether to show a separator between pages. Defaults to True.
    :param scroll_to_page: Scroll to a specific page in the PDF. The parameter is an integer, which represent the positional value of the page. E.g. 1, will be the first page. Defaults to None.
    :param scroll_to_annotation: Scroll to a specific annotation in the PDF. The parameter is a 1-based positional integer referring to the order of the annotation in the `annotations` list, independent of any `id` field on the annotation itself. E.g. 1 scrolls to the first annotation. Values below 1 are silently coerced to None. Defaults to None.
    :param scroll_behavior: The scrolling behavior when navigating to a page or annotation. Can be "smooth" (animated scroll) or "instant" (immediate jump). Defaults to "smooth".
    :param on_annotation_click: A callback function that will be called when an annotation is clicked. The function should accept a single argument, which is the annotation that was clicked. Defaults to None.
    :param allow_clickable_annotations_with_text_rendering: When True, annotations remain clickable even when render_text is enabled. Note that text selection will not work through annotation areas. Defaults to False.

    The function reads the PDF file (from a file path, URL, or binary data), encodes it in base64,
    and uses a Streamlit component to render it in the app. It supports optional annotations and adjustable margins.

    Returns the value of the selected component (if any).
    """

    # Validate width and height parameters
    if width is not None:
        if isinstance(width, str):
            # Check if the string is a valid integer or ends with '%'
            if not (width.isdigit() or width.endswith('%')):
                raise ValueError("Width must be an integer or a percentage string (e.g., '50%')")
        elif not isinstance(width, int):
            raise TypeError("Width must be an integer or a string")
    if height is not None and not isinstance(height, int):
        raise TypeError("Height must be an integer or None")
    if not all(isinstance(page, int) for page in pages_to_render):
        raise TypeError("pages_to_render must be a list of integers")

    if resolution_boost < 1:
        raise ValueError("resolution_boost must be greater than 1")
    elif resolution_boost > 10:
        raise ValueError("resolution_boost must be lower than 10")

    if zoom_level is not None:
        if isinstance(zoom_level, float) and (zoom_level < 0.1 or zoom_level > 10):
            raise ValueError("If zoom_level is a float, it must be between 0.1 and 10")
        elif isinstance(zoom_level, str) and zoom_level not in ["auto", "auto-height"]:
            raise ValueError("If zoom_level is a string, it must be 'auto' or 'auto-height'")

    if viewer_align not in ["center", "left", "right"]:
        raise ValueError("viewer_align must be one of 'center', 'left', or 'right'")

    if scroll_behavior not in ["smooth", "instant"]:
        raise ValueError("scroll_behavior must be one of 'smooth' or 'instant'")

    if scroll_to_page is not None:
        if scroll_to_annotation is not None:
            raise ValueError("scroll_to_page and scroll_to_annotation cannot be used together")
        if scroll_to_page is not None and scroll_to_page < 1:
            scroll_to_page = None

    else:
        if scroll_to_annotation is not None and scroll_to_annotation < 1:
            scroll_to_annotation = None

    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    if not isinstance(annotations, list):
        raise TypeError("annotations must be a list of dictionaries")
    if any(not isinstance(annotation, dict) for annotation in annotations):
        raise TypeError("annotations must be a list of dictionaries")


    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(
        binary=base64_pdf,
        width=width,
        height=height,
        key=key,
        default=0,
        annotations=annotations,
        pages_vertical_spacing=pages_vertical_spacing,
        annotation_outline_size=annotation_outline_size,
        pages_to_render=pages_to_render,
        render_text=render_text,
        resolution_boost=resolution_boost,
        zoom_level=zoom_level,
        viewer_align=viewer_align,
        show_page_separator=show_page_separator,
        scroll_to_page=scroll_to_page,
        scroll_to_annotation=scroll_to_annotation,
        scroll_behavior=scroll_behavior,
        allow_clickable_annotations_with_text_rendering=allow_clickable_annotations_with_text_rendering
    )

    # Execute the custom callback function
    if component_value and 'clicked_annotation' in component_value:
        clicked_annotation = component_value['clicked_annotation']
        if on_annotation_click is not None and callable(on_annotation_click):
            on_annotation_click(clicked_annotation)
    return component_value


if not _RELEASE:
    import streamlit as st
    from streamlit import markdown

    # from glob import glob

    # paths = glob("/Users/lfoppiano/kDrive/library/articles/materials informatics/polymers/*.pdf")
    # path = "/Users/lfoppiano/development/projects/alirahelth/data/articles/Basso Dias RAD 2022.pdf"
    # values = list(range(1, 10))
    # for id, tab in enumerate(st.tabs([f"tab {val}" for val in values])):
    #     with tab:
    #         with st.container(height=600):
    #             pdf_viewer(path, width=800, render_text=True, resolution_boost=values[id])
    #
    # def scroll_to_page(page):
    # st.markdown(
    #     """
    #     function(){
    #         document.getElementById(""" + page + """).scrollIntoView({behavior: 'smooth'})
    #     };
    #
    #     function()
    #     """, unsafe_allow_html=True)

    # print(page)
    # st.components.v1.html(
    #     """
    #     <script>
    #         function scrollDown(){
    #             page_canvas = document.getElementById('""" + page + """')
    #             console.log(page_canvas)
    #             page_canvas.scrollIntoView({behavior: 'smooth'})
    #         }
    #         scrollDown()
    #     </script>
    #     """
    # )

    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    with open("resources/test.pdf", 'rb') as fo:
        binary2 = fo.read()

    with open("resources/annotations.sample.json", 'rb') as fo:
        annotations = json.loads(fo.read())

    tab1, tab2 = st.tabs(["tab1", "tab2"])

    # st.markdown("""
    #     <style>
    #     * {
    #     overflow-anchor: none !important;
    #     }
    #     </style>""", unsafe_allow_html=True)
    # @st.fragment
    # def show_buttons_scrolling(pages_id: List):
    #     for page in pages_id:
    #         print(page)
    #         st.button(f"Page {page}", key=f"page_{page}", on_click=scroll_to_page, args=(page,))

    with tab1:
        st.markdown("tab 1")
        with st.container(height=400):
            viewer = pdf_viewer(
                binary,
                annotations=annotations,
                render_text=True,
                key="bao",
                scroll_to_page=3
            )
        # st.markdown(viewer)
        # st.markdown(type(viewer))
        # if type(viewer) == dict:
        #     annotations_id = viewer['annotations']
        #     pages_id = viewer['pages']
        #     show_buttons_scrolling(pages_id)

    with tab2:
        st.markdown("tab 2")
        viewer2 = pdf_viewer(
            binary2,
            height=500,
            annotations=annotations,
            render_text=True,
            key="miao",
            resolution_boost=4,
            scroll_to_annotation=2
        )

## Issue with Chrome

# from glob import glob
#
# # paths = glob("/Users/lfoppiano/kDrive/library/articles/materials informatics/polymers/*.pdf")
# paths = glob("/Users/lfoppiano/development/projects/alirahelth/data/articles/*.pdf")
# for id, (tab, path) in enumerate(zip(st.tabs(paths),paths)):
#     with tab:
#         with st.container(height=600):
#             if id == 0:
#                 pdf_viewer(path, width=500, render_text=True)
#             else:
#                 pdf_viewer(path, width=1000, render_text=True)
