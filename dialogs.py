"""
dialogs.py — Shared Streamlit dialog components for BalikGamit.
"""

import streamlit as st
from utils import icon, icon_html, badge, photo_html, CATEGORY_ICONS


@st.dialog("Item Details", width="large")
def item_detail_dialog(item: dict) -> None:
    cat_icon_name = CATEGORY_ICONS.get(item.get("category", "Other"), "package")

    if item.get("photo"):
        st.markdown(photo_html(item["photo"], width="100%", height="320px", radius="12px"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    else:
        st.markdown(photo_html(None, width="100%", height="120px", radius="12px", placeholder_text="No photo uploaded"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;'>
          {badge(item['status'])}
          <span style='display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;color:#164EC6;
                       text-transform:uppercase;letter-spacing:.06em;'>
            {icon(cat_icon_name, 13, "#164EC6")} {item.get('category','—')}
          </span>
          <code style='margin-left:auto;font-size:.72rem;'>{item.get('id','—')}</code>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(f"### {item.get('title', 'Untitled Item')}")

    col_l, col_r = st.columns(2)
    col_l.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;">'
        f'{icon_html("map-pin",14,"#6B7280")} <strong>Location:</strong>&nbsp;{item.get("location","—")}</div>',
        unsafe_allow_html=True,
    )
    col_r.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;">'
        f'{icon_html("calendar",14,"#6B7280")} <strong>Date:</strong>&nbsp;{item.get("date","—")}</div>',
        unsafe_allow_html=True,
    )

    if item.get("marks"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;margin-top:6px;">'
            f'{icon_html("tag",14,"#6B7280")} <strong>Identifying marks:</strong>&nbsp;{item["marks"]}</div>',
            unsafe_allow_html=True,
        )
    if item.get("contact"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;margin-top:6px;">'
            f'{icon_html("mail",14,"#6B7280")} <strong>Contact:</strong>&nbsp;{item["contact"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-weight:600;font-size:.875rem;margin-bottom:6px;">'
        f'{icon_html("file-text",14,"#374151")} Full Description</div>',
        unsafe_allow_html=True,
    )
    st.write(item.get("note") or "No additional details provided.")
