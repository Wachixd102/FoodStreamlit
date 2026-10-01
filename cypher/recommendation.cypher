// Explainable Hybrid Book Recommendation
// Parameters: $student_id, $limit
MATCH (u:Student {student_id:$student_id})
MATCH (b:Book)
WHERE NOT (u)-[:BORROWED]->(b)

// 1) Social signal: books borrowed by friends
OPTIONAL MATCH (u)-[:FRIEND_OF]-(f:Student)-[:BORROWED]->(b)
WITH u, b,
     count(DISTINCT f) AS friend_count,
     [x IN collect(DISTINCT f.name) WHERE x IS NOT NULL][0..3] AS friend_names

// 2) Content signal: categories matching the user's interests
OPTIONAL MATCH (u)-[:INTERESTED_IN]->(c:Category)<-[:IN_CATEGORY]-(b)
WITH b, friend_count, friend_names,
     count(DISTINCT c) AS interest_matches,
     [x IN collect(DISTINCT c.name) WHERE x IS NOT NULL] AS matched_categories

// 3) Popularity and rating signal
OPTIONAL MATCH (:Student)-[br:BORROWED]->(b)
WITH b, friend_count, friend_names, interest_matches, matched_categories,
     count(br) AS popularity,
     coalesce(avg(br.rating), 0.0) AS avg_rating

// 4) Teaching-friendly heuristic score
WITH b, friend_count, friend_names, interest_matches, matched_categories,
     popularity, avg_rating,
     (friend_count * 3.0) +
     (interest_matches * 2.0) +
     (popularity * 0.20) +
     (avg_rating * 0.50) AS score
WHERE friend_count > 0 OR interest_matches > 0 OR popularity > 0

OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
OPTIONAL MATCH (b)-[:IN_CATEGORY]->(allc:Category)
RETURN b.book_id AS book_id,
       b.title AS title,
       collect(DISTINCT a.name) AS authors,
       collect(DISTINCT allc.name) AS categories,
       friend_count,
       friend_names,
       interest_matches,
       matched_categories,
       popularity,
       round(avg_rating * 100) / 100.0 AS avg_rating,
       round(score * 100) / 100.0 AS score
ORDER BY score DESC, b.title
LIMIT $limit;
