from __future__ import annotations

from typing import Any

import streamlit as st
from neo4j import GraphDatabase


@st.cache_resource
def get_driver():
    uri = st.secrets["neo4j"]["uri"]
    username = st.secrets["neo4j"]["username"]
    password = st.secrets["neo4j"]["password"]

    return GraphDatabase.driver(
        uri,
        auth=(username, password)
    )


def run_query(
    cypher: str,
    parameters: dict[str, Any] | None = None
):
    database = st.secrets["neo4j"].get("database", "neo4j")

    driver = get_driver()

    with driver.session(database=database) as session:
        result = session.run(
            cypher,
            parameters or {}
        )

        return [record.data() for record in result]


# -----------------------------
# Connection
# -----------------------------

def ping():
    try:
        result = run_query("RETURN 1 AS ok")
        return len(result) > 0 and result[0]["ok"] == 1
    except Exception:
        return False


# -----------------------------
# Get Data
# -----------------------------

def get_users():
    return run_query("""
        MATCH (u:User)
        RETURN
            u.user_id AS user_id,
            u.name AS name
        ORDER BY u.user_id
    """)


def get_foods():
    return run_query("""
        MATCH (f:Food)
        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image
        ORDER BY f.food_id
    """)


def get_dashboard_metrics():
    result = run_query("""
        OPTIONAL MATCH (u:User)
        WITH count(u) AS users

        OPTIONAL MATCH (f:Food)
        WITH users, count(f) AS foods

        OPTIONAL MATCH ()-[r:LIKES]->()

        RETURN
            users,
            foods,
            count(r) AS likes
    """)

    if not result:
        return {
            "users": 0,
            "foods": 0,
            "likes": 0
        }

    return result[0]


def get_user_likes(user_id):
    return run_query("""
        MATCH (u:User {user_id: $user_id})
              -[:LIKES]->
              (f:Food)

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image

        ORDER BY f.name
    """, {
        "user_id": user_id
    })


# -----------------------------
# Recommendation
# -----------------------------

def recommend_foods(user_id, top_n=6):
    return run_query("""
        MATCH
            (me:User {user_id: $user_id})
            -[:LIKES]->(shared:Food)
            <-[:LIKES]-(similar:User)
            -[:LIKES]->(food:Food)

        WHERE
            similar <> me
            AND NOT (me)-[:LIKES]->(food)

        RETURN
            food.food_id AS food_id,
            food.name AS recommendation,
            food.image AS image,
            count(DISTINCT similar) AS score,
            collect(DISTINCT similar.name) AS similar_users

        ORDER BY score DESC, recommendation

        LIMIT $top_n
    """, {
        "user_id": user_id,
        "top_n": int(top_n)
    })


# -----------------------------
# Search
# -----------------------------

def search_foods(keyword=""):
    return run_query("""
        MATCH (f:Food)

        WHERE
            $keyword = ""
            OR toLower(f.name) CONTAINS toLower($keyword)

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image

        ORDER BY f.name
    """, {
        "keyword": keyword
    })


# -----------------------------
# Graph
# -----------------------------

def get_graph(user_id):
    return run_query("""
        MATCH
            (u:User {user_id: $user_id})
            -[r:LIKES]->
            (f:Food)

        RETURN
            u.user_id AS source_id,
            u.name AS source_name,
            "User" AS source_label,

            f.food_id AS target_id,
            f.name AS target_name,
            f.image AS image,
            "Food" AS target_label,

            type(r) AS relationship
    """, {
        "user_id": user_id
    })


# =====================================================
# ADMIN - ADD DATA
# =====================================================

def add_user(user_id, name):
    result = run_query("""
        CREATE (u:User {
            user_id: $user_id,
            name: $name
        })

        RETURN
            u.user_id AS user_id,
            u.name AS name
    """, {
        "user_id": user_id,
        "name": name
    })

    return result


def add_food(food_id, name, image):
    result = run_query("""
        CREATE (f:Food {
            food_id: $food_id,
            name: $name,
            image: $image
        })

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image
    """, {
        "food_id": food_id,
        "name": name,
        "image": image
    })

    return result


def add_like(user_id, food_id):
    result = run_query("""
        MATCH
            (u:User {user_id: $user_id}),
            (f:Food {food_id: $food_id})

        MERGE (u)-[:LIKES]->(f)

        RETURN
            u.name AS user,
            f.name AS food
    """, {
        "user_id": user_id,
        "food_id": food_id
    })

    return result


# =====================================================
# ADMIN - UPDATE DATA
# =====================================================

def update_user(user_id, new_name):
    result = run_query("""
        MATCH (u:User {
            user_id: $user_id
        })

        SET u.name = $new_name

        RETURN
            u.user_id AS user_id,
            u.name AS name
    """, {
        "user_id": user_id,
        "new_name": new_name
    })

    return result


def update_food(food_id, new_name, new_image):
    result = run_query("""
        MATCH (f:Food {
            food_id: $food_id
        })

        SET
            f.name = $new_name,
            f.image = $new_image

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image
    """, {
        "food_id": food_id,
        "new_name": new_name,
        "new_image": new_image
    })

    return result


# =====================================================
# ADMIN - DELETE DATA
# =====================================================

def delete_user(user_id):
    result = run_query("""
        MATCH (u:User {
            user_id: $user_id
        })

        DETACH DELETE u

        RETURN "deleted" AS status
    """, {
        "user_id": user_id
    })

    return result


def delete_food(food_id):
    result = run_query("""
        MATCH (f:Food {
            food_id: $food_id
        })

        DETACH DELETE f

        RETURN "deleted" AS status
    """, {
        "food_id": food_id
    })

    return result


def delete_like(user_id, food_id):
    result = run_query("""
        MATCH
            (u:User {user_id: $user_id})
            -[r:LIKES]->
            (f:Food {food_id: $food_id})

        DELETE r

        RETURN "deleted" AS status
    """, {
        "user_id": user_id,
        "food_id": food_id
    })

    return result