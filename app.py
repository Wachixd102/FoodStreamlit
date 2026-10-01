from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from neo4j_service import (
    get_dashboard_metrics,
    get_profile,
    get_students,
    graph_neighborhood,
    list_categories,
    ping,
    recommend_books,
    record_borrow,
    search_books,
    seed_demo_data,
)

st.set_page_config(
    page_title="GraphBook Recommender",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
      .hero {
        padding: 1.4rem 1.6rem; border-radius: 22px;
        background: linear-gradient(120deg, #111827 0%, #1f2937 55%, #0f766e 100%);
        color: white; margin-bottom: 1rem;
      }
      .hero h1 {margin:0; font-size:2.15rem;}
      .hero p {opacity:.88; margin:.35rem 0 0 0;}
      .book-card {
        padding: 1rem 1.1rem; border: 1px solid rgba(128,128,128,.25);
        border-radius: 16px; margin-bottom: .75rem;
      }
      .score-pill {
        display:inline-block; padding:.2rem .55rem; border-radius:999px;
        background:#0f766e; color:white; font-size:.8rem; font-weight:700;
      }
      .muted {opacity:.72; font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def require_connection() -> None:
    try:
        if not ping():
            raise RuntimeError("Neo4j did not return a healthy response")
    except Exception as exc:
        st.error("ยังเชื่อมต่อ Neo4j Aura ไม่สำเร็จ")
        st.code(
            '[neo4j]\nuri = "neo4j+s://YOUR_INSTANCE.databases.neo4j.io"\n'
            'username = "neo4j"\npassword = "YOUR_PASSWORD"\ndatabase = "neo4j"',
            language="toml",
        )
        st.caption("ให้นำค่าด้านบนไปใส่ใน Streamlit Secrets และห้าม commit password ลง GitHub")
        st.exception(exc)
        st.stop()


def student_selector(key: str = "student") -> str:
    students = get_students()
    if not students:
        st.info("ยังไม่มีข้อมูลนักศึกษา กรุณาไปหน้า Admin / Setup แล้วสร้างข้อมูลตัวอย่าง")
        st.stop()
    labels = {f"{x['student_id']} — {x['name']}": x["student_id"] for x in students}
    chosen = st.selectbox("เลือกผู้ใช้", list(labels), key=key)
    return labels[chosen]


def explain_reason(row: dict) -> str:
    parts = []
    if row.get("friend_count", 0):
        friends = ", ".join(row.get("friend_names") or [])
        parts.append(f"เพื่อน {row['friend_count']} คนเคยยืม" + (f" ({friends})" if friends else ""))
    if row.get("interest_matches", 0):
        cats = ", ".join(row.get("matched_categories") or [])
        parts.append(f"ตรงกับความสนใจ {row['interest_matches']} หมวด" + (f" ({cats})" if cats else ""))
    if row.get("popularity", 0):
        parts.append(f"ถูกยืมแล้ว {row['popularity']} ครั้ง")
    if row.get("avg_rating", 0):
        parts.append(f"คะแนนเฉลี่ย {row['avg_rating']:.2f}/5")
    return " • ".join(parts) or "แนะนำจากข้อมูลพฤติกรรมโดยรวม"


require_connection()

with st.sidebar:
    st.markdown("## 📚 GraphBook")
    st.caption("Neo4j Aura + Streamlit")
    page = st.radio(
        "เมนู",
        ["Dashboard", "Recommendations", "Book Search", "Borrow / Rate", "Graph Explorer", "Admin / Setup"],
    )
    st.divider()
    st.caption("Bachelor-level Graph Database Project")

st.markdown(
    """
    <div class="hero">
      <h1>📚 GraphBook Recommendation System</h1>
      <p>ระบบแนะนำหนังสือด้วย Graph Database ที่อธิบายเหตุผลของคำแนะนำได้</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Dashboard":
    st.subheader("ภาพรวมระบบ")
    m = get_dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", m.get("students", 0))
    c2.metric("Books", m.get("books", 0))
    c3.metric("Borrowed relationships", m.get("borrows", 0))
    c4.metric("Friend relationships", m.get("friendships", 0))

    st.divider()
    student_id = student_selector("dash_student")
    profile = get_profile(student_id)
    if profile:
        left, right = st.columns([1, 2])
        with left:
            st.markdown(f"### {profile['name']}")
            st.write(f"**รหัส:** {profile['student_id']}")
            st.write(f"**สาขา:** {profile['major']}")
            st.write(f"**ชั้นปี:** {profile['year']}")
            st.write("**ความสนใจ:** " + (", ".join(profile["interests"]) or "ยังไม่มี"))
        with right:
            st.markdown("### ประวัติการยืม")
            if profile["borrowed"]:
                st.dataframe(pd.DataFrame(profile["borrowed"]), use_container_width=True, hide_index=True)
            else:
                st.info("ยังไม่มีประวัติการยืม")

elif page == "Recommendations":
    st.subheader("✨ หนังสือที่แนะนำ")
    student_id = student_selector("rec_student")
    top_n = st.slider("จำนวนคำแนะนำ", 3, 12, 6)
    rows = recommend_books(student_id, top_n)

    st.caption("คะแนนตัวอย่าง = เพื่อน × 3 + หมวดความสนใจ × 2 + ความนิยม × 0.20 + rating เฉลี่ย × 0.50")
    if not rows:
        st.info("ยังไม่มีคำแนะนำสำหรับผู้ใช้นี้")
    for i, row in enumerate(rows, start=1):
        authors = ", ".join(row.get("authors") or []) or "ไม่ระบุผู้แต่ง"
        categories = ", ".join(row.get("categories") or []) or "ไม่ระบุหมวด"
        st.markdown(
            f"""
            <div class="book-card">
              <span class="score-pill">#{i} · score {row['score']:.2f}</span>
              <h3 style="margin:.55rem 0 .2rem 0">{row['title']}</h3>
              <div class="muted">{row['book_id']} · {authors} · {categories}</div>
              <p><b>เหตุผล:</b> {explain_reason(row)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif page == "Book Search":
    st.subheader("🔎 ค้นหาหนังสือ")
    c1, c2 = st.columns([2, 1])
    keyword = c1.text_input("ชื่อหนังสือหรือผู้แต่ง", placeholder="เช่น Python, Neo4j, Kanya")
    categories = [""] + list_categories()
    category = c2.selectbox("หมวด", categories, format_func=lambda x: "ทุกหมวด" if x == "" else x)
    rows = search_books(keyword, category)
    st.write(f"พบ {len(rows)} รายการ")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

elif page == "Borrow / Rate":
    st.subheader("📝 บันทึกการยืมและให้คะแนน")
    student_id = student_selector("borrow_student")
    books = search_books()
    if not books:
        st.info("ยังไม่มีหนังสือ")
        st.stop()
    book_labels = {f"{b['book_id']} — {b['title']}": b["book_id"] for b in books}
    selected = st.selectbox("หนังสือ", list(book_labels))
    borrow_date = st.date_input("วันที่ยืม", value=date.today())
    use_rating = st.checkbox("ให้คะแนนพร้อมกัน")
    rating = st.slider("คะแนน", 1.0, 5.0, 4.0, 0.5, disabled=not use_rating)
    if st.button("บันทึก", type="primary", use_container_width=True):
        record_borrow(student_id, book_labels[selected], borrow_date.isoformat(), rating if use_rating else None)
        st.success("บันทึกความสัมพันธ์ BORROWED แล้ว")

elif page == "Graph Explorer":
    st.subheader("🕸️ Graph Explorer")
    student_id = student_selector("graph_student")
    rows = graph_neighborhood(student_id)
    if not rows:
        st.info("ยังไม่มี neighborhood graph")
    else:
        dot = ["digraph G {", 'rankdir="LR";', 'node [shape=box, style="rounded,filled", fillcolor="#f8fafc"];']
        seen_nodes = set()
        for r in rows:
            for nid, label, name in [
                (r["source_id"], r["source_label"], r["source_name"]),
                (r["target_id"], r["target_label"], r["target_name"]),
            ]:
                if nid not in seen_nodes:
                    safe_name = str(name).replace('"', "'")
                    dot.append(f'"{nid}" [label="{safe_name}\\n:{label}"];')
                    seen_nodes.add(nid)
            dot.append(f'"{r["source_id"]}" -> "{r["target_id"]}" [label="{r["relationship"]}"];')
        dot.append("}")
        st.graphviz_chart("\n".join(dot), use_container_width=True)
        with st.expander("ดูข้อมูล edge ที่ใช้วาดกราฟ"):
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

elif page == "Admin / Setup":
    st.subheader("⚙️ Setup ข้อมูลตัวอย่าง")
    st.warning("ปุ่มนี้ไม่ลบข้อมูลเดิม และใช้ MERGE จึงสามารถกดซ้ำได้")
    st.markdown(
        """
        **Graph schema**
        - `(:Student)-[:FRIEND_OF]-(:Student)`
        - `(:Student)-[:BORROWED {borrow_date, rating}]->(:Book)`
        - `(:Student)-[:INTERESTED_IN]->(:Category)`
        - `(:Book)-[:IN_CATEGORY]->(:Category)`
        - `(:Author)-[:WROTE]->(:Book)`
        """
    )
    if st.button("สร้าง Constraint + Demo Data", type="primary", use_container_width=True):
        with st.spinner("กำลังสร้างข้อมูล..."):
            seed_demo_data()
        st.success("สร้างข้อมูลตัวอย่างเรียบร้อยแล้ว")
        st.rerun()
