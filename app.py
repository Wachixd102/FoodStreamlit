from __future__ import annotations

import os
from pathlib import Path
import mimetypes

import pandas as pd
import streamlit as st

from neo4j_service import (
    add_food,
    add_like,
    add_user,
    delete_food,
    delete_like,
    delete_user,
    get_dashboard_metrics,
    get_foods,
    get_graph,
    get_user_likes,
    get_users,
    ping,
    recommend_foods,
    search_foods,
    update_food,
    update_user,
)


# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="Food Recommendation System",
    page_icon="🍜",
    layout="wide"
)


# =====================================================
# CSS
# =====================================================

st.markdown(r'''
<style>
.stApp{background:radial-gradient(circle at 10% 0%,rgba(255,159,67,.08),transparent 30%),radial-gradient(circle at 90% 10%,rgba(255,95,109,.06),transparent 28%),#08090c;color:#f5f5f5;}
.block-container{max-width:1500px;padding-top:2rem;padding-bottom:4rem;}
#MainMenu{visibility:hidden;} footer{visibility:hidden;}
.hero{position:relative;overflow:hidden;padding:34px 38px;border-radius:24px;margin-bottom:28px;border:1px solid rgba(255,255,255,.1);background:radial-gradient(circle at 85% 20%,rgba(255,180,80,.28),transparent 28%),linear-gradient(135deg,#17191f,#0d0f14 55%,#171115);box-shadow:0 20px 60px rgba(0,0,0,.35);}
.hero h1{margin:10px 0 0;font-size:42px;line-height:1.1;color:#fff;letter-spacing:-1px;} .hero p{margin:12px 0 0;color:#b8bec8;font-size:16px;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d0f13,#090a0d);border-right:1px solid rgba(255,255,255,.07);}
section[data-testid="stSidebar"] [data-testid="stRadio"] label{border-radius:12px;padding:7px 10px;transition:.2s;} section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(255,159,67,.09);}
h1,h2,h3{color:#fff!important;letter-spacing:-.3px;} p,label{color:#b8bec8;}
.card{padding:16px;border-radius:20px;border:1px solid rgba(255,255,255,.09);margin-bottom:18px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));box-shadow:0 14px 38px rgba(0,0,0,.22);transition:.2s;} .card:hover{transform:translateY(-4px);border-color:rgba(255,159,67,.3);box-shadow:0 20px 50px rgba(0,0,0,.34);}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#15181e,#0f1116);border:1px solid rgba(255,255,255,.09);border-radius:20px;padding:22px 24px;box-shadow:0 12px 35px rgba(0,0,0,.2);} div[data-testid="stMetricLabel"]{color:#9da3ae!important;} div[data-testid="stMetricValue"]{color:#fff!important;font-weight:750;}
div[data-baseweb="select"]>div,div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{background:#111318!important;color:#fff!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:12px!important;}
.stButton>button,.stFormSubmitButton>button{border:1px solid rgba(255,159,67,.3);border-radius:12px;background:linear-gradient(135deg,#ff9f43,#ff6b4a);color:#111;font-weight:750;min-height:42px;transition:.2s;} .stButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-1px);box-shadow:0 10px 28px rgba(255,110,65,.22);}
button[data-baseweb="tab"]{color:#9da3ae!important;font-weight:650;} button[data-baseweb="tab"][aria-selected="true"]{color:#ffb15a!important;} div[data-baseweb="tab-highlight"]{background:#ff9f43!important;}
div[data-testid="stDataFrame"]{border:1px solid rgba(255,255,255,.09);border-radius:16px;overflow:hidden;} hr{border-color:rgba(255,255,255,.08)!important;}
.food-image{width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:16px;margin-bottom:14px;background:#0b0d11;border:1px solid rgba(255,255,255,.07);}.food-image img{width:100%;height:100%;object-fit:contain;padding:6px;}
.premium-label{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(255,159,67,.1);border:1px solid rgba(255,159,67,.2);color:#ffb15a;font-size:12px;font-weight:700;letter-spacing:.5px;}
</style>
''',unsafe_allow_html=True)

# FUNCTIONS
# =====================================================

def show_food_image(image_name, width=220):
    if not image_name:
        st.info("ยังไม่มีรูปอาหาร")
        return

    image_path = Path(__file__).parent / "images" / image_name

    if image_path.exists():
        import base64
        mime_type, _ = mimetypes.guess_type(str(image_path))
        if not mime_type:
            mime_type = "image/jpeg"
        with open(image_path, "rb") as file:
            image_base64 = base64.b64encode(file.read()).decode()
        st.markdown(f'''
            <div class="food-image" style="height:{width}px;">
                <img src="data:{mime_type};base64,{image_base64}" alt="{image_name}">
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.warning(f"หารูปไม่เจอ: {image_name}")


def get_user_options():
    users = get_users()

    return {
        f"{user['user_id']} - {user['name']}":
        user["user_id"]
        for user in users
    }


def get_food_options():
    foods = get_foods()

    return {
        f"{food['food_id']} - {food['name']}":
        food["food_id"]
        for food in foods
    }


# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
<div class="hero">
<span class="premium-label">GRAPH-POWERED FOOD DISCOVERY</span>
<h1>🍜 Food Recommendation System</h1>
<p>ค้นพบเมนูที่เข้ากับคุณ ผ่านความสัมพันธ์ของผู้ใช้และอาหารบน Graph Database</p>
</div>
""",
    unsafe_allow_html=True
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("<div class='premium-label'>FOOD GRAPH</div><h2 style='margin:10px 0 4px;'>🍜 Discover</h2><div style='color:#8f96a3;font-size:13px;margin-bottom:14px;'>Food Recommendation System</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "เลือกหน้า",
    [
        "🏠 Dashboard",
        "🍱 Recommendations",
        "🔎 Food Search",
        "❤️ My Likes",
        "🕸️ Graph Explorer",
        "⚙️ จัดการข้อมูล"
    ]
)


# =====================================================
# CHECK DATABASE
# =====================================================

if not ping():

    st.error(
        "❌ ไม่สามารถเชื่อมต่อ Neo4j ได้"
    )

    st.stop()


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    st.markdown('<div class="premium-label">OVERVIEW</div>', unsafe_allow_html=True)
    st.header("🏠 Dashboard")
    st.caption("ภาพรวมข้อมูลผู้ใช้งาน อาหาร และความสัมพันธ์ในระบบ")

    metrics = get_dashboard_metrics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "👤 Users",
            metrics["users"]
        )

    with col2:
        st.metric(
            "🍜 Foods",
            metrics["foods"]
        )

    with col3:
        st.metric(
            "❤️ LIKES",
            metrics["likes"]
        )

    st.divider()

    st.subheader("👥 ผู้ใช้งาน")

    users = get_users()

    if users:

        df = pd.DataFrame(users)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("ยังไม่มีข้อมูล User")


# =====================================================
# RECOMMENDATIONS
# =====================================================

elif page == "🍱 Recommendations":

    st.markdown('<div class="premium-label">PERSONALIZED</div>', unsafe_allow_html=True)
    st.header("🍱 Food Recommendations")
    st.caption("ระบบแนะนำอาหารจากความชอบที่เชื่อมโยงกันของผู้ใช้งาน")

    user_options = get_user_options()

    if not user_options:

        st.warning("ยังไม่มี User")

        st.stop()

    selected_user = st.selectbox(
        "เลือกผู้ใช้",
        list(user_options.keys())
    )

    user_id = user_options[selected_user]

    st.divider()

    recommendations = recommend_foods(
        user_id,
        top_n=6
    )

    if not recommendations:

        st.info(
            "ยังไม่พบอาหารที่สามารถแนะนำได้"
        )

    else:

        st.subheader(
            f"อาหารที่แนะนำสำหรับ {selected_user}"
        )

        cols = st.columns(3)

        for index, food in enumerate(recommendations):

            with cols[index % 3]:

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                show_food_image(
                    food.get("image"),
                    width=220
                )

                st.subheader(
                    food["recommendation"]
                )

                st.write(
                    f"⭐ คะแนน: {food['score']}"
                )

                similar_users = food.get(
                    "similar_users",
                    []
                )

                if similar_users:

                    st.caption(
                        "ผู้ใช้ที่มีความชอบคล้ายกัน: "
                        + ", ".join(similar_users)
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =====================================================
# FOOD SEARCH
# =====================================================

elif page == "🔎 Food Search":

    st.markdown('<div class="premium-label">DISCOVER</div>', unsafe_allow_html=True)
    st.header("🔎 Food Search")
    st.caption("ค้นหาเมนูอาหารจากฐานข้อมูลของระบบ")

    keyword = st.text_input(
        "ค้นหาอาหาร",
        placeholder="เช่น Noodle, Pad Thai..."
    )

    foods = search_foods(keyword)

    if not foods:

        st.info("ไม่พบอาหาร")

    else:

        cols = st.columns(3)

        for index, food in enumerate(foods):

            with cols[index % 3]:

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                show_food_image(
                    food.get("image"),
                    width=220
                )

                st.subheader(
                    food["name"]
                )

                st.caption(
                    f"Food ID: {food['food_id']}"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =====================================================
# MY LIKES
# =====================================================

elif page == "❤️ My Likes":

    st.markdown('<div class="premium-label">YOUR COLLECTION</div>', unsafe_allow_html=True)
    st.header("❤️ My Likes")
    st.caption("รวมเมนูอาหารที่ผู้ใช้งานเลือกถูกใจ")

    user_options = get_user_options()

    if not user_options:

        st.warning("ยังไม่มี User")

        st.stop()

    selected_user = st.selectbox(
        "เลือกผู้ใช้",
        list(user_options.keys())
    )

    user_id = user_options[selected_user]

    st.divider()

    likes = get_user_likes(user_id)

    if not likes:

        st.info(
            "ผู้ใช้นี้ยังไม่มีอาหารที่กด Like"
        )

    else:

        st.subheader(
            f"อาหารที่ {selected_user} ชอบ"
        )

        cols = st.columns(3)

        for index, food in enumerate(likes):

            with cols[index % 3]:

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                show_food_image(
                    food.get("image"),
                    width=220
                )

                st.subheader(
                    food["name"]
                )

                st.caption(
                    f"Food ID: {food['food_id']}"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =====================================================
# GRAPH EXPLORER
# =====================================================

elif page == "🕸️ Graph Explorer":

    st.markdown('<div class="premium-label">GRAPH VIEW</div>', unsafe_allow_html=True)
    st.header("🕸️ Graph Explorer")
    st.caption("สำรวจความสัมพันธ์ระหว่าง User และ Food")

    user_options = get_user_options()

    if not user_options:
        st.warning("ยังไม่มี User")
        st.stop()

    selected_user = st.selectbox(
        "เลือกผู้ใช้",
        list(user_options.keys())
    )

    user_id = user_options[selected_user]

    graph_data = get_graph(user_id)

    if not graph_data:

        st.info(
            "User คนนี้ยังไม่มีความสัมพันธ์ LIKES"
        )

    else:

        st.subheader("🕸️ ความสัมพันธ์ User → Food")

        cols = st.columns(3)

        for i, item in enumerate(graph_data):

            with cols[i % 3]:

                # -------------------------
                # ข้อมูลอาหาร
                # -------------------------

                food_name = item.get("target_name", "ไม่ทราบชื่อ")
                image_name = item.get("image", "")

                st.markdown(
                    f"### 🍽️ {food_name}"
                )

                st.caption(
                    f"รูป: {image_name}"
                )

                # -------------------------
                # โหลดรูป
                # -------------------------

                if image_name:

                    image_path = (
                        Path(__file__).parent
                        / "images"
                        / image_name
                    )

                    if image_path.exists():

                        st.image(
                            str(image_path),
                            width=220
                        )

                    else:

                        st.error(
                            f"❌ หาไฟล์ไม่เจอ\n\n"
                            f"{image_path}"
                        )

                else:

                    st.warning(
                        "⚠️ Food นี้ไม่มีชื่อไฟล์รูปใน Neo4j"
                    )

                st.caption(
                    f"❤️ {item.get('relationship', 'LIKES')}"
                )

        st.divider()

        st.subheader("📋 ข้อมูลความสัมพันธ์")

        df = pd.DataFrame(graph_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# ADMIN / CRUD
# =====================================================

elif page == "⚙️ จัดการข้อมูล":

    st.markdown('<div class="premium-label">ADMIN CONTROL</div>', unsafe_allow_html=True)
    st.header("⚙️ จัดการข้อมูล")
    st.caption("จัดการ User, Food และความสัมพันธ์ LIKES")

    st.info(
        "หน้านี้ใช้สำหรับ เพิ่ม / แก้ไข / ลบข้อมูลในระบบ"
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "➕ เพิ่มข้อมูล",
            "✏️ แก้ไขข้อมูล",
            "🗑️ ลบข้อมูล",
            "❤️ จัดการ LIKES"
        ]
    )

    # =================================================
    # ADD
    # =================================================

    with tab1:

        st.subheader("👤 เพิ่ม User")

        with st.form("add_user_form"):

            user_id = st.text_input(
                "User ID",
                placeholder="เช่น U006"
            )

            user_name = st.text_input(
                "ชื่อ User",
                placeholder="เช่น Somchai"
            )

            submit_user = st.form_submit_button(
                "➕ เพิ่ม User"
            )

            if submit_user:

                if not user_id or not user_name:

                    st.error(
                        "กรุณากรอกข้อมูลให้ครบ"
                    )

                else:

                    try:

                        result = add_user(
                            user_id,
                            user_name
                        )

                        if result:

                            st.success(
                                "เพิ่ม User สำเร็จ"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "ไม่สามารถเพิ่ม User ได้"
                            )

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

        st.divider()

        st.subheader("🍜 เพิ่ม Food")

        with st.form("add_food_form"):

            food_id = st.text_input(
                "Food ID",
                placeholder="เช่น F008"
            )

            food_name = st.text_input(
                "ชื่ออาหาร",
                placeholder="เช่น Tom Yum"
            )

            image_file = st.file_uploader(
                "เลือกรูปอาหาร",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ]
            )

            submit_food = st.form_submit_button(
                "➕ เพิ่ม Food"
            )

            if submit_food:

                if not food_id or not food_name:

                    st.error(
                        "กรุณากรอก Food ID และชื่ออาหาร"
                    )

                else:

                    image_name = ""

                    if image_file:

                        image_name = image_file.name

                        image_folder = (
                            Path(__file__).parent
                            / "images"
                        )

                        image_folder.mkdir(
                            exist_ok=True
                        )

                        image_path = (
                            image_folder
                            / image_name
                        )

                        with open(
                            image_path,
                            "wb"
                        ) as file:

                            file.write(
                                image_file.getbuffer()
                            )

                    try:

                        result = add_food(
                            food_id,
                            food_name,
                            image_name
                        )

                        if result:

                            st.success(
                                "เพิ่ม Food สำเร็จ"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "ไม่สามารถเพิ่ม Food ได้"
                            )

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

        st.divider()

        st.subheader("❤️ เพิ่มความสัมพันธ์ LIKES")

        user_options = get_user_options()
        food_options = get_food_options()

        if user_options and food_options:

            with st.form("add_like_form"):

                selected_user = st.selectbox(
                    "User",
                    list(user_options.keys())
                )

                selected_food = st.selectbox(
                    "Food",
                    list(food_options.keys())
                )

                submit_like = st.form_submit_button(
                    "❤️ เพิ่ม LIKES"
                )

                if submit_like:

                    try:

                        result = add_like(
                            user_options[selected_user],
                            food_options[selected_food]
                        )

                        if result:

                            st.success(
                                "เพิ่ม LIKES สำเร็จ"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "ไม่สามารถเพิ่ม LIKES ได้"
                            )

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

        else:

            st.info(
                "ต้องมี User และ Food ก่อน"
            )


    # =================================================
    # UPDATE
    # =================================================

    with tab2:

        st.subheader("✏️ แก้ไข User")

        user_options = get_user_options()

        if user_options:

            selected_user = st.selectbox(
                "เลือก User ที่ต้องการแก้ไข",
                list(user_options.keys()),
                key="edit_user"
            )

            selected_user_id = user_options[
                selected_user
            ]

            current_name = selected_user.split(
                " - ",
                1
            )[1]

            new_name = st.text_input(
                "ชื่อใหม่",
                value=current_name
            )

            if st.button(
                "💾 บันทึก User",
                key="save_user"
            ):

                if not new_name:

                    st.error(
                        "กรุณากรอกชื่อ"
                    )

                else:

                    try:

                        result = update_user(
                            selected_user_id,
                            new_name
                        )

                        if result:

                            st.success(
                                "แก้ไข User สำเร็จ"
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

        st.divider()

        st.subheader("✏️ แก้ไข Food")

        food_options = get_food_options()

        if food_options:

            selected_food = st.selectbox(
                "เลือก Food ที่ต้องการแก้ไข",
                list(food_options.keys()),
                key="edit_food"
            )

            selected_food_id = food_options[
                selected_food
            ]

            foods = get_foods()

            current_food = next(
                (
                    food
                    for food in foods
                    if food["food_id"]
                    == selected_food_id
                ),
                None
            )

            if current_food:

                show_food_image(
                    current_food.get("image"),
                    width=200
                )

                new_food_name = st.text_input(
                    "ชื่ออาหารใหม่",
                    value=current_food["name"]
                )

                new_image_file = st.file_uploader(
                    "เปลี่ยนรูปอาหาร (ถ้าต้องการ)",
                    type=[
                        "jpg",
                        "jpeg",
                        "png",
                        "webp"
                    ],
                    key="edit_image"
                )

                if st.button(
                    "💾 บันทึก Food",
                    key="save_food"
                ):

                    image_name = current_food.get(
                        "image",
                        ""
                    )

                    if new_image_file:

                        image_name = new_image_file.name

                        image_folder = (
                            Path(__file__).parent
                            / "images"
                        )

                        image_folder.mkdir(
                            exist_ok=True
                        )

                        image_path = (
                            image_folder
                            / image_name
                        )

                        with open(
                            image_path,
                            "wb"
                        ) as file:

                            file.write(
                                new_image_file.getbuffer()
                            )

                    try:

                        result = update_food(
                            selected_food_id,
                            new_food_name,
                            image_name
                        )

                        if result:

                            st.success(
                                "แก้ไข Food สำเร็จ"
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )


    # =================================================
    # DELETE
    # =================================================

    with tab3:

        st.subheader("🗑️ ลบ User")

        user_options = get_user_options()

        if user_options:

            selected_user = st.selectbox(
                "เลือก User ที่ต้องการลบ",
                list(user_options.keys()),
                key="delete_user"
            )

            selected_user_id = user_options[
                selected_user
            ]

            confirm_user = st.checkbox(
                "ฉันยืนยันว่าต้องการลบ User นี้",
                key="confirm_delete_user"
            )

            if st.button(
                "🗑️ ลบ User",
                key="delete_user_button"
            ):

                if not confirm_user:

                    st.warning(
                        "กรุณาติ๊กยืนยันก่อนลบ"
                    )

                else:

                    try:

                        delete_user(
                            selected_user_id
                        )

                        st.success(
                            "ลบ User สำเร็จ"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

        st.divider()

        st.subheader("🗑️ ลบ Food")

        food_options = get_food_options()

        if food_options:

            selected_food = st.selectbox(
                "เลือก Food ที่ต้องการลบ",
                list(food_options.keys()),
                key="delete_food"
            )

            selected_food_id = food_options[
                selected_food
            ]

            confirm_food = st.checkbox(
                "ฉันยืนยันว่าต้องการลบ Food นี้",
                key="confirm_delete_food"
            )

            if st.button(
                "🗑️ ลบ Food",
                key="delete_food_button"
            ):

                if not confirm_food:

                    st.warning(
                        "กรุณาติ๊กยืนยันก่อนลบ"
                    )

                else:

                    try:

                        delete_food(
                            selected_food_id
                        )

                        st.success(
                            "ลบ Food สำเร็จ"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )


    # =================================================
    # LIKES MANAGEMENT
    # =================================================

    with tab4:

        st.subheader("❤️ ลบความสัมพันธ์ LIKES")

        user_options = get_user_options()

        if user_options:

            selected_user = st.selectbox(
                "เลือก User",
                list(user_options.keys()),
                key="like_user"
            )

            selected_user_id = user_options[
                selected_user
            ]

            likes = get_user_likes(
                selected_user_id
            )

            if likes:

                food_options = {
                    f"{food['food_id']} - {food['name']}":
                    food["food_id"]
                    for food in likes
                }

                selected_food = st.selectbox(
                    "เลือก Food ที่ต้องการเอา Like ออก",
                    list(food_options.keys())
                )

                if st.button(
                    "💔 ลบ LIKES"
                ):

                    try:

                        delete_like(
                            selected_user_id,
                            food_options[selected_food]
                        )

                        st.success(
                            "ลบ LIKES สำเร็จ"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"เกิดข้อผิดพลาด: {e}"
                        )

            else:

                st.info(
                    "User คนนี้ยังไม่มี LIKES"
                )