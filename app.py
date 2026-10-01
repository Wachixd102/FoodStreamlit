from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from neo4j_service import (
    get_dashboard_metrics,
    get_graph,
    get_user_likes,
    get_users,
    ping,
    recommend_foods,
    search_foods,
)


# =========================
# PAGE SETUP
# =========================

st.set_page_config(
    page_title="Food Recommendation System",
    page_icon="🍜",
    layout="wide",
)


# =========================
# STYLE
# =========================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.3rem;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            #111827,
            #0f766e
        );
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
    }

    .food-card {
        padding: 1rem;
        border: 1px solid #444;
        border-radius: 15px;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# CONNECTION
# =========================

if not ping():

    st.error(
        "ไม่สามารถเชื่อมต่อ Neo4j Aura ได้"
    )

    st.stop()


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown(
        "## 🍜 Food Recommendation"
    )

    st.caption(
        "Neo4j Aura + Streamlit"
    )

    page = st.radio(
        "เมนู",
        [
            "Dashboard",
            "Recommendations",
            "Food Search",
            "My Likes",
            "Graph Explorer",
        ]
    )


# =========================
# HEADER
# =========================

st.markdown(
    """
    <div class="hero">

        <h1>
            🍜 Food Recommendation System
        </h1>

        <p>
            ระบบแนะนำอาหารด้วย Graph Database
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# USER SELECTOR
# =========================

def user_selector(key):

    users = get_users()

    if not users:

        st.warning(
            "ยังไม่มี User ใน Neo4j"
        )

        st.stop()

    labels = {
        f"{u['user_id']} — {u['name']}":
        u["user_id"]

        for u in users
    }

    selected = st.selectbox(
        "เลือกผู้ใช้",
        list(labels.keys()),
        key=key
    )

    return labels[selected]


# =========================
# SHOW IMAGE
# =========================

def show_food_image(
    image_name,
    width=220
):

    if not image_name:
        return

    path = os.path.join(
        "images",
        image_name
    )

    if os.path.exists(path):

        st.image(
            path,
            width=width
        )

    else:

        st.info(
            f"ยังไม่มีรูป {image_name}"
        )


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.subheader(
        "📊 ภาพรวมระบบ"
    )

    data = get_dashboard_metrics()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Users",
        data["users"]
    )

    c2.metric(
        "Foods",
        data["foods"]
    )

    c3.metric(
        "LIKES",
        data["likes"]
    )

    st.divider()

    user_id = user_selector(
        "dashboard_user"
    )

    likes = get_user_likes(
        user_id
    )

    st.subheader(
        "❤️ อาหารที่ผู้ใช้ชอบ"
    )

    if likes:

        cols = st.columns(
            min(3, len(likes))
        )

        for i, food in enumerate(likes):

            with cols[i % len(cols)]:

                show_food_image(
                    food["image"]
                )

                st.markdown(
                    f"### {food['name']}"
                )

    else:

        st.info(
            "ยังไม่มีอาหารที่ชอบ"
        )


# ==================================================
# RECOMMENDATION
# ==================================================

elif page == "Recommendations":

    st.subheader(
        "✨ อาหารที่แนะนำ"
    )

    user_id = user_selector(
        "recommend_user"
    )

    top_n = st.slider(
        "จำนวนคำแนะนำ",
        1,
        7,
        5
    )

    rows = recommend_foods(
        user_id,
        top_n
    )

    if not rows:

        st.info(
            "ยังไม่มีอาหารที่สามารถแนะนำได้"
        )

    else:

        for i, row in enumerate(
            rows,
            start=1
        ):

            col1, col2 = st.columns(
                [1, 3]
            )

            with col1:

                show_food_image(
                    row["image"]
                )

            with col2:

                st.markdown(
                    f"## #{i} {row['recommendation']}"
                )

                st.write(
                    f"Food ID: {row['food_id']}"
                )

                st.write(
                    f"⭐ Recommendation Score: "
                    f"{row['score']}"
                )

                users = ", ".join(
                    row["similar_users"]
                )

                if users:

                    st.write(
                        "👥 ผู้ใช้ที่มีความชอบคล้ายกัน: "
                        + users
                    )

            st.divider()


# ==================================================
# FOOD SEARCH
# ==================================================

elif page == "Food Search":

    st.subheader(
        "🔎 ค้นหาอาหาร"
    )

    keyword = st.text_input(
        "ค้นหาชื่ออาหาร"
    )

    foods = search_foods(
        keyword
    )

    st.write(
        f"พบ {len(foods)} รายการ"
    )

    cols = st.columns(3)

    for i, food in enumerate(foods):

        with cols[i % 3]:

            show_food_image(
                food["image"]
            )

            st.markdown(
                f"### {food['name']}"
            )

            st.caption(
                food["food_id"]
            )


# ==================================================
# MY LIKES
# ==================================================

elif page == "My Likes":

    st.subheader(
        "❤️ อาหารที่ผู้ใช้ชอบ"
    )

    user_id = user_selector(
        "likes_user"
    )

    foods = get_user_likes(
        user_id
    )

    if not foods:

        st.info(
            "ยังไม่มีอาหารที่ชอบ"
        )

    else:

        cols = st.columns(3)

        for i, food in enumerate(foods):

            with cols[i % 3]:

                show_food_image(
                    food["image"]
                )

                st.markdown(
                    f"### {food['name']}"
                )


# ==================================================
# GRAPH EXPLORER
# ==================================================

elif page == "Graph Explorer":

    st.subheader(
        "🕸️ Food Graph Explorer"
    )

    user_id = user_selector(
        "graph_user"
    )

    rows = get_graph(
        user_id
    )

    if not rows:

        st.info(
            "ยังไม่มีความสัมพันธ์ LIKES"
        )

    else:

        dot = [
            "digraph G {",
            'rankdir="LR";',
            'node [shape=box];'
        ]

        for row in rows:

            dot.append(
                f'"{row["source_id"]}" '
                f'[label="{row["source_name"]}\\nUser"];'
            )

            dot.append(
                f'"{row["target_id"]}" '
                f'[label="{row["target_name"]}\\nFood"];'
            )

            dot.append(
                f'"{row["source_id"]}" -> '
                f'"{row["target_id"]}" '
                f'[label="LIKES"];'
            )

        dot.append("}")

        st.graphviz_chart(
            "\n".join(dot),
            use_container_width=True
        )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )