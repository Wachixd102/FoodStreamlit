from __future__ import annotations

from typing import Any

import streamlit as st
from neo4j import GraphDatabase, RoutingControl


def _config() -> tuple[str, str, str, str]:
    cfg = st.secrets["neo4j"]
    return (
        cfg["uri"],
        cfg["username"],
        cfg["password"],
        cfg.get("database", "neo4j"),
    )


@st.cache_resource(show_spinner=False)
def get_driver():
    """Create one thread-safe Neo4j Driver for the Streamlit process."""
    uri, username, password, _ = _config()
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    return driver


def query(cypher: str, parameters: dict[str, Any] | None = None, *, write: bool = False) -> list[dict[str, Any]]:
    """Execute parameterized Cypher and return rows as dictionaries."""
    _, _, _, database = _config()
    records, _, _ = get_driver().execute_query(
        cypher,
        parameters_=parameters or {},
        database_=database,
        routing_=RoutingControl.WRITE if write else RoutingControl.READ,
    )
    return [record.data() for record in records]


def ping() -> bool:
    rows = query("RETURN 1 AS ok")
    return bool(rows and rows[0]["ok"] == 1)


def create_schema() -> None:
    statements = [
        "CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE",
        "CREATE CONSTRAINT book_id_unique IF NOT EXISTS FOR (b:Book) REQUIRE b.book_id IS UNIQUE",
        "CREATE CONSTRAINT author_id_unique IF NOT EXISTS FOR (a:Author) REQUIRE a.author_id IS UNIQUE",
        "CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
    ]
    for stmt in statements:
        query(stmt, write=True)


def seed_demo_data() -> None:
    """Idempotent sample dataset: safe to run more than once."""
    create_schema()

    students = [
        {"student_id": "S001", "name": "Anan", "major": "Computer Science", "year": 2},
        {"student_id": "S002", "name": "Mali", "major": "Computer Science", "year": 2},
        {"student_id": "S003", "name": "Krit", "major": "Information Technology", "year": 3},
        {"student_id": "S004", "name": "Nida", "major": "Data Science", "year": 2},
        {"student_id": "S005", "name": "Ploy", "major": "Business Computer", "year": 3},
        {"student_id": "S006", "name": "Ton", "major": "Computer Science", "year": 1},
    ]
    books = [
        {"book_id": "B101", "title": "Python Programming", "year": 2025},
        {"book_id": "B102", "title": "Artificial Intelligence Basics", "year": 2026},
        {"book_id": "B103", "title": "Data Science for Students", "year": 2025},
        {"book_id": "B104", "title": "Introduction to Database", "year": 2024},
        {"book_id": "B105", "title": "Graph Databases with Neo4j", "year": 2026},
        {"book_id": "B106", "title": "Machine Learning Foundations", "year": 2025},
        {"book_id": "B107", "title": "Web Application Development", "year": 2024},
        {"book_id": "B108", "title": "Algorithms and Problem Solving", "year": 2023},
    ]
    authors = [
        {"author_id": "A01", "name": "Somchai Tech"},
        {"author_id": "A02", "name": "Narin Data"},
        {"author_id": "A03", "name": "Kanya AI"},
        {"author_id": "A04", "name": "Preecha DB"},
    ]
    categories = ["Programming", "AI", "Data Science", "Database", "Web Development", "Algorithms"]

    query(
        """
        UNWIND $rows AS row
        MERGE (s:Student {student_id: row.student_id})
        SET s.name = row.name, s.major = row.major, s.year = row.year
        """,
        {"rows": students},
        write=True,
    )
    query(
        """
        UNWIND $rows AS row
        MERGE (b:Book {book_id: row.book_id})
        SET b.title = row.title, b.year = row.year
        """,
        {"rows": books},
        write=True,
    )
    query(
        """
        UNWIND $rows AS row
        MERGE (a:Author {author_id: row.author_id})
        SET a.name = row.name
        """,
        {"rows": authors},
        write=True,
    )
    query(
        "UNWIND $rows AS name MERGE (:Category {name:name})",
        {"rows": categories},
        write=True,
    )

    friendships = [
        ["S001", "S002"], ["S001", "S003"], ["S001", "S004"],
        ["S002", "S005"], ["S003", "S004"], ["S004", "S006"],
    ]
    query(
        """
        UNWIND $rows AS row
        MATCH (a:Student {student_id: row[0]}), (b:Student {student_id: row[1]})
        MERGE (a)-[:FRIEND_OF]->(b)
        """,
        {"rows": friendships},
        write=True,
    )

    borrows = [
        {"s": "S001", "b": "B101", "date": "2026-08-01", "rating": 4.0},
        {"s": "S001", "b": "B108", "date": "2026-08-14", "rating": 4.0},
        {"s": "S002", "b": "B103", "date": "2026-08-05", "rating": 5.0},
        {"s": "S002", "b": "B102", "date": "2026-08-18", "rating": 4.0},
        {"s": "S003", "b": "B103", "date": "2026-08-07", "rating": 4.0},
        {"s": "S003", "b": "B104", "date": "2026-08-20", "rating": 5.0},
        {"s": "S004", "b": "B105", "date": "2026-08-09", "rating": 5.0},
        {"s": "S004", "b": "B103", "date": "2026-08-24", "rating": 5.0},
        {"s": "S005", "b": "B107", "date": "2026-08-11", "rating": 4.0},
        {"s": "S006", "b": "B106", "date": "2026-08-12", "rating": 4.0},
    ]
    query(
        """
        UNWIND $rows AS row
        MATCH (s:Student {student_id: row.s}), (b:Book {book_id: row.b})
        MERGE (s)-[r:BORROWED]->(b)
        SET r.borrow_date = date(row.date), r.rating = row.rating
        """,
        {"rows": borrows},
        write=True,
    )

    interests = [
        ["S001", "Programming"], ["S001", "Database"],
        ["S002", "AI"], ["S002", "Data Science"],
        ["S003", "Database"], ["S003", "Data Science"],
        ["S004", "AI"], ["S004", "Data Science"],
        ["S005", "Web Development"], ["S006", "Programming"],
    ]
    query(
        """
        UNWIND $rows AS row
        MATCH (s:Student {student_id: row[0]}), (c:Category {name: row[1]})
        MERGE (s)-[:INTERESTED_IN]->(c)
        """,
        {"rows": interests},
        write=True,
    )

    book_categories = [
        ["B101", "Programming"], ["B102", "AI"], ["B103", "Data Science"],
        ["B104", "Database"], ["B105", "Database"], ["B106", "AI"],
        ["B106", "Data Science"], ["B107", "Web Development"],
        ["B108", "Algorithms"], ["B108", "Programming"],
    ]
    query(
        """
        UNWIND $rows AS row
        MATCH (b:Book {book_id: row[0]}), (c:Category {name: row[1]})
        MERGE (b)-[:IN_CATEGORY]->(c)
        """,
        {"rows": book_categories},
        write=True,
    )

    wrote = [
        ["A01", "B101"], ["A03", "B102"], ["A02", "B103"], ["A04", "B104"],
        ["A04", "B105"], ["A03", "B106"], ["A01", "B107"], ["A01", "B108"],
    ]
    query(
        """
        UNWIND $rows AS row
        MATCH (a:Author {author_id: row[0]}), (b:Book {book_id: row[1]})
        MERGE (a)-[:WROTE]->(b)
        """,
        {"rows": wrote},
        write=True,
    )


def get_students() -> list[dict[str, Any]]:
    return query("MATCH (s:Student) RETURN s.student_id AS student_id, s.name AS name, s.major AS major, s.year AS year ORDER BY s.student_id")


def get_dashboard_metrics() -> dict[str, int]:
    rows = query(
        """
        MATCH (s:Student) WITH count(s) AS students
        MATCH (b:Book) WITH students, count(b) AS books
        MATCH ()-[r:BORROWED]->() WITH students, books, count(r) AS borrows
        MATCH ()-[f:FRIEND_OF]->()
        RETURN students, books, borrows, count(f) AS friendships
        """
    )
    return rows[0] if rows else {"students": 0, "books": 0, "borrows": 0, "friendships": 0}


def get_profile(student_id: str) -> dict[str, Any] | None:
    rows = query(
        """
        MATCH (s:Student {student_id:$student_id})
        OPTIONAL MATCH (s)-[:INTERESTED_IN]->(c:Category)
        OPTIONAL MATCH (s)-[:BORROWED]->(b:Book)
        RETURN s.student_id AS student_id, s.name AS name, s.major AS major, s.year AS year,
               collect(DISTINCT c.name) AS interests,
               collect(DISTINCT {book_id:b.book_id, title:b.title}) AS borrowed
        """,
        {"student_id": student_id},
    )
    if not rows:
        return None
    row = rows[0]
    row["borrowed"] = [x for x in row["borrowed"] if x.get("book_id")]
    return row


def recommend_books(student_id: str, limit: int = 8) -> list[dict[str, Any]]:
    """Explainable hybrid score: social + interests + popularity + ratings."""
    return query(
        """
        MATCH (u:Student {student_id:$student_id})
        MATCH (b:Book)
        WHERE NOT (u)-[:BORROWED]->(b)

        OPTIONAL MATCH (u)-[:FRIEND_OF]-(f:Student)-[:BORROWED]->(b)
        WITH u, b, count(DISTINCT f) AS friend_count,
             [x IN collect(DISTINCT f.name) WHERE x IS NOT NULL][0..3] AS friend_names

        OPTIONAL MATCH (u)-[:INTERESTED_IN]->(c:Category)<-[:IN_CATEGORY]-(b)
        WITH b, friend_count, friend_names,
             count(DISTINCT c) AS interest_matches,
             [x IN collect(DISTINCT c.name) WHERE x IS NOT NULL] AS matched_categories

        OPTIONAL MATCH (:Student)-[br:BORROWED]->(b)
        WITH b, friend_count, friend_names, interest_matches, matched_categories,
             count(br) AS popularity,
             avg(br.rating) AS avg_rating

        WITH b, friend_count, friend_names, interest_matches, matched_categories,
             popularity, coalesce(avg_rating, 0.0) AS avg_rating,
             (friend_count * 3.0) + (interest_matches * 2.0) +
             (popularity * 0.20) + (coalesce(avg_rating, 0.0) * 0.50) AS score
        WHERE friend_count > 0 OR interest_matches > 0 OR popularity > 0

        OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
        OPTIONAL MATCH (b)-[:IN_CATEGORY]->(allc:Category)
        RETURN b.book_id AS book_id, b.title AS title, b.year AS year,
               collect(DISTINCT a.name) AS authors,
               collect(DISTINCT allc.name) AS categories,
               friend_count, friend_names, interest_matches, matched_categories,
               popularity, round(avg_rating * 100) / 100.0 AS avg_rating,
               round(score * 100) / 100.0 AS score
        ORDER BY score DESC, b.title
        LIMIT $limit
        """,
        {"student_id": student_id, "limit": int(limit)},
    )


def search_books(keyword: str = "", category: str | None = None) -> list[dict[str, Any]]:
    return query(
        """
        MATCH (b:Book)
        OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
        OPTIONAL MATCH (b)-[:IN_CATEGORY]->(c:Category)
        WITH b, collect(DISTINCT a.name) AS authors, collect(DISTINCT c.name) AS categories
        WHERE ($keyword = '' OR toLower(b.title) CONTAINS toLower($keyword)
               OR any(x IN authors WHERE toLower(x) CONTAINS toLower($keyword)))
          AND ($category = '' OR $category IN categories)
        RETURN b.book_id AS book_id, b.title AS title, b.year AS year,
               authors, categories
        ORDER BY b.title
        """,
        {"keyword": keyword.strip(), "category": category or ""},
    )


def list_categories() -> list[str]:
    return [row["name"] for row in query("MATCH (c:Category) RETURN c.name AS name ORDER BY c.name")]


def record_borrow(student_id: str, book_id: str, borrow_date: str, rating: float | None = None) -> None:
    query(
        """
        MATCH (s:Student {student_id:$student_id}), (b:Book {book_id:$book_id})
        MERGE (s)-[r:BORROWED]->(b)
        SET r.borrow_date = date($borrow_date)
        FOREACH (_ IN CASE WHEN $rating IS NULL THEN [] ELSE [1] END | SET r.rating = $rating)
        """,
        {"student_id": student_id, "book_id": book_id, "borrow_date": borrow_date, "rating": rating},
        write=True,
    )


def graph_neighborhood(student_id: str, limit: int = 40) -> list[dict[str, Any]]:
    return query(
        """
        MATCH (u:Student {student_id:$student_id})
        OPTIONAL MATCH p=(u)-[:FRIEND_OF|BORROWED|INTERESTED_IN*1..2]-(x)
        WITH u, collect(p)[0..$limit] AS paths
        UNWIND paths AS p
        UNWIND relationships(p) AS r
        WITH DISTINCT startNode(r) AS s, r, endNode(r) AS t
        RETURN elementId(s) AS source_id, labels(s)[0] AS source_label,
               coalesce(s.name, s.title, s.student_id, s.book_id) AS source_name,
               type(r) AS relationship,
               elementId(t) AS target_id, labels(t)[0] AS target_label,
               coalesce(t.name, t.title, t.student_id, t.book_id) AS target_name
        LIMIT $limit
        """,
        {"student_id": student_id, "limit": int(limit)},
    )
