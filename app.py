from __future__ import annotations

import os
from pathlib import Path
import mimetypes

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
    run_query,
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

def add_friend_relation(user_id_1, user_id_2):
    return run_query("""
        MATCH (u1:User {user_id: $user_id_1}),
              (u2:User {user_id: $user_id_2})
        WHERE u1 <> u2
        MERGE (u1)-[:FRIENDS]-(u2)
        RETURN u1.name AS user1, u2.name AS user2
    """, {
        "user_id_1": user_id_1,
        "user_id_2": user_id_2
    })


def delete_friend_relation(user_id_1, user_id_2):
    return run_query("""
        MATCH (u1:User {user_id: $user_id_1})-[r:FRIENDS]-(u2:User {user_id: $user_id_2})
        DELETE r
        RETURN "deleted" AS status
    """, {
        "user_id_1": user_id_1,
        "user_id_2": user_id_2
    })


def render_network_graph(graph_rows, selected_user_id, height=650):
    'Render a Neo4j-style interactive network graph in an HTML/SVG canvas.'
    import json
    import math

    users = {}
    foods = {}
    edges = []

    for row in graph_rows:
        uid = str(row.get("source_id", ""))
        uname = str(row.get("source_name", uid))
        tid = str(row.get("target_id", ""))
        tname = str(row.get("target_name", tid))
        target_type = str(row.get("target_type", "Food"))

        users[uid] = uname
        if target_type == "User":
            users[tid] = tname
        else:
            foods[tid] = {
                "name": tname,
                "image": row.get("image", "")
            }

        edges.append({
            "source": uid,
            "target": tid,
            "label": str(row.get("relationship", "LIKES"))
        })

    # Include all users and foods so the graph shows the complete network.
    for row in run_query('''
        MATCH (u:User)
        RETURN u.user_id AS user_id, u.name AS name
        ORDER BY u.user_id
    '''):
        users[str(row["user_id"])] = str(row["name"])

    for row in run_query('''
        MATCH (f:Food)
        RETURN f.food_id AS food_id, f.name AS name, f.image AS image
        ORDER BY f.food_id
    '''):
        foods[str(row["food_id"])] = {
            "name": str(row["name"]),
            "image": row.get("image", "")
        }

    width = 1180
    center_x = 500
    center_y = 325
    nodes = []
    user_ids = list(users.keys())
    food_ids = list(foods.keys())
    selected = str(selected_user_id)

    nodes.append({
        "id": selected,
        "label": users.get(selected, selected),
        "type": "user",
        "selected": True,
        "x": center_x,
        "y": center_y,
    })

    other_users = [uid for uid in user_ids if uid != selected]
    for i, uid in enumerate(other_users):
        angle = math.radians(-150 + (300 / max(1, len(other_users) - 1)) * i) if len(other_users) > 1 else math.radians(180)
        nodes.append({
            "id": uid,
            "label": users[uid],
            "type": "user",
            "selected": False,
            "x": center_x + math.cos(angle) * 350,
            "y": center_y + math.sin(angle) * 245,
        })

    for i, fid in enumerate(food_ids):
        angle = math.radians(-82 + (164 / max(1, len(food_ids) - 1)) * i) if len(food_ids) > 1 else math.radians(0)
        nodes.append({
            "id": fid,
            "label": foods[fid]["name"],
            "type": "food",
            "selected": False,
            "x": center_x + math.cos(angle) * 445,
            "y": center_y + math.sin(angle) * 275,
        })

    seen = set()
    clean_edges = []
    for edge in edges:
        key = (edge["source"], edge["target"])
        if key not in seen:
            seen.add(key)
            clean_edges.append(edge)

    payload = {
        "nodes": nodes,
        "edges": clean_edges,
        "selected": selected,
    }

    safe_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    graph_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#090908;font-family:Inter,Arial,sans-serif}}
#wrap{{position:relative;width:100%;height:100%;background:radial-gradient(circle at 50% 45%,rgba(214,179,106,.055),transparent 38%),linear-gradient(135deg,#0b0b09,#11100c 55%,#080807);border:1px solid rgba(214,179,106,.20);overflow:hidden}}
svg{{width:100%;height:100%;display:block;cursor:grab;user-select:none}}
svg.dragging{{cursor:grabbing}}
.edge{{stroke:#8c8a82;stroke-width:1.25;fill:none;opacity:.72}}
.edge.selected{{stroke:#d6b36a;stroke-width:1.7;opacity:.96}}
.edge-label{{font-size:9px;fill:#77736b;letter-spacing:.5px;pointer-events:none}}
.edge-label.selected{{fill:#e8cc8e}}
.edge.friend{{stroke:#8f7bd9;stroke-width:2;opacity:.9}}
.edge-label.friend{{fill:#b7a8f0}}
.user-node{{fill:#989ca5;stroke:#d7d9dc;stroke-width:1.2;filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))}}
.user-node.selected{{fill:#0b0b0a;stroke:#e1c27b;stroke-width:2.3;filter:drop-shadow(0 0 12px rgba(214,179,106,.28))}}
.food-node{{fill:#12120f;stroke:#d5d0c3;stroke-width:1.5;filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))}}
.food-node.liked{{stroke:#d6b36a;stroke-width:2.1;fill:#17140e}}
.node-label{{font-size:12px;fill:#ddd8cc;pointer-events:none;text-anchor:middle}}
.food-label{{font-size:11px;fill:#eee9dd;pointer-events:none;text-anchor:middle}}
.toolbar{{position:absolute;top:14px;right:14px;display:flex;gap:7px;z-index:5}}
.tool{{height:34px;min-width:34px;padding:0 11px;border:1px solid rgba(214,179,106,.28);border-radius:2px;background:rgba(16,16,14,.92);color:#e9dfca;font-weight:600;cursor:pointer;backdrop-filter:blur(8px);transition:.2s}}
.tool:hover{{border-color:#d6b36a;color:#f1d99b;transform:translateY(-1px)}}
.hint{{position:absolute;left:14px;top:14px;padding:8px 12px;border:1px solid rgba(214,179,106,.18);background:rgba(13,13,11,.78);color:#8f8a80;font-size:11px;letter-spacing:.3px;border-radius:2px;z-index:5}}
.legend{{position:absolute;left:14px;bottom:14px;display:flex;gap:15px;align-items:center;padding:9px 13px;border:1px solid rgba(214,179,106,.18);background:rgba(13,13,11,.84);color:#aaa397;font-size:10px;letter-spacing:.5px;z-index:5}}
.legend span{{display:flex;align-items:center;gap:6px}}
.dot{{width:11px;height:11px;border-radius:50%;background:#989ca5;border:1px solid #d7d9dc}}
.dot.sel{{background:#0b0b0a;border:1px solid #e1c27b}}
.box{{width:15px;height:11px;border-radius:1px;background:#12120f;border:1px solid #d5d0c3}}
.line{{width:24px;height:0;border-top:1px solid #8c8a82}}
</style>
</head>
<body>
<div id="wrap">
  <div class="hint">ลากเพื่อเลื่อน · ลากโหนดเพื่อจัดตำแหน่ง · scroll เพื่อซูม</div>
  <div class="toolbar">
    <button class="tool" id="plus">＋</button>
    <button class="tool" id="minus">－</button>
    <button class="tool" id="fit">พอดีกรอบ</button>
    <button class="tool" id="reset">จัดวางใหม่</button>
  </div>
  <div class="legend">
    <span><i class="dot"></i>User</span>
    <span><i class="dot sel"></i>User ที่เลือก</span>
    <span><i class="box"></i>Food</span>
    <span><i class="line"></i>LIKES</span>
    <span><i class="line" style="border-top-color:#8f7bd9"></i>FRIENDS</span>
  </div>
  <svg id="graph" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#8c8a82"></path>
      </marker>
      <marker id="arrowGold" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#d6b36a"></path>
      </marker>
    </defs>
    <g id="viewport">
      <g id="edges"></g>
      <g id="nodes"></g>
    </g>
  </svg>
</div>
<script>
const DATA = {safe_json};
const svg = document.getElementById('graph');
const viewport = document.getElementById('viewport');
const edgeLayer = document.getElementById('edges');
const nodeLayer = document.getElementById('nodes');
const ns = 'http://www.w3.org/2000/svg';
let scale = 1, tx = 0, ty = 0;
let dragPan = null, dragNode = null;
const nodeMap = new Map(DATA.nodes.map(n => [n.id, n]));

function el(name, attrs={{}}){{const e=document.createElementNS(ns,name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e}}
function isLikedEdge(e){{return e.label==='LIKES' && e.source===DATA.selected}}
function isFriendEdge(e){{return e.label==='FRIENDS'}}
function render(){{
  edgeLayer.innerHTML=''; nodeLayer.innerHTML='';
  for(const e of DATA.edges){{
    const a=nodeMap.get(e.source), b=nodeMap.get(e.target); if(!a||!b) continue;
    const friend=isFriendEdge(e);
    const selectedEdge=isLikedEdge(e);
    const line=el('line',{{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:'edge'+(selectedEdge?' selected':'')+(friend?' friend':'')}});
    line.setAttribute('marker-end',friend?'url(#arrow)':(selectedEdge?'url(#arrowGold)':'url(#arrow)'));
    edgeLayer.appendChild(line);
    const t=el('text',{{x:(a.x+b.x)/2,y:(a.y+b.y)/2-6,class:'edge-label'+(selectedEdge?' selected':'')+(friend?' friend':'')}});
    t.textContent=e.label||'LIKES'; edgeLayer.appendChild(t);
  }}
  for(const n of DATA.nodes){{
    const g=el('g',{{class:'node',transform:`translate(${{n.x}},${{n.y}})`,cursor:'pointer'}});
    if(n.type==='user'){{
      const c=el('circle',{{r:n.selected?18:11,class:'user-node'+(n.selected?' selected':'')}}); g.appendChild(c);
      const t=el('text',{{y:n.selected?34:26,class:'node-label'}});t.textContent=n.label;g.appendChild(t);
    }} else {{
      const w=Math.max(92,Math.min(150,n.label.length*8+26));
      const liked=DATA.edges.some(e=>e.source===DATA.selected&&e.target===n.id);
      const r=el('rect',{{x:-w/2,y:-17,width:w,height:34,rx:2,class:'food-node'+(liked?' liked':'')}});g.appendChild(r);
      const t=el('text',{{y:4,class:'food-label'}});t.textContent=n.label;g.appendChild(t);
    }}
    g.addEventListener('mousedown',ev=>{{ev.stopPropagation();dragNode={{node:n,startX:ev.clientX,startY:ev.clientY,ox:n.x,oy:n.y}};}});
    nodeLayer.appendChild(g);
  }}
}}
function setTransform(){{viewport.setAttribute('transform',`translate(${{tx}},${{ty}}) scale(${{scale}})`);}}
function zoomAt(factor){{scale=Math.max(.45,Math.min(2.6,scale*factor));setTransform();}}
function fit(){{scale=1;tx=0;ty=0;setTransform();}}
function resetLayout(){{
  const center={{x:500,y:325}};
  const selected=DATA.selected;
  const users=DATA.nodes.filter(n=>n.type==='user'&&n.id!==selected);
  const foods=DATA.nodes.filter(n=>n.type==='food');
  const sel=nodeMap.get(selected); if(sel){{sel.x=center.x;sel.y=center.y;}}
  users.forEach((n,i)=>{{const a=(-150+(300/Math.max(1,users.length-1))*i)*Math.PI/180;n.x=center.x+Math.cos(a)*350;n.y=center.y+Math.sin(a)*245;}});
  foods.forEach((n,i)=>{{const a=(-82+(164/Math.max(1,foods.length-1))*i)*Math.PI/180;n.x=center.x+Math.cos(a)*445;n.y=center.y+Math.sin(a)*275;}});
  fit();render();
}}
svg.addEventListener('mousedown',ev=>{{dragPan={{x:ev.clientX,y:ev.clientY,tx,ty}};svg.classList.add('dragging')}});
window.addEventListener('mousemove',ev=>{{
  if(dragNode){{const dx=(ev.clientX-dragNode.startX)/scale;const dy=(ev.clientY-dragNode.startY)/scale;dragNode.node.x=dragNode.ox+dx;dragNode.node.y=dragNode.oy+dy;render();return;}}
  if(dragPan){{tx=dragPan.tx+(ev.clientX-dragPan.x);ty=dragPan.ty+(ev.clientY-dragPan.y);setTransform();}}
}});
window.addEventListener('mouseup',()=>{{dragNode=null;dragPan=null;svg.classList.remove('dragging')}});
svg.addEventListener('wheel',ev=>{{ev.preventDefault();zoomAt(ev.deltaY<0?1.10:.91)}},{{passive:false}});
document.getElementById('plus').onclick=()=>zoomAt(1.18);
document.getElementById('minus').onclick=()=>zoomAt(.85);
document.getElementById('fit').onclick=fit;
document.getElementById('reset').onclick=resetLayout;
render();setTransform();
</script>
</body>
</html>'''

    components.html(graph_html, height=height, scrolling=False)




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
    st.caption("สำรวจเครือข่าย User และ Food แบบ Interactive Graph")

    user_options = get_user_options()

    if not user_options:
        st.warning("ยังไม่มี User")
        st.stop()

    selected_user = st.selectbox(
        "เลือกผู้ใช้",
        list(user_options.keys())
    )

    user_id = user_options[selected_user]

    graph_data = run_query('''
        MATCH (u:User)-[r]->(target)
        WHERE type(r) IN ['LIKES', 'FRIENDS']
        RETURN
            u.user_id AS source_id,
            u.name AS source_name,
            CASE WHEN target:User THEN target.user_id ELSE target.food_id END AS target_id,
            target.name AS target_name,
            CASE WHEN target:User THEN 'User' ELSE 'Food' END AS target_type,
            target.image AS image,
            type(r) AS relationship
        ORDER BY u.user_id, target_id
    ''')

    if not graph_data:
        st.info("ยังไม่มีความสัมพันธ์ LIKES หรือ FRIENDS ในระบบ")
    else:
        st.markdown(
            f'<span class="premium-label">SELECTED GUEST · {selected_user}</span>',
            unsafe_allow_html=True
        )
        st.write("")

        render_network_graph(
            graph_data,
            user_id,
            height=680
        )

        st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
        st.caption("เส้นทอง = LIKES ของ User ที่เลือก · เส้นม่วง = FRIENDS · ลากโหนดเพื่อจัดตำแหน่ง")

        with st.expander("ดู Connection Ledger"):
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
            "❤️ จัดการความสัมพันธ์"
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

        st.divider()

        st.subheader("🤝 เพิ่มความสัมพันธ์ FRIENDS")
        user_options = get_user_options()

        if len(user_options) >= 2:
            with st.form("add_friend_form"):
                friend_a = st.selectbox("User คนที่ 1", list(user_options.keys()), key="friend_a")
                friend_b = st.selectbox("User คนที่ 2", list(user_options.keys()), key="friend_b")
                submit_friend = st.form_submit_button("🤝 เพิ่มเพื่อน")

                if submit_friend:
                    if user_options[friend_a] == user_options[friend_b]:
                        st.error("ไม่สามารถเพิ่มเพื่อนกับตัวเองได้")
                    else:
                        try:
                            result = add_friend_relation(user_options[friend_a], user_options[friend_b])
                            if result:
                                st.success(f"เพิ่มเพื่อน {friend_a} ↔ {friend_b} สำเร็จ")
                                st.rerun()
                            else:
                                st.error("ไม่สามารถเพิ่ม FRIENDS ได้")
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาด: {e}")
        else:
            st.info("ต้องมี User อย่างน้อย 2 คนก่อน")


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

        st.divider()
        st.subheader("🤝 ลบความสัมพันธ์ FRIENDS")

        friend_rows = run_query("""
            MATCH (u:User)-[:FRIENDS]-(f:User)
            RETURN DISTINCT
                u.user_id AS user1_id,
                u.name AS user1_name,
                f.user_id AS user2_id,
                f.name AS user2_name
            ORDER BY user1_id, user2_id
        """)

        if friend_rows:
            friend_options = {}
            for row in friend_rows:
                a = row["user1_id"]
                b = row["user2_id"]
                if a == b:
                    continue
                key = tuple(sorted([a, b]))
                friend_options[key] = f'{a} - {row["user1_name"]} ↔ {b} - {row["user2_name"]}'

            if friend_options:
                selected_friend = st.selectbox(
                    "เลือกคู่เพื่อนที่ต้องการลบ",
                    list(friend_options.keys()),
                    format_func=lambda x: friend_options[x],
                    key="delete_friend_pair"
                )

                if st.button("💔 ลบเพื่อน", key="delete_friend_btn"):
                    try:
                        a, b = selected_friend
                        delete_friend_relation(a, b)
                        st.success("ลบความสัมพันธ์ FRIENDS สำเร็จ")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
            else:
                st.info("ยังไม่มีความสัมพันธ์ FRIENDS")
        else:
            st.info("ยังไม่มีความสัมพันธ์ FRIENDS")

