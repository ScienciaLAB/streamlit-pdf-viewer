# Copyright 2025 Streamlit PDF Component
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reproduction app for streamlit/streamlit#14917.

Renders the PDF viewer at the top of the page with clickable annotations. Clicking
a page-2 annotation scrolls the page down (the PDF is tall) and opens an
``st.dialog``; closing that dialog triggers a rerun. On affected Streamlit versions
(1.41-1.58) the parent page scroll (``section[data-testid="stMain"]``) resets to the
top when the dialog closes; on <= 1.40.2 and >= 1.59.0 it is preserved.
"""

import os

import streamlit as st
from tests import ROOT_DIRECTORY

from streamlit_pdf_viewer import pdf_viewer

st.subheader("Dialog scroll-reset reproduction (issue #14917)")


@st.dialog("Annotation")
def show_popup(annotation):
    st.write("Close me (Escape / X) and observe whether the page scroll is preserved.")
    st.json(annotation)


# The component's returned value is sticky: on_annotation_click fires again on the
# rerun caused by closing the dialog. Gate on session_state so the dialog opens once
# per click and stays closed afterwards (otherwise it would immediately reopen).
def handle_click(annotation):
    if not st.session_state.get("dialog_shown"):
        st.session_state["dialog_shown"] = True
        show_popup(annotation)


annotations = [
    {"page": 1, "x": 100, "y": 100, "height": 22, "width": 30, "color": "blue"},
    {"page": 1, "x": 150, "y": 120, "height": 22, "width": 30, "color": "green"},
    {"page": 2, "x": 180, "y": 130, "height": 22, "width": 30, "color": "purple"},
    {"page": 2, "x": 220, "y": 155, "height": 22, "width": 30, "color": "red"},
]

pdf_viewer(
    os.path.join(ROOT_DIRECTORY, "resources/test.pdf"),
    width=800,
    annotations=annotations,
    on_annotation_click=handle_click,
)
