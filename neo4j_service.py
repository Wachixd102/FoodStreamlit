from __future__ import annotations

from typing import Any

import streamlit as st
from neo4j import GraphDatabase, RoutingControl


# =========================
# NEO4J CONFIG
# =========================

def _config() -> tuple[str, str, str, str]:
    cfg = st.secrets["neo4j"]

    return (
        cfg["uri"],
        cfg["username"],
        cfg["password"],
        cfg.get("database", "neo4j"),
    )


# =========================
# NEO4J DRIVER
# =========================

@st.cache_resource(show_spinner=False)
def get_driver():

    uri, username, password, _ = _config()

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()

    return driver


# =========================
# RUN QUERY
# =========================

def query(
    cypher: str,
    parameters: dict[str, Any] | None = None,
    *,
    write: bool = False
) -> list[dict[str, Any]]:

    _, _, _, database = _config()

    records, _, _ = get_driver().execute_query(
        cypher,
        parameters_=parameters or {},
        database_=database,
        routing_=(
            RoutingControl.WRITE
            if write
            else RoutingControl.READ
        ),
    )

    return [
        record.data()
        for record in records
    ]


# =========================
# TEST CONNECTION
# =========================

def ping() -> bool:

    try:

        rows = query(
            "RETURN 1 AS ok"
        )

        return bool(
            rows
            and rows[0]["ok"] == 1
        )

    except Exception:

        return False


# =========================
# GET USERS
# =========================

def get_users() -> list[dict[str, Any]]:

    return query(
        """
        MATCH (u:User)

        RETURN
            u.user_id AS user_id,
            u.name AS name

        ORDER BY u.user_id
        """
    )


# =========================
# GET FOODS
# =========================

def get_foods() -> list[dict[str, Any]]:

    return query(
        """
        MATCH (f:Food)

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image

        ORDER BY f.food_id
        """
    )


# =========================
# DASHBOARD METRICS
# =========================

def get_dashboard_metrics() -> dict[str, int]:

    rows = query(
        """
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
    )

    if not rows:

        return {
            "users": 0,
            "foods": 0,
            "likes": 0,
        }

    return rows[0]


# =========================
# USER LIKES
# =========================

def get_user_likes(
    user_id: str
) -> list[dict[str, Any]]:

    return query(
        """
        MATCH
            (u:User {user_id: $user_id})
            -[:LIKES]->
            (f:Food)

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image

        ORDER BY f.name
        """,
        {
            "user_id": user_id
        },
    )


# =========================
# FOOD RECOMMENDATION
# =========================

def recommend_foods(
    user_id: str,
    limit: int = 6
) -> list[dict[str, Any]]:

    return query(
        """
        MATCH
            (me:User {user_id: $user_id})
            -[:LIKES]->
            (shared:Food)
            <-[:LIKES]-
            (similar:User)
            -[:LIKES]->
            (food:Food)

        WHERE
            similar <> me
            AND NOT (me)-[:LIKES]->(food)

        RETURN
            food.food_id AS food_id,
            food.name AS recommendation,
            food.image AS image,

            count(
                DISTINCT similar
            ) AS score,

            collect(
                DISTINCT similar.name
            ) AS similar_users

        ORDER BY
            score DESC,
            recommendation

        LIMIT $limit
        """,
        {
            "user_id": user_id,
            "limit": int(limit),
        },
    )


# =========================
# SEARCH FOOD
# =========================

def search_foods(
    keyword: str = ""
) -> list[dict[str, Any]]:

    return query(
        """
        MATCH (f:Food)

        WHERE
            $keyword = ""
            OR toLower(f.name)
               CONTAINS toLower($keyword)

        RETURN
            f.food_id AS food_id,
            f.name AS name,
            f.image AS image

        ORDER BY f.name
        """,
        {
            "keyword": keyword.strip()
        },
    )


# =========================
# GRAPH EXPLORER
# =========================

def get_graph(
    user_id: str
) -> list[dict[str, Any]]:

    return query(
        """
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
            "Food" AS target_label,

            type(r) AS relationship
        """,
        {
            "user_id": user_id
        },
    )