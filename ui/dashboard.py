"""Human-in-the-loop audit dashboard with cropped document visualizations."""
import io, json, base64
import streamlit as st
import requests
from PIL import Image

API = "http://localhost:8000"
st.set_page_config(page_title="Extraction Audit", layout="wide")
st.title("HITL Audit Dashboard — Document Extraction")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Upload & Extract")
    f = st.file_uploader("Invoice / receipt image", type=["png", "jpg", "jpeg"])
    if f and st.button("Run extraction"):
        img = Image.open(f)
        st.session_state["img"] = img
        r = requests.post(f"{API}/extract", files={"file": (f.name, f.getvalue())}).json()
        st.session_state["result"] = r
        st.rerun()

    if "img" in st.session_state:
        img: Image.Image = st.session_state["img"]
        st.image(img, caption="Full document", use_container_width=True)
        w, h = img.size
        st.image(img.crop((0, 0, w, h // 3)), caption="Header crop (vendor / GSTIN / date)",
                 use_container_width=True)
        st.image(img.crop((0, h // 3, w, h)), caption="Line-items & totals crop",
                 use_container_width=True)

with col2:
    st.header("Extraction Result")
    r = st.session_state.get("result")
    if r:
        st.badge(r["status"])
        if r["validation_issues"]:
            st.error("Validation issues detected")
            for issue in r["validation_issues"]:
                st.write("•", issue)
        edited = st.text_area("Correct JSON if needed, then approve",
                              json.dumps(r["invoice"], indent=2, default=str), height=400)
        if st.button("✅ Approve"):
            requests.post(f"{API}/records/{r['id']}/approve",
                          params={"corrected_payload": edited})
            st.success("Approved & persisted.")

    st.divider()
    st.header("Queue")
    if st.button("Refresh"):
        st.session_state.pop("queue", None)
    if "queue" not in st.session_state:
        st.session_state["queue"] = requests.get(f"{API}/records",
                                                 params={"needs_review": True}).json()
    for rec in st.session_state["queue"]:
        st.write(f"🔎 `{rec['id'][:8]}` — {rec['filename']} — {rec['issues'] or 'no issues'}")
