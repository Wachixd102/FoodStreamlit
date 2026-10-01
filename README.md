# GraphBook Recommendation System

โปรเจ็คตัวอย่างระดับปริญญาตรีสำหรับรายวิชา Graph Database / Advanced Database
พัฒนาด้วย **Streamlit + Neo4j Aura + Cypher** และออกแบบให้ deploy ผ่าน **GitHub → Streamlit Community Cloud** ได้โดยตรง

## 1. แนวคิดของระบบ

ระบบใช้ Property Graph ดังนี้

```text
(Student)-[:FRIEND_OF]-(Student)
(Student)-[:BORROWED {borrow_date, rating}]->(Book)
(Student)-[:INTERESTED_IN]->(Category)
(Book)-[:IN_CATEGORY]->(Category)
(Author)-[:WROTE]->(Book)
```

จุดเด่นคือคำแนะนำอธิบายได้ (Explainable Recommendation) ว่าหนังสือถูกแนะนำเพราะ
1. เพื่อนของผู้ใช้เคยยืม
2. หมวดหนังสือตรงกับความสนใจ
3. หนังสือได้รับความนิยม
4. หนังสือมีคะแนนเฉลี่ยดี

ตัวอย่างคะแนน Hybrid:

```text
score = friend_count*3
      + interest_matches*2
      + popularity*0.20
      + average_rating*0.50
```

สูตรนี้เป็น heuristic เพื่อการเรียนการสอน ไม่ใช่โมเดล ML ที่ผ่านการ optimize

## 2. โครงสร้างไฟล์

```text
book_graph_recommender/
├── app.py
├── neo4j_service.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
└── cypher/
    └── schema.cypher
```

## 3. สร้าง Neo4j Aura

1. สร้าง AuraDB instance
2. เก็บค่า Connection URI, username และ password
3. URI ของ Aura โดยทั่วไปอยู่ในรูป `neo4j+s://...databases.neo4j.io`
4. อย่านำ password ไปใส่ในไฟล์ที่ commit ขึ้น GitHub

## 4. รันในเครื่อง

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

คัดลอกไฟล์ตัวอย่าง secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

จากนั้นใส่ credential จริง แล้วรัน

```bash
streamlit run app.py
```

## 5. ครั้งแรกที่เปิดระบบ

1. เข้าเมนู **Admin / Setup**
2. กด **สร้าง Constraint + Demo Data**
3. ระบบใช้ `MERGE` จึงกดซ้ำได้โดยไม่สร้าง node ซ้ำจาก key เดิม
4. จากนั้นทดลอง Dashboard, Recommendations, Search, Borrow/Rate และ Graph Explorer

## 6. Deploy GitHub → Streamlit Community Cloud

1. สร้าง GitHub repository ใหม่
2. push ไฟล์ทั้งหมดขึ้น GitHub **ยกเว้น `.streamlit/secrets.toml`**
3. เข้า Streamlit Community Cloud แล้วเลือก Create app
4. เลือก repository, branch และ entrypoint = `app.py`
5. ใน Advanced settings → Secrets ใส่

```toml
[neo4j]
uri = "neo4j+s://YOUR_INSTANCE.databases.neo4j.io"
username = "neo4j"
password = "YOUR_PASSWORD"
database = "neo4j"
```

6. Deploy

## 7. ประเด็น Graph Database ที่นักศึกษาจะได้ฝึก

- Node, Label, Property
- Relationship และ Direction
- Constraint และ Unique Key
- `MATCH`, `MERGE`, `OPTIONAL MATCH`, `WITH`, `UNWIND`
- Graph traversal ผ่านเพื่อน → หนังสือ
- Aggregation เช่น `count`, `avg`, `collect`
- Recommendation จาก topology ของกราฟ
- Parameterized Cypher
- Python Driver และ connection pooling
- Streamlit UI
- Secrets และ cloud deployment

## 8. สิ่งที่ปรับปรุงจาก notebook ต้นแบบ

- ใช้ label `Student` ให้สอดคล้องทั้งระบบ แทนการปะปน `Student2`/`Student`
- ใช้ `MERGE` ใน seed data เพื่อรองรับการรันซ้ำ
- เพิ่ม Unique Constraints
- ใช้ parameterized Cypher แทนการต่อ string จาก input
- มอง `FRIEND_OF` เป็นความสัมพันธ์เชิงสมมาตรตอน query ด้วย `-[:FRIEND_OF]-`
- เพิ่ม Author, Category และ Interest เพื่อให้ recommendation มีมิติด้าน content
- เพิ่ม rating และ popularity เพื่อสร้าง Hybrid Score
- แยก database layer (`neo4j_service.py`) ออกจาก UI (`app.py`)
- ใช้ Streamlit Secrets แทนการ hardcode Aura credential

## 9. แนวทางต่อยอดเป็นโครงงานนักศึกษา

สามารถเพิ่ม Login, Favorite/Wishlist, การคืนหนังสือ, due date, collaborative filtering, Graph Data Science similarity, PageRank, community detection, evaluation metrics เช่น Precision@K/Recall@K และระบบผู้ดูแลได้
