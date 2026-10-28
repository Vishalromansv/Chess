import streamlit as st
import sqlite3
import pandas as pd
import time
import base64
from database import init_db, get_connection

# Page Configuration
st.set_page_config(
    page_title="Chess Tournament Manager",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# Background Video with dark overlay
def add_bg_video(video_path):
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        encoded = base64.b64encode(video_bytes).decode()
        html = (
            "<style>"
            ".stApp { background: transparent !important; }"
            "#bg-video-container { position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -999; overflow: hidden; }"
            "#bg-video { position: absolute; top: 50%; left: 50%; min-width: 100%; min-height: 100%; width: auto; height: auto; transform: translateX(-50%) translateY(-50%); object-fit: cover; }"
            "#bg-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 31, 35, 0.76); z-index: -998; }"
            "</style>"
            "<div id='bg-video-container'>"
            "<div id='bg-overlay'></div>"
            f"<video autoplay muted loop playsinline id='bg-video'><source src='data:video/mp4;base64,{encoded}' type='video/mp4'></video>"
            "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

add_bg_video("anime_forest.mp4")

# Custom CSS for Points Table, Tournament Bracket Boxes & Mobile Touch UI
st.markdown("""
<style>
:root {
    --deep-teal: #003135;
    --dark-ocean: #024950;
    --terracotta: #964734;
    --vibrant-cyan: #0FA4AF;
    --ice-blue: #AFDDE5;
}
.stApp { background-color: #003135; color: var(--ice-blue); }
section[data-testid="stSidebar"] { background-color: rgba(0, 24, 27, 0.96) !important; border-right: 1px solid var(--vibrant-cyan); }
section[data-testid="stSidebar"] * { color: var(--ice-blue) !important; }
.metric-card, .glass-panel {
    background-color: rgba(0, 49, 53, 0.88) !important;
    backdrop-filter: blur(10px);
    border: 1px solid var(--vibrant-cyan);
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 16px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.5);
}
h1, h2, h3 { color: #AFDDE5 !important; font-weight: 800 !important; text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95); }
p, label, span, div { color: var(--ice-blue); text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8); }

/* Points Table */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    background-color: rgba(0, 36, 40, 0.94);
    border: 2px solid #0FA4AF;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.5);
}
.custom-table th {
    background-color: #024950;
    color: #AFDDE5;
    font-weight: 800;
    text-align: center;
    padding: 14px 10px;
    border-bottom: 2px solid #0FA4AF;
    font-size: 15px;
    text-transform: uppercase;
}
.custom-table td {
    padding: 12px 10px;
    border-bottom: 1px solid rgba(15, 164, 175, 0.25);
    color: #ffffff;
    text-align: center;
    font-size: 15px;
}
.custom-table td.player-col, .custom-table th.player-col { text-align: left; padding-left: 18px; }
.top-two-row { background-color: rgba(15, 164, 175, 0.25) !important; font-weight: bold; }
.pts-badge {
    background-color: #0FA4AF;
    color: #002225 !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 900;
    font-size: 16px;
    text-shadow: none !important;
    display: inline-block;
}

/* Visual Bracket & Match Boxes */
.bracket-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    justify-content: center;
    background: rgba(0, 31, 35, 0.88);
    border: 2px solid #0FA4AF;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
.bracket-box {
    background: rgba(2, 73, 80, 0.95);
    border: 2px solid #0FA4AF;
    border-radius: 12px;
    padding: 16px 20px;
    min-width: 220px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.bracket-box.final-box { border-color: #964734; background: rgba(45, 25, 22, 0.92); }
.bracket-box.champ-box { border: 3px solid #0FA4AF; background: linear-gradient(135deg, rgba(2,73,80,0.95), rgba(15,164,175,0.35)); }
.bracket-arrow { font-size: 28px; color: #0FA4AF; font-weight: bold; }

/* Round Grid Boxes */
.round-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}
.match-box-card {
    background: rgba(0, 38, 42, 0.92);
    border: 1px solid #0FA4AF;
    border-top: 4px solid #0FA4AF;
    border-radius: 10px;
    padding: 12px 14px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.35);
}
.match-box-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 4px;
    border-bottom: 1px solid rgba(175, 221, 229, 0.15);
    font-size: 15px;
}
.match-box-row:last-child { border-bottom: none; }

.stButton>button {
    background-color: var(--vibrant-cyan);
    color: #002225 !important;
    border-radius: 10px;
    padding: 0.75rem 1.2rem;
    font-weight: 800;
    font-size: 16px;
    border: none;
    width: 100%;
    min-height: 48px;
    text-shadow: none !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.35);
}
.stButton>button:hover { background-color: var(--ice-blue); color: #002225 !important; }
input, select, textarea { background-color: #001f22 !important; color: #AFDDE5 !important; border: 1px solid #0FA4AF !important; font-size: 16px !important; }
div[data-baseweb="select"] > div { background-color: #001f22 !important; color: #AFDDE5 !important; }
</style>
""", unsafe_allow_html=True)

def compute_league_standings(conn, t_id):
    participants = conn.execute("""
        SELECT p.id, p.name, p.rating FROM tournament_participants tp
        JOIN players p ON tp.player_id = p.id
        WHERE tp.tournament_id = ?
    """, (t_id,)).fetchall()
    
    standings = []
    for p in participants:
        pid = p['id']
        pname = p['name']
        
        matches = conn.execute("""
            SELECT * FROM matches 
            WHERE tournament_id = ? AND group_name = 'League Stage' AND status = 'Completed'
            AND (white_player_id = ? OR black_player_id = ?)
        """, (t_id, pid, pid)).fetchall()
        
        played = len(matches)
        wins, draws, losses, points = 0, 0, 0, 0.0
        
        for m in matches:
            is_white = (m['white_player_id'] == pid)
            res = m['result']
            if res == '1-0':
                if is_white: wins += 1; points += 1.0
                else: losses += 1
            elif res == '0-1':
                if not is_white: wins += 1; points += 1.0
                else: losses += 1
            elif res == '½-½':
                draws += 1; points += 0.5
                
        standings.append({
            "id": pid,
            "Player": pname,
            "Played": played,
            "Wins": wins,
            "Draws": draws,
            "Losses": losses,
            "Points": points
        })
        
    standings.sort(key=lambda x: (x["Points"], x["Wins"]), reverse=True)
    return standings

def check_or_create_grand_final(conn, t_id):
    existing_final = conn.execute("SELECT id FROM matches WHERE tournament_id = ? AND group_name = 'Grand Final'", (t_id,)).fetchone()
    if existing_final:
        return existing_final['id']
        
    league_matches = conn.execute("SELECT status FROM matches WHERE tournament_id = ? AND group_name = 'League Stage'", (t_id,)).fetchall()
    if not league_matches:
        return None
        
    if all(m['status'] == 'Completed' for m in league_matches):
        standings = compute_league_standings(conn, t_id)
        if len(standings) >= 2:
            top1_id = standings[0]['id']
            top2_id = standings[1]['id']
            tourn = conn.execute("SELECT time_control_mins FROM tournaments WHERE id = ?", (t_id,)).fetchone()
            tc_secs = (tourn['time_control_mins'] if tourn else 5) * 60
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO matches (tournament_id, round_num, group_name, white_player_id, black_player_id, status, white_time_left, black_time_left)
                VALUES (?, 99, 'Grand Final', ?, ?, 'Upcoming', ?, ?)
            """, (t_id, top1_id, top2_id, tc_secs, tc_secs))
            conn.commit()
            return cursor.lastrowid
    return None

# Sidebar Navigation
st.sidebar.title("♟️ Chess Tournament")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", [
    "🏠 Dashboard",
    "👥 Players",
    "🏆 Create Tournament",
    "📋 Match List",
    "⏱️ Live Chess Clock",
    "📊 Standings & Top 2 Final",
    "⚙️ Settings"
])

if 'active_match_id' not in st.session_state:
    st.session_state.active_match_id = None
if 'current_tournament_id' not in st.session_state:
    conn = get_connection()
    t = conn.execute("SELECT id FROM tournaments ORDER BY id DESC LIMIT 1").fetchone()
    st.session_state.current_tournament_id = t['id'] if t else None
    conn.close()

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if menu == "🏠 Dashboard":
    st.title("♟️ Chess Tournament Dashboard")
    conn = get_connection()
    t_id = st.session_state.current_tournament_id
    
    col1, col2, col3 = st.columns(3)
    player_count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    with col1:
        st.markdown(f"<div class='metric-card'><h3>👥 Registered Players</h3><h1 style='color:#0FA4AF;margin:0;'>{player_count}</h1></div>", unsafe_allow_html=True)
        
    if t_id:
        check_or_create_grand_final(conn, t_id)
        tourn = conn.execute("SELECT * FROM tournaments WHERE id = ?", (t_id,)).fetchone()
        matches = conn.execute("SELECT * FROM matches WHERE tournament_id = ?", (t_id,)).fetchall()
        total_m = len(matches)
        comp_m = len([m for m in matches if m['status'] == 'Completed'])
        prog_m = len([m for m in matches if m['status'] == 'In Progress'])
        
        with col2:
            st.markdown(f"<div class='metric-card'><h3>🏆 Active Tournament</h3><h2 style='color:#AFDDE5;margin:0;'>{tourn['name']}</h2><p style='color:#0FA4AF;margin-top:6px;'>League + Top 2 Final ({tourn['time_control_mins']}m + {tourn['increment_secs']}s)</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><h3>⚔️ Match Progress</h3><h1 style='color:#0FA4AF;margin:0;'>{comp_m} / {total_m}</h1><p style='color:#AFDDE5;margin-top:6px;'>In Progress: {prog_m}</p></div>", unsafe_allow_html=True)
    else:
        with col2:
            st.markdown("<div class='metric-card'><h3>🏆 Active Tournament</h3><p>No active tournament. Go to <b>Create Tournament</b> to start!</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'><h3>⚔️ Match Progress</h3><p>-</p></div>", unsafe_allow_html=True)
    conn.close()

# ----------------------------------------------------
# 2. PLAYERS
# ----------------------------------------------------
elif menu == "👥 Players":
    st.title("👥 Player Management")
    conn = get_connection()
    
    with st.form("add_player_form"):
        st.subheader("Add New Player")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            p_name = st.text_input("Player Name")
        with col2:
            p_rating = st.number_input("Rating (Elo)", min_value=100, max_value=3000, value=1200)
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Player")
            
        if submitted:
            if p_name.strip():
                try:
                    conn.execute("INSERT INTO players (name, rating) VALUES (?, ?)", (p_name.strip(), p_rating))
                    conn.commit()
                    st.success(f"Added player: {p_name}")
                    safe_rerun()
                except sqlite3.IntegrityError:
                    st.error("A player with this name already exists.")
            else:
                st.warning("Please enter a valid player name.")

    st.subheader("Registered Players")
    search_query = st.text_input("🔍 Search Players by Name", "")
    if search_query:
        players = conn.execute("SELECT * FROM players WHERE name LIKE ? ORDER BY name", (f"%{search_query}%",)).fetchall()
    else:
        players = conn.execute("SELECT * FROM players ORDER BY name").fetchall()
        
    if players:
        rows_html = "".join([f"<tr><td>{idx}</td><td class='player-col'><b>{p['name']}</b></td><td>{p['rating']}</td></tr>" for idx, p in enumerate(players, 1)])
        table_html = f"<table class='custom-table'><thead><tr><th>#</th><th class='player-col'>Player Name</th><th>Rating</th></tr></thead><tbody>{rows_html}</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        with st.expander("🗑️ Remove a Player"):
            del_id = st.selectbox("Select Player to Delete", options=[p['id'] for p in players], format_func=lambda x: next(p['name'] for p in players if p['id'] == x))
            if st.button("Delete Selected Player"):
                conn.execute("DELETE FROM players WHERE id = ?", (del_id,))
                conn.commit()
                st.success("Player removed.")
                safe_rerun()
    else:
        st.info("No players registered yet. Add players above!")
    conn.close()

# ----------------------------------------------------
# 3. CREATE TOURNAMENT
# ----------------------------------------------------
elif menu == "🏆 Create Tournament":
    st.title("🏆 Create Tournament")
    st.markdown("<div class='glass-panel'><b>Format: Full Round-Robin League + Top 2 Grand Final</b><br>1. Every player plays against every other player once in the <b>League Stage</b>.<br>2. Rankings & points update live.<br>3. The <b>Top 2 players (#1 vs #2)</b> advance to the <b>Grand Final</b>!</div>", unsafe_allow_html=True)
    
    conn = get_connection()
    players = conn.execute("SELECT * FROM players ORDER BY name").fetchall()
    
    if len(players) < 2:
        st.warning("You need at least 2 registered players to create a tournament.")
    else:
        with st.form("tournament_setup_form"):
            t_name = st.text_input("Tournament Name", value="Local Chess Championship 2026")
            col_tc1, col_tc2 = st.columns(2)
            with col_tc1:
                time_control = st.selectbox("Minutes per Player", [3, 5, 10, 15, 30], index=1)
            with col_tc2:
                increment = st.selectbox("Increment per Move (Seconds)", [0, 2, 3, 5, 10], index=0)
                
            st.markdown("### Select Participating Players (2 to 16)")
            selected_player_ids = []
            cols = st.columns(2)
            for idx, p in enumerate(players):
                with cols[idx % 2]:
                    if st.checkbox(f"{p['name']} ({p['rating']})", value=True, key=f"p_{p['id']}"):
                        selected_player_ids.append(p['id'])
            
            submit_tournament = st.form_submit_button("🚀 Start Tournament & Generate All Matches")
            
            if submit_tournament:
                n_players = len(selected_player_ids)
                if not (2 <= n_players <= 16):
                    st.error("Please select between 2 and 16 players.")
                elif not t_name.strip():
                    st.error("Please provide a valid tournament name.")
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO tournaments (name, format, time_control_mins, increment_secs, status) VALUES (?, ?, ?, ?, ?)",
                        (t_name.strip(), "League + Top 2 Final", time_control, increment, 'Active')
                    )
                    new_t_id = cursor.lastrowid
                    
                    for pid in selected_player_ids:
                        cursor.execute("INSERT INTO tournament_participants (tournament_id, player_id, group_name) VALUES (?, ?, 'League Stage')", (new_t_id, pid))
                        
                    gp_list = list(selected_player_ids)
                    if len(gp_list) % 2 != 0:
                        gp_list.append(None)
                        
                    num_rounds = len(gp_list) - 1
                    for r in range(num_rounds):
                        round_num = r + 1
                        for i in range(len(gp_list) // 2):
                            p1 = gp_list[i]
                            p2 = gp_list[len(gp_list) - 1 - i]
                            if p1 is not None and p2 is not None:
                                white_id, black_id = (p1, p2) if (r + i) % 2 == 0 else (p2, p1)
                                cursor.execute(
                                    "INSERT INTO matches (tournament_id, round_num, group_name, white_player_id, black_player_id, status, white_time_left, black_time_left) VALUES (?, ?, 'League Stage', ?, ?, 'Upcoming', ?, ?)",
                                    (new_t_id, round_num, white_id, black_id, time_control * 60, time_control * 60)
                                )
                        gp_list = [gp_list[0]] + [gp_list[-1]] + gp_list[1:-1]
                        
                    conn.commit()
                    st.session_state.current_tournament_id = new_t_id
                    st.session_state.active_match_id = None
                    st.success("Tournament created!")
                    safe_rerun()
    conn.close()

# ----------------------------------------------------
# 4. MATCH LIST
# ----------------------------------------------------
elif menu == "📋 Match List":
    st.title("📋 Tournament Match List")
    conn = get_connection()
    t_id = st.session_state.current_tournament_id
    
    if not t_id:
        st.info("No active tournament found. Please create one.")
    else:
        check_or_create_grand_final(conn, t_id)
        tourn = conn.execute("SELECT * FROM tournaments WHERE id = ?", (t_id,)).fetchone()
        st.subheader(f"{tourn['name']}")
        
        matches = conn.execute("""
            SELECT m.*, wp.name as white_name, bp.name as black_name
            FROM matches m
            LEFT JOIN players wp ON m.white_player_id = wp.id
            LEFT JOIN players bp ON m.black_player_id = bp.id
            WHERE m.tournament_id = ?
            ORDER BY CASE WHEN m.group_name = 'Grand Final' THEN 0 ELSE 1 END, m.round_num, m.id
        """, (t_id,)).fetchall()
        
        filter_status = st.selectbox("Filter Matches", ["All", "Upcoming", "In Progress", "Completed"])
        
        for m in matches:
            if filter_status != "All" and m['status'] != filter_status:
                continue
                
            is_final = (m['group_name'] == 'Grand Final')
            status_color = "#0FA4AF" if m['status'] == 'Completed' else ("#964734" if m['status'] == 'In Progress' else "#AFDDE5")
            border_style = "3px solid #0FA4AF" if is_final else f"1px solid {status_color}"
            stage_badge = "🏆 GRAND FINAL (TOP 1 vs TOP 2)" if is_final else f"League Round {m['round_num']}"
            res_text = f" &nbsp;|&nbsp; Result: <b style='color:#0FA4AF;'>{m['result']}</b>" if m['result'] else ""
            
            card_html = (
                f"<div class='glass-panel' style='border:{border_style};border-left:6px solid {status_color};padding:14px;'>"
                f"<div style='font-size:14px;color:#0FA4AF;font-weight:bold;'>{stage_badge}</div>"
                f"<div style='font-size:20px;color:#ffffff;margin:6px 0;'>♔ <b>{m['white_name']}</b> &nbsp;vs&nbsp; ♚ <b>{m['black_name']}</b></div>"
                f"<div style='font-size:14px;'>Status: <b style='color:{status_color};'>{m['status']}</b>{res_text}</div>"
                f"</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            if m['status'] != 'Completed':
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    btn_label = "⏱️ Play / Open Clock" if m['status'] == 'Upcoming' else "⏱️ Resume Clock"
                    if st.button(btn_label, key=f"start_m_{m['id']}"):
                        conn.execute("UPDATE matches SET status = 'In Progress' WHERE id = ?", (m['id'],))
                        conn.commit()
                        st.session_state.active_match_id = m['id']
                        safe_rerun()
                with col_b2:
                    if st.button("✅ Quick Record Result", key=f"quick_rec_{m['id']}"):
                        st.session_state[f"show_quick_{m['id']}"] = True
                        
                if st.session_state.get(f"show_quick_{m['id']}", False):
                    q_cols = st.columns(3)
                    with q_cols[0]:
                        if st.button(f"♔ {m['white_name']} (1-0)", key=f"qw_{m['id']}"):
                            conn.execute("UPDATE matches SET status = 'Completed', result = '1-0' WHERE id = ?", (m['id'],))
                            conn.commit()
                            st.session_state[f"show_quick_{m['id']}"] = False
                            check_or_create_grand_final(conn, t_id)
                            safe_rerun()
                    with q_cols[1]:
                        if st.button(f"♚ {m['black_name']} (0-1)", key=f"qb_{m['id']}"):
                            conn.execute("UPDATE matches SET status = 'Completed', result = '0-1' WHERE id = ?", (m['id'],))
                            conn.commit()
                            st.session_state[f"show_quick_{m['id']}"] = False
                            check_or_create_grand_final(conn, t_id)
                            safe_rerun()
                    with q_cols[2]:
                        if st.button("🤝 Draw (½-½)", key=f"qd_{m['id']}"):
                            conn.execute("UPDATE matches SET status = 'Completed', result = '½-½' WHERE id = ?", (m['id'],))
                            conn.commit()
                            st.session_state[f"show_quick_{m['id']}"] = False
                            check_or_create_grand_final(conn, t_id)
                            safe_rerun()
    conn.close()

# ----------------------------------------------------
# 5. LIVE CHESS CLOCK
# ----------------------------------------------------
elif menu == "⏱️ Live Chess Clock":
    st.title("⏱️ Live Chess Clock")
    conn = get_connection()
    t_id = st.session_state.current_tournament_id
    
    if not t_id:
        st.warning("No active tournament.")
    else:
        active_m_id = st.session_state.active_match_id
        if not active_m_id:
            in_prog = conn.execute("SELECT id FROM matches WHERE tournament_id = ? AND status = 'In Progress'", (t_id,)).fetchone()
            if in_prog:
                active_m_id = in_prog['id']
                st.session_state.active_match_id = active_m_id
                
        if not active_m_id:
            st.info("No match selected. Go to **Match List** and tap **Play / Open Clock**.")
        else:
            match = conn.execute("""
                SELECT m.*, wp.name as white_name, bp.name as black_name, t.increment_secs 
                FROM matches m
                JOIN players wp ON m.white_player_id = wp.id
                JOIN players bp ON m.black_player_id = bp.id
                JOIN tournaments t ON m.tournament_id = t.id
                WHERE m.id = ?
            """, (active_m_id,)).fetchone()
            
            if match:
                stage_title = "🏆 GRAND FINAL" if match['group_name'] == 'Grand Final' else f"League Round {match['round_num']}"
                st.subheader(f"{stage_title}: {match['white_name']} vs {match['black_name']}")
                
                clock_key = f"clock_{match['id']}"
                if clock_key not in st.session_state:
                    st.session_state[clock_key] = {
                        'white_time': match['white_time_left'],
                        'black_time': match['black_time_left'],
                        'active': match['active_clock'],
                        'running': bool(match['clock_running']),
                        'last_tick': time.time()
                    }
                c_state = st.session_state[clock_key]
                
                def fmt_time(secs):
                    return f"{int(secs // 60):02d}:{int(secs % 60):02d}"

                w_bg = "rgba(15, 164, 175, 0.45)" if c_state['active'] == 'white' else "rgba(0, 36, 40, 0.92)"
                w_color = "#964734" if c_state['white_time'] < 30 else "#ffffff"
                st.markdown(f"<div style='background-color:{w_bg};border:3px solid #0FA4AF;border-radius:16px;padding:20px;text-align:center;margin-bottom:10px;'><h3 style='color:#AFDDE5;margin:0;'>♔ WHITE: {match['white_name']}</h3><h1 style='font-size:60px;font-family:monospace;color:{w_color};margin:8px 0;'>{fmt_time(c_state['white_time'])}</h1></div>", unsafe_allow_html=True)
                
                if st.button("👆 TAP AFTER WHITE MOVES (Start Black's Clock)", key="tap_white"):
                    if c_state['running'] and c_state['active'] == 'white':
                        c_state['active'] = 'black'
                        c_state['white_time'] += match['increment_secs']
                    elif not c_state['running']:
                        c_state['running'] = True
                        c_state['active'] = 'white'
                    safe_rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                b_bg = "rgba(150, 71, 52, 0.5)" if c_state['active'] == 'black' else "rgba(0, 36, 40, 0.92)"
                b_color = "#964734" if c_state['black_time'] < 30 else "#ffffff"
                st.markdown(f"<div style='background-color:{b_bg};border:3px solid #964734;border-radius:16px;padding:20px;text-align:center;margin-bottom:10px;'><h3 style='color:#AFDDE5;margin:0;'>♚ BLACK: {match['black_name']}</h3><h1 style='font-size:60px;font-family:monospace;color:{b_color};margin:8px 0;'>{fmt_time(c_state['black_time'])}</h1></div>", unsafe_allow_html=True)
                
                if st.button("👆 TAP AFTER BLACK MOVES (Start White's Clock)", key="tap_black"):
                    if c_state['running'] and c_state['active'] == 'black':
                        c_state['active'] = 'white'
                        c_state['black_time'] += match['increment_secs']
                    elif not c_state['running']:
                        c_state['running'] = True
                        c_state['active'] = 'black'
                    safe_rerun()
                        
                st.markdown("---")
                ctrl_cols = st.columns(2)
                with ctrl_cols[0]:
                    if st.button("⏯️ Pause / Resume"):
                        c_state['running'] = not c_state['running']
                        safe_rerun()
                with ctrl_cols[1]:
                    if st.button("🔄 Reset Clocks"):
                        c_state['white_time'] = match['white_time_left']
                        c_state['black_time'] = match['black_time_left']
                        c_state['active'] = None
                        c_state['running'] = False
                        safe_rerun()
                        
                if st.button("🏁 Finish Game & Record Winner"):
                    c_state['running'] = False
                    st.session_state.show_result_modal = True
                    safe_rerun()
                        
                if c_state['running']:
                    now = time.time()
                    elapsed = now - c_state['last_tick']
                    c_state['last_tick'] = now
                    if c_state['active'] == 'white':
                        c_state['white_time'] = max(0, c_state['white_time'] - elapsed)
                    elif c_state['active'] == 'black':
                        c_state['black_time'] = max(0, c_state['black_time'] - elapsed)
                    time.sleep(0.5)
                    safe_rerun()
                else:
                    c_state['last_tick'] = time.time()
                    
                if st.session_state.get('show_result_modal', False):
                    st.markdown("### 🏆 Select Match Winner")
                    res_choice = st.radio("Outcome", [
                        f"White Wins ({match['white_name']}) - 1-0",
                        f"Black Wins ({match['black_name']}) - 0-1",
                        "Draw - ½-½"
                    ])
                    if st.button("💾 Save Match Result"):
                        result_str = "1-0" if "1-0" in res_choice else ("0-1" if "0-1" in res_choice else "½-½")
                        conn.execute("UPDATE matches SET status = 'Completed', result = ? WHERE id = ?", (result_str, match['id']))
                        conn.commit()
                        check_or_create_grand_final(conn, t_id)
                        st.session_state.show_result_modal = False
                        st.session_state.active_match_id = None
                        st.success("Result saved!")
                        safe_rerun()
    conn.close()

# ----------------------------------------------------
# 6. STANDINGS & TOP 2 FINAL (POINTS TABLE + VISUAL BRACKET)
# ----------------------------------------------------
elif menu == "📊 Standings & Top 2 Final":
    st.title("📊 Points Table & Tournament Bracket")
    
    conn = get_connection()
    t_id = st.session_state.current_tournament_id
    
    if not t_id:
        st.info("No active tournament.")
    else:
        check_or_create_grand_final(conn, t_id)
        tourn = conn.execute("SELECT * FROM tournaments WHERE id = ?", (t_id,)).fetchone()
        st.subheader(f"🏆 {tourn['name']}")
        
        standings = compute_league_standings(conn, t_id)
        
        if standings:
            # 1. RENDER CLEAN POINTS TABLE (Single-line HTML so Streamlit never shows raw tags)
            rows_list = []
            for rank, s in enumerate(standings, 1):
                row_class = "top-two-row" if rank <= 2 else ""
                badge = "🥇 #1 (Finalist)" if rank == 1 else ("🥈 #2 (Finalist)" if rank == 2 else f"#{rank}")
                row_str = (
                    f"<tr class='{row_class}'>"
                    f"<td><b>{badge}</b></td>"
                    f"<td class='player-col'><b>{s['Player']}</b></td>"
                    f"<td>{s['Played']}</td>"
                    f"<td style='color:#0FA4AF;'><b>{s['Wins']}</b></td>"
                    f"<td>{s['Draws']}</td>"
                    f"<td style='color:#964734;'>{s['Losses']}</td>"
                    f"<td><span class='pts-badge'>{s['Points']}</span></td>"
                    f"</tr>"
                )
                rows_list.append(row_str)
                
            full_table_html = (
                "<table class='custom-table'>"
                "<thead><tr>"
                "<th>Rank</th><th class='player-col'>Player</th><th>Played</th><th>Won</th><th>Drawn</th><th>Lost</th><th>Points</th>"
                "</tr></thead>"
                f"<tbody>{''.join(rows_list)}</tbody>"
                "</table>"
            )
            st.markdown(full_table_html, unsafe_allow_html=True)
            
            # 2. VISUAL CHAMPIONSHIP BRACKET (TOP 2 QUALIFICATION)
            st.markdown("### 🗺️ Championship Progression Bracket")
            
            top1_name = standings[0]['Player'] if len(standings) >= 1 else "TBD"
            top1_pts = standings[0]['Points'] if len(standings) >= 1 else 0.0
            top2_name = standings[1]['Player'] if len(standings) >= 2 else "TBD"
            top2_pts = standings[1]['Points'] if len(standings) >= 2 else 0.0
            
            final_match = conn.execute("""
                SELECT m.*, wp.name as white_name, bp.name as black_name
                FROM matches m
                JOIN players wp ON m.white_player_id = wp.id
                JOIN players bp ON m.black_player_id = bp.id
                WHERE m.tournament_id = ? AND m.group_name = 'Grand Final'
            """, (t_id,)).fetchone()
            
            if final_match:
                f_white = final_match['white_name']
                f_black = final_match['black_name']
                f_status = final_match['status']
                if f_status == 'Completed':
                    champ_name = f_white if final_match['result'] == '1-0' else (f_black if final_match['result'] == '0-1' else "Shared Title")
                    f_sub = f"Result: {final_match['result']}"
                else:
                    champ_name = "Awaiting Final"
                    f_sub = f"Status: {f_status}"
            else:
                f_white = top1_name
                f_black = top2_name
                f_sub = "Projected Matchup"
                champ_name = "TBD"
                
            bracket_html = (
                "<div class='bracket-wrapper'>"
                "<div style='display:flex;flex-direction:column;gap:14px;'>"
                f"<div class='bracket-box'><div style='font-size:12px;color:#0FA4AF;'>🥇 RANK #1 SEED</div><div style='font-size:18px;font-weight:bold;color:#fff;margin:4px 0;'>{top1_name}</div><div style='font-size:13px;'>{top1_pts} Pts</div></div>"
                f"<div class='bracket-box'><div style='font-size:12px;color:#0FA4AF;'>🥈 RANK #2 SEED</div><div style='font-size:18px;font-weight:bold;color:#fff;margin:4px 0;'>{top2_name}</div><div style='font-size:13px;'>{top2_pts} Pts</div></div>"
                "</div>"
                "<div class='bracket-arrow'>➔</div>"
                f"<div class='bracket-box final-box'><div style='font-size:13px;color:#AFDDE5;font-weight:bold;'>⚔️ GRAND FINAL</div><div style='font-size:17px;color:#fff;margin:8px 0;'>♔ <b>{f_white}</b><br><span style='font-size:12px;color:#0FA4AF;'>VS</span><br>♚ <b>{f_black}</b></div><div style='font-size:12px;color:#0FA4AF;'>{f_sub}</div></div>"
                "<div class='bracket-arrow'>➔</div>"
                f"<div class='bracket-box champ-box'><div style='font-size:13px;color:#0FA4AF;font-weight:bold;'>👑 CHAMPION</div><div style='font-size:22px;font-weight:900;color:#ffffff;margin:10px 0;'>🏆 {champ_name}</div></div>"
                "</div>"
            )
            st.markdown(bracket_html, unsafe_allow_html=True)
            
            if not final_match and len(standings) >= 2:
                if st.button("⚡ Lock Standings & Generate Top 2 Grand Final Now"):
                    tc_secs = tourn['time_control_mins'] * 60
                    conn.execute(
                        "INSERT INTO matches (tournament_id, round_num, group_name, white_player_id, black_player_id, status, white_time_left, black_time_left) VALUES (?, 99, 'Grand Final', ?, ?, 'Upcoming', ?, ?)",
                        (t_id, standings[0]['id'], standings[1]['id'], tc_secs, tc_secs)
                    )
                    conn.commit()
                    safe_rerun()
            elif final_match and final_match['status'] != 'Completed':
                if st.button("⏱️ Open Grand Final Chess Clock"):
                    conn.execute("UPDATE matches SET status = 'In Progress' WHERE id = ?", (final_match['id'],))
                    conn.commit()
                    st.session_state.active_match_id = final_match['id']
                    safe_rerun()

            # 3. VISUAL TOURNAMENT MATCH BOXES BY ROUND
            st.markdown("### 📦 League Stage Match Boxes")
            all_league_matches = conn.execute("""
                SELECT m.*, wp.name as white_name, bp.name as black_name
                FROM matches m
                LEFT JOIN players wp ON m.white_player_id = wp.id
                LEFT JOIN players bp ON m.black_player_id = bp.id
                WHERE m.tournament_id = ? AND m.group_name = 'League Stage'
                ORDER BY m.round_num, m.id
            """, (t_id,)).fetchall()
            
            if all_league_matches:
                cards_html_list = []
                for m in all_league_matches:
                    w_score = "1" if m['result'] == '1-0' else ("½" if m['result'] == '½-½' else ("0" if m['result'] == '0-1' else "-"))
                    b_score = "1" if m['result'] == '0-1' else ("½" if m['result'] == '½-½' else ("0" if m['result'] == '1-0' else "-"))
                    top_border = "#0FA4AF" if m['status'] == 'Completed' else ("#964734" if m['status'] == 'In Progress' else "#AFDDE5")
                    
                    box_str = (
                        f"<div class='match-box-card' style='border-top-color:{top_border};'>"
                        f"<div style='display:flex;justify-content:space-between;font-size:12px;color:#0FA4AF;margin-bottom:6px;'><b>ROUND {m['round_num']}</b><span>{m['status']}</span></div>"
                        f"<div class='match-box-row'><span>♔ {m['white_name']}</span><b style='color:#0FA4AF;'>{w_score}</b></div>"
                        f"<div class='match-box-row'><span>♚ {m['black_name']}</span><b style='color:#0FA4AF;'>{b_score}</b></div>"
                        f"</div>"
                    )
                    cards_html_list.append(box_str)
                    
                st.markdown(f"<div class='round-grid'>{''.join(cards_html_list)}</div>", unsafe_allow_html=True)
                
    conn.close()

# ----------------------------------------------------
# 7. SETTINGS
# ----------------------------------------------------
elif menu == "⚙️ Settings":
    st.title("⚙️ Tournament Settings")
    conn = get_connection()
    t_id = st.session_state.current_tournament_id
    
    if t_id:
        tourn = conn.execute("SELECT * FROM tournaments WHERE id = ?", (t_id,)).fetchone()
        st.markdown(f"<div class='glass-panel'><h3>Current Tournament: {tourn['name']}</h3><p><b>Format:</b> Everyone Plays Everyone (League) + Top 2 Final</p><p><b>Time Control:</b> {tourn['time_control_mins']} mins + {tourn['increment_secs']}s increment</p></div>", unsafe_allow_html=True)
        
        if st.button("🗑️ Delete Current Tournament & Reset"):
            conn.execute("DELETE FROM matches WHERE tournament_id = ?", (t_id,))
            conn.execute("DELETE FROM tournament_participants WHERE tournament_id = ?", (t_id,))
            conn.execute("DELETE FROM tournaments WHERE id = ?", (t_id,))
            conn.commit()
            st.session_state.current_tournament_id = None
            st.session_state.active_match_id = None
            st.success("Tournament deleted.")
            safe_rerun()
    else:
        st.info("No active tournament.")
    conn.close()