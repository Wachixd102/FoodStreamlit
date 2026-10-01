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
    initial_sidebar_state="expanded",
)


# =========================
# STYLE
# =========================

st.markdown(
    """
    <style>
      .block-container {
          padding-top: 1.3rem;
          padding-bottom: 2rem;
      }

      .hero {
          padding: 1.5rem 1.7rem;
          border-radius: 22px;
          background: linear-gradient(
              120deg,
              #111827 0%,
              #1f2937 55%,
              #0f766e 100%
          );
          color: white;
          margin-bottom: 1rem;
      }

      .hero h1 {
          margin: 0;
          font-size: 2.2rem;
      }

      .hero p {
          opacity: .88;
          margin: .4rem 0 0 0;
      }

      .food-card {
          padding: 1rem;
          border: 1px solid rgba(128,128,128,.25);
          border-radius: 16px;
          margin-bottom: .8rem;
      }

      .score-pill {
          display: inline-block;
          padding: .2rem .6rem;
          border-radius: 999px;
          background: #0f766e;
          color: white;
          font-size: .8rem;
          font-weight: 700;
      }

      .muted {
          opacity: .72;
          font-size: .9rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# NEO4J CONNECTION
# =========================

@st.cache_resource
def get_driver():
    uri = st.secrets["neo4j"]["uri"]
    username = st.secrets["neo4j"]["username"]
    password = st.secrets["neo4j"]["password"]

    return GraphDatabase.driver(
        uri,
        auth=(username, password)
    )


def run_query(query, parameters=None):
    driver = get_driver()

    with driver.session(
        database=st.secrets["neo4j"].get("database", "neo4j")
    ) as session:
        result = session.run(
            query,
            parameters or {}
        )
        return [record.data() for record in result]


def ping():
    try:
        run_query("RETURN 1 AS ok")
        return True
    except Exception:
        return False


# =========================
# NEO4J FUNCTIONS
# =========================

def get_users():

    query = """
    MATCH (u:User)
    RETURN
        u.user_id AS user_id,
        u.name AS name
    ORDER BY u.user_id
    """

    return run_query(query)


def get_foods():

    query = """
    MATCH (f:Food)
    RETURN
        f.food_id AS food_id,
        f.name AS name,
        f.image AS image
    ORDER BY f.food_id
    """

    return run_query(query)


def get_dashboard_metrics():

    query = """
    OPTIONAL MATCH (u:User)
    WITH count(u) AS users

    OPTIONAL MATCH (f:Food)
    WITH users, count(f) AS foods

    OPTIONAL MATCH ()-[r:LIKES]->()
    RETURN
        users,
        foods,
        count(r) AS likes
    """

    rows = run_query(query)

    if not rows:
        return {
            "users": 0,
            "foods": 0,
            "likes": 0
        }

    return rows[0]


def get_user_likes(user_id):

    query = """
    MATCH (u:User {user_id: $user_id})
          -[:LIKES]->(f:Food)

    RETURN
        f.food_id AS food_id,
        f.name AS name,
        f.image AS image

    ORDER BY f.name
    """

    return run_query(
        query,
        {"user_id": user_id}
    )


def recommend_foods(user_id, top_n=6):

    query = """
    MATCH
        (me:User {user_id: $user_id})
        -[:LIKES]->(shared:Food)
        <-[:LIKES]-(similar:User)
        -[:LIKES]->(food:Food)

    WHERE similar <> me
      AND NOT (me)-[:LIKES]->(food)

    RETURN
        food.food_id AS food_id,
        food.name AS recommendation,
        food.image AS image,
        count(DISTINCT similar) AS score,
        collect(DISTINCT similar.name) AS similar_users

    ORDER BY score DESC, recommendation

    LIMIT $top_n
    """

    return run_query(
        query,
        {
            "user_id": user_id,
            "top_n": top_n
        }
    )


def search_foods(keyword=""):

    query = """
    MATCH (f:Food)

    WHERE
        $keyword = ""
        OR toLower(f.name) CONTAINS toLower($keyword)

    RETURN
        f.food_id AS food_id,
        f.name AS name,
        f.image AS image

    ORDER BY f.name
    """

    return run_query(
        query,
        {"keyword": keyword}
    )


def get_graph(user_id):

    query = """
    MATCH
        (u:User {user_id: $user_id})
        -[r:LIKES]->(f:Food)

    RETURN
        u.user_id AS source_id,
        u.name AS source_name,
        "User" AS source_label,

        f.food_id AS target_id,
        f.name AS target_name,
        "Food" AS target_label,

        type(r) AS relationship
    """

    return run_query(
        query,
        {"user_id": user_id}
    )


# =========================
# IMAGE
# =========================

def show_food_image(image_name, width=220):

    if not image_name:
        return

    image_path = os.path.join(
        "images",
        image_name
    )

    if os.path.exists(image_path):
        st.image(
            image_path,
            width=width
        )
    else:
        st.info(
            f"ยังไม่มีรูป {image_name}"
        )


# =========================
# CONNECTION CHECK
# =========================

if not ping():

    st.error(
        "❌ ยังเชื่อมต่อ Neo4j Aura ไม่สำเร็จ"
    )

    st.code(
        """
[neo4j]
uri = "neo4j+s://YOUR_INSTANCE.databases.neo4j.io"
username = "neo4j"
password = "YOUR_PASSWORD"
database = "neo4j"
        """,
        language="toml"
    )

    st.caption(
        "ใส่ข้อมูล Neo4j Aura ใน Streamlit Secrets และห้ามใส่ Password ลง GitHub"
    )

    st.stop()


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown("## 🍜 Food Recommendation")

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
            "Graph Explorer"
        ]
    )

    st.divider()

    st.caption(
        "Food Recommendation System"
    )


# =========================
# HEADER
# =========================

st.markdown(
    """
    <div class="hero">
        <h1>🍜 Food Recommendation System</h1>
        <p>
            ระบบแนะนำอาหารด้วย Graph Database
            โดยใช้ความชอบของผู้ใช้ในการสร้างคำแนะนำ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# USER SELECTOR
# =========================

def user_selector(key):

    users = get_users()

    if not users:
        st.warning(
            "ยังไม่มีข้อมูล User ใน Neo4j"
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
# DASHBOARD
# =========================

if page == "Dashboard":

    st.subheader("📊 ภาพรวมระบบ")

    metrics = get_dashboard_metrics()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Users",
        metrics["users"]
    )

    c2.metric(
        "Foods",
        metrics["foods"]
    )

    c3.metric(
        "LIKES",
        metrics["likes"]
    )

    st.divider()

    st.subheader("👤 ข้อมูลผู้ใช้")

    user_id = user_selector(
        "dashboard_user"
    )

    users = get_users()

    selected_user = next(
        (
            u for u in users
            if u["user_id"] == user_id
        ),
        None
    )

    if selected_user:

        st.markdown(
            f"### {selected_user['name']}"
        )

        st.write(
            f"**User ID:** {selected_user['user_id']}"
        )

        likes = get_user_likes(user_id)

        st.markdown(
            "#### ❤️ อาหารที่ชอบ"
        )

        if likes:

            cols = st.columns(
                min(len(likes), 3)
            )

            for i, food in enumerate(likes):

                with cols[i % len(cols)]:

                    show_food_image(
                        food["image"],
                        width=180
                    )

                    st.write(
                        f"**{food['name']}**"
                    )

        else:

            st.info(
                "ผู้ใช้นี้ยังไม่มีอาหารที่ชอบ"
            )


# =========================
# RECOMMENDATIONS
# =========================

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

    st.caption(
        "Score = จำนวนผู้ใช้ที่มีความชอบร่วมกันและชอบอาหารที่แนะนำ"
    )

    if not rows:

        st.info(
            "ยังไม่มีคำแนะนำสำหรับผู้ใช้นี้"
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
                    row["image"],
                    width=200
                )

            with col2:

                st.markdown(
                    f"""
                    <span class="score-pill">
                    #{i} · Score {row['score']}
                    </span>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"### {row['recommendation']}"
                )

                st.write(
                    f"Food ID: {row['food_id']}"
                )

                similar_users = ", ".join(
                    row.get("similar_users") or []
                )

                if similar_users:

                    st.write(
                        "👥 ผู้ใช้ที่มีความชอบคล้ายกัน: "
                        + similar_users
                    )

                st.markdown("---")


# =========================
# FOOD SEARCH
# =========================

elif page == "Food Search":

    st.subheader(
        "🔎 ค้นหาอาหาร"
    )

    keyword = st.text_input(
        "ชื่ออาหาร",
        placeholder="เช่น Noodle, Fried Rice"
    )

    foods = search_foods(
        keyword
    )

    st.write(
        f"พบ {len(foods)} รายการ"
    )

    if foods:

        cols = st.columns(3)

        for i, food in enumerate(foods):

            with cols[i % 3]:

                show_food_image(
                    food["image"],
                    width=220
                )

                st.markdown(
                    f"### {food['name']}"
                )

                st.caption(
                    food["food_id"]
                )

                st.divider()


# =========================
# MY LIKES
# =========================

elif page == "My Likes":

    st.subheader(
        "❤️ อาหารที่ผู้ใช้ชอบ"
    )

    user_id = user_selector(
        "likes_user"
    )

    likes = get_user_likes(
        user_id
    )

    if not likes:

        st.info(
            "ผู้ใช้นี้ยังไม่มีอาหารที่ชอบ"
        )

    else:

        cols = st.columns(
            min(len(likes), 3)
        )

        for i, food in enumerate(likes):

            with cols[i % len(cols)]:

                show_food_image(
                    food["image"],
                    width=220
                )

                st.markdown(
                    f"### {food['name']}"
                )

                st.caption(
                    food["food_id"]
                )


# =========================
# GRAPH EXPLORER
# =========================

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
            'node [shape=box, style="rounded,filled"];'
        ]

        seen_nodes = set()

        for row in rows:

            source_id = row["source_id"]
            target_id = row["target_id"]

            if source_id not in seen_nodes:

                safe_name = str(
                    row["source_name"]
                ).replace('"', "'")

                dot.append(
                    f'"{source_id}" '
                    f'[label="{safe_name}\\nUser"];'
                )

                seen_nodes.add(
                    source_id
                )

            if target_id not in seen_nodes:

                safe_name = str(
                    row["target_name"]
                ).replace('"', "'")

                dot.append(
                    f'"{target_id}" '
                    f'[label="{safe_name}\\nFood"];'
                )

                seen_nodes.add(
                    target_id
                )

            dot.append(
                f'"{source_id}" -> '
                f'"{target_id}" '
                f'[label="LIKES"];'
            )

        dot.append("}")

        st.graphviz_chart(
            "\n".join(dot),
            use_container_width=True
        )

        with st.expander(
            "ดูข้อมูลความสัมพันธ์"
        ):

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )