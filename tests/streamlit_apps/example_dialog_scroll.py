import os

import streamlit as st
from tests import ROOT_DIRECTORY

from streamlit_pdf_viewer import pdf_viewer

st.subheader("Test scroll preservation around annotation-click dialog (issue #107)")


@st.dialog("annotation popup")
def show_popup():
    st.text("Close this dialog and the previous scroll position should be preserved.")


def handler(annotation):
    show_popup()


annotations = [
    {"page": 1, "x": 100, "y": 50, "height": 30, "width": 100, "color": "red"},
    {"page": 1, "x": 100, "y": 400, "height": 30, "width": 100, "color": "blue"},
    {"page": 1, "x": 100, "y": 700, "height": 30, "width": 100, "color": "green"},
]

pdf_viewer(
    os.path.join(ROOT_DIRECTORY, "resources/test.pdf"),
    width=600,
    height=400,
    annotations=annotations,
    on_annotation_click=handler,
    key="dialog-scroll-viewer",
)
