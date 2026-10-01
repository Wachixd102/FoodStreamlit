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
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
:root{--gold:#d6b36a;--gold2:#f1d99b;--cream:#f4efe4;--line:rgba(214,179,106,.24)}
.stApp{background:radial-gradient(circle at 15% 0%,rgba(214,179,106,.10),transparent 24%),linear-gradient(135deg,#070706,#0d0d0b 48%,#080807);color:var(--cream);font-family:'Inter',sans-serif}
.block-container{max-width:1480px;padding:2.2rem 3rem 5rem;animation:pageIn .7s ease both}
@keyframes pageIn{from{opacity:0;transform:translateY(16px);filter:blur(3px)}to{opacity:1;transform:none;filter:none}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes shimmer{0%,100%{opacity:.45}50%{opacity:1}}
#MainMenu,footer{visibility:hidden}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(21,20,16,.98),rgba(7,7,6,.99));border-right:1px solid var(--line)}
section[data-testid="stSidebar"]>div{padding:1.4rem .85rem}
section[data-testid="stSidebar"] [data-testid="stRadio"]>div{gap:7px}
section[data-testid="stSidebar"] [data-testid="stRadio"] label{border:1px solid transparent;border-radius:14px;padding:10px 12px;color:#aaa59a;transition:all .25s ease}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{color:var(--gold2);background:rgba(214,179,106,.07);border-color:rgba(214,179,106,.14);transform:translateX(3px)}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"]{color:#17130b;background:linear-gradient(135deg,var(--gold2),var(--gold));box-shadow:0 8px 24px rgba(214,179,106,.16)}
h1,h2,h3,h4{font-family:'Cormorant Garamond',serif!important;color:#f7f0df!important;letter-spacing:.2px}
h1{font-size:3rem!important}h2{font-size:2rem!important}h3{font-size:1.45rem!important}
p,label,.stCaption{color:#b9b3a7}
.luxury-hero{position:relative;min-height:330px;overflow:hidden;border:1px solid var(--line);border-radius:2px;margin-bottom:38px;padding:58px 62px;display:flex;align-items:flex-end;background:linear-gradient(90deg,rgba(5,5,4,.97),rgba(5,5,4,.88) 45%,rgba(5,5,4,.42)),radial-gradient(circle at 78% 48%,rgba(214,179,106,.24),transparent 22%),linear-gradient(135deg,#211d13,#0b0b09 60%,#18150e);box-shadow:0 28px 80px rgba(0,0,0,.48)}
.luxury-hero:before{content:'';position:absolute;inset:18px;border:1px solid rgba(214,179,106,.20);pointer-events:none}
.luxury-hero:after{content:'✦';position:absolute;right:8%;top:18%;font-size:130px;color:rgba(214,179,106,.10);animation:shimmer 4s ease-in-out infinite}
.hero-copy{position:relative;z-index:2;max-width:760px}
.eyebrow{display:inline-flex;align-items:center;gap:10px;color:var(--gold2);font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase}
.eyebrow:before{content:'';width:38px;height:1px;background:var(--gold)}
.hero-title{margin:12px 0 4px!important;font-size:58px!important;line-height:.94!important;text-transform:uppercase}
.hero-sub{font-size:15px;color:#c4bfb4;max-width:650px;margin-top:18px}.gold-rule{height:1px;background:linear-gradient(90deg,var(--gold),transparent);margin:22px 0 30px}
.section-kicker{color:var(--gold);font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:4px}
.card{padding:18px;border-radius:2px;border:1px solid rgba(214,179,106,.16);margin-bottom:20px;background:linear-gradient(145deg,#171713,#0d0d0b);box-shadow:0 16px 42px rgba(0,0,0,.28);transition:all .35s cubic-bezier(.2,.8,.2,1);animation:rise .55s ease both}
.card:hover{transform:translateY(-8px);border-color:rgba(214,179,106,.52);box-shadow:0 24px 60px rgba(0,0,0,.45)}
.food-image{width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:1px;margin-bottom:16px;background:#080807;border:1px solid rgba(255,255,255,.08);position:relative}
.food-image:after{content:'';position:absolute;inset:0;border:1px solid rgba(214,179,106,.10);pointer-events:none}
.food-image img{width:100%;height:100%;object-fit:contain;padding:7px;transition:transform .5s ease}.card:hover .food-image img{transform:scale(1.035)}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#171612,#0d0d0b);border:1px solid rgba(214,179,106,.18);border-radius:2px;padding:22px 24px;box-shadow:0 15px 40px rgba(0,0,0,.25)}
div[data-testid="stMetricLabel"]{color:#aaa397!important;text-transform:uppercase;letter-spacing:1.5px;font-size:10px!important}
div[data-testid="stMetricValue"]{color:var(--gold2)!important;font-family:'Cormorant Garamond',serif;font-size:38px!important}
div[data-baseweb="select"]>div,div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stFileUploaderDropzone"]{background:#10100e!important;color:#f4efe4!important;border:1px solid rgba(214,179,106,.18)!important;border-radius:2px!important}
.stButton>button,.stFormSubmitButton>button{border:1px solid var(--gold)!important;border-radius:2px!important;background:linear-gradient(135deg,#e7ca8c,#b9954e)!important;color:#17130b!important;font-weight:700!important;min-height:43px;letter-spacing:.5px;transition:all .25s ease!important}
.stButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(214,179,106,.22)}
button[data-baseweb="tab"]{color:#8f8a80!important;font-weight:600!important}button[data-baseweb="tab"][aria-selected="true"]{color:var(--gold2)!important}div[data-baseweb="tab-highlight"]{background:var(--gold)!important}
div[data-testid="stDataFrame"]{border:1px solid rgba(214,179,106,.16);border-radius:2px;overflow:hidden}hr{border-color:rgba(214,179,106,.16)!important}
.premium-label{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(214,179,106,.07);border:1px solid rgba(214,179,106,.20);color:var(--gold2);font-size:10px;font-weight:700;letter-spacing:2px}
.menu-note{color:#79746b;font-size:10px;letter-spacing:2px;text-transform:uppercase;padding:12px 5px;border-top:1px solid rgba(214,179,106,.14);margin-top:18px}
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
<div class="luxury-hero">
<div class="hero-copy">
<div class="eyebrow">THE DINING CONCIERGE</div>
<h1 class="hero-title">Food<br>Recommendation</h1>
<div class="gold-rule"></div>
<div class="hero-sub">A refined dining discovery experience, powered by Graph Database.</div>
</div>
</div>
""",
    unsafe_allow_html=True
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown('<div style="padding:8px 8px 18px;"><div class="eyebrow" style="font-size:9px;letter-spacing:2px;">PRIVATE DINING</div><div style="font-family:Cormorant Garamond;font-size:30px;color:#f4efe4;margin-top:7px;">Maison<br>Gastronomique</div><div style="color:#777269;font-size:10px;letter-spacing:2px;margin-top:8px;">FOOD DISCOVERY CONCIERGE</div></div>', unsafe_allow_html=True)

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
st.sidebar.markdown("<div class='menu-note'>Curated dining experience<br>Graph intelligence • Neo4j</div>", unsafe_allow_html=True)



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

    st.markdown('<div class="section-kicker">01 · HOUSE OVERVIEW</div>', unsafe_allow_html=True)
    st.header("The Dining House")
    st.caption("ภาพรวมของแขก เมนู และเครือข่ายความชอบภายในระบบ")

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

    st.subheader("Guest Registry")

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

    st.markdown("<div class='section-kicker'>02 · CHEF'S SELECTION</div>", unsafe_allow_html=True)
    st.header("Curated For You")
    st.caption("เมนูที่คัดสรรจากรูปแบบความชอบของแขกที่มีรสนิยมใกล้เคียงกัน")

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

    st.markdown('<div class="section-kicker">03 · THE MENU</div>', unsafe_allow_html=True)
    st.header("The Dining Menu")
    st.caption("สำรวจเมนูทั้งหมดจาก collection ของห้องอาหาร")

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

    st.markdown('<div class="section-kicker">04 · YOUR TABLE</div>', unsafe_allow_html=True)
    st.header("Your Dining Collection")
    st.caption("เมนูที่แขกบันทึกไว้เป็นรายการโปรด")

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

    st.markdown('<div class="section-kicker">05 · THE CONNECTIONS</div>', unsafe_allow_html=True)
    st.header("Dining Connections")
    st.caption("สำรวจสายสัมพันธ์ระหว่างแขกและเมนูผ่าน Graph Database")

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

        st.subheader("Guest → Menu Connections")

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

        st.subheader("Connection Ledger")

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

    st.markdown('<div class="section-kicker">06 · HOUSE MANAGEMENT</div>', unsafe_allow_html=True)
    st.header("House Management")
    st.caption("จัดการแขก เมนู และความสัมพันธ์ภายในระบบ")

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