CREATE CONSTRAINT student_id_unique IF NOT EXISTS
FOR (s:Student) REQUIRE s.student_id IS UNIQUE;

CREATE CONSTRAINT book_id_unique IF NOT EXISTS
FOR (b:Book) REQUIRE b.book_id IS UNIQUE;

CREATE CONSTRAINT author_id_unique IF NOT EXISTS
FOR (a:Author) REQUIRE a.author_id IS UNIQUE;

CREATE CONSTRAINT category_name_unique IF NOT EXISTS
FOR (c:Category) REQUIRE c.name IS UNIQUE;
