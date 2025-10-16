#import datetime
#import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vollyball Stat Recorder", page_icon="🏐")

# --- Setup Game in Sidebar ---
st.sidebar.subheader("Lineup")
lineup = {}
for i in range(1, 7):
    lineup[f"position_{i}"] = st.sidebar.number_input(f"Jersey # at Position {i}", min_value=1, value=i)
rotation = st.sidebar.slider("Rotation", min_value=1, max_value=6, value=1)

st.sidebar.header("Initialize Set")
game_id = st.sidebar.text_input("Game ID", value="", max_chars=16, placeholder="KLA-YY-MM-DD-1")
set_number = str(st.sidebar.number_input("Set", min_value=1, max_value=5, value=1))
GAME_SET =  f"{game_id}-{set_number}" 
serving_team = st.sidebar.selectbox("Who is serving?", options=["us", "them"])

score_us = st.sidebar.number_input("Our Score", min_value=0, value=0)
score_them = st.sidebar.number_input("Opponent Score", min_value=0, value=0)
play_to = st.sidebar.number_input("Game to", min_value=15, value=25)
rally_step = 0 if serving_team == "us" else 1


st.title(f"🏐 {GAME_SET}")

# --- Create DataFrame ---
index = pd.MultiIndex.from_tuples([(GAME_SET, score_us, score_them, rally_step)],
                                  names=["game", "score_us", "score_them", "rally_step"])
data = {
    **lineup,
    "rotation": rotation,
    "touch_serve": None, 
    "touch_block": None,
    "touch_block_asst": None,
    'touch_1': None,
    'touch_2': None,
    'touch_3': None,
    'sanctions': None,
    'volley_idx': rally_step
}

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([data], index=index)
df = st.session_state.df


st.subheader("Initial Match State")
st.dataframe(df, use_container_width=True)

if st.sidebar.button("🔄 Reset Match"):
    st.session_state.row_idx = 0
    st.session_state.game_over = False
    st.session_state.radio_counter = 0
    st.session_state.select_counter = 0
    st.session_state.touch_phase = 1
    st.session_state.phase_confirmed = False
    st.session_state.df = pd.DataFrame([data], index=index)




###
# --- Extract Current State --- 
###
if "row_idx" not in st.session_state:
    st.session_state.row_idx = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "phase_confirmed" not in st.session_state:
    st.session_state.phase_confirmed = False


st.session_state.radio_counter = 0
st.session_state.select_counter = 0
if "touch_phase" not in st.session_state:
    st.session_state.touch_phase = 1



###
# Define Some Helper functions
###
def reset_phase():
    st.session_state.phase_confirmed = False
    st.session_state.radio_counter = 0
    st.session_state.select_counter = 0


def add_new_row():
    global df, row_idx, GAME_SET, score_us, score_them, rally_step, rotation, lineup
    # Construct new multi-index
    new_index = pd.MultiIndex.from_tuples(
        [(GAME_SET, score_us, score_them, rally_step)],
        names=["game", "score_us", "score_them", "rally_step"]
    )

    # Build new row with lineup and rotation
    new_data = {
        **lineup,
        "rotation": rotation,
        "touch_serve": None,
        "touch_block": None,
        "touch_block_asst": None,
        "touch_1": None,
        "touch_2": None,
        "touch_3": None,
        "sanctions": None,
        "volley_idx": rally_step  
    }
    # Append new row
    new_df = pd.DataFrame([new_data], index=new_index)
    st.session_state.df = pd.concat([st.session_state.df, new_df])


###
# outcome helpers
###
def point_us():
    global score_us, score_them, rotation, rally_step, play_to, game_over
    score_us += 1
    if rally_step % 2 == 1:
        rotation = rotation % 6 + 1 
    add_new_row()
    st.session_state.row_idx += 1
    if score_us >= play_to and score_us >= score_them + 2: 
        game_over = True
        st.success("We Win!")
    pass

def point_them():
    global score_us, score_them, rally_step, play_to, game_over
    score_them += 1
    rally_step = 1
    add_new_row()
    st.session_state.row_idx += 1
    if score_them >= play_to and score_them >= score_us + 2: 
        game_over = True
        st.error("Game Over Man")
    pass

def over_net(check_for_point=True):
    global rally_step
    rally_step +=2
    if check_for_point: 
        rally_result = st.radio("They Rally", options=["Error", "Return"], key=f"result_{st.session_state.radio_counter}", index=None)
        st.session_state.radio_counter += 1
        if rally_result == "Error": point_us()
        else: 
            add_new_row()
            st.session_state.row_idx += 1
    else: 
        add_new_row()
        st.session_state.row_idx += 1
    pass

def handle_serve():
    global df, row_idx, rotation
    player = df.iloc[row_idx][f"position_{rotation}"]
    st.markdown(f"🟢 **Serving Player:** Jersey #{player}")
    serve_result = st.radio("Result of the serve:", options=["Ace", "Error", "Return"], key=f"result_{st.session_state.radio_counter}", index=None)
    st.session_state.radio_counter += 1
    
    if st.button("Confirm Serve Result"):
        df.at[df.index[row_idx], "touch_serve"] = str(player) + ":" + serve_result
        st.success(f"Recorded serve result: **{serve_result}** by #{player}")
        if serve_result == "Ace":
            point_us()
            st.success("Ace! We scored a point and continue serving.")
        elif serve_result == "Error":
            point_them()
            st.error("Serve Error. Opponent scores and we switch to receive.")
        elif serve_result == "Return":
            over_net(False)  
            st.info("Serve returned. Prepare for defense and attack.")
        reset_phase()
        pass

def handle_serve_receive():
    serve_result = st.radio("Result of the serve:", options=["Over", "Error"], key=f"result_{st.session_state.radio_counter}", index=None)
    st.session_state.radio_counter += 1
    
    if st.button("Confirm Serve Result"):
        if serve_result == "Error":
            point_us()
        else:
            check_for_block()
            defend_to_attack()
        reset_phase()
        pass


def check_for_block():
    global df, row_idx
    st.info("Blocked?")
    block_result = st.radio("Block:", options=["Block","Block:Kill","Block:Tip","Block:Assist","NoBlock"], key=f"result_{st.session_state.radio_counter}", index=None)
    st.session_state.radio_counter += 1

    def pos(i): return 6 if i % 6 == 0 else i % 6
    options = [df.iloc[row_idx][f"position_{pos(rotation + j)}"] for j in [3, 2, 1]]
    blocker = st.selectbox("Blocker", options=options, key=f"player_{st.session_state.select_counter}")
    st.session_state.select_counter += 1

    if st.button("Confirm Block Result"):
        if block_result != "NoBlock":
            df.at[df.index[row_idx], "touch_block"] = f"{blocker}:{block_result}"
        if block_result == "Block:Assist":
            second_blocker = st.selectbox("Second Blocker", options=[p for p in options if p != blocker], key=f"player_{st.session_state.select_counter}")
            st.session_state.select_counter += 1
            df.at[df.index[row_idx], "touch_block_asst"] = f"{second_blocker}:Block:Assist"
        if block_result in ["Block:Kill", "Block:Assist"]:
            point_us()
        elif block_result == "Block:Error":
            point_them()
        elif block_result == "Block":
            over_net()
        reset_phase()
        pass


def record_touch(touch_num):
    options=[df.iloc[row_idx][f"position_{i}"] for i in range(1,7)]
    player = st.selectbox(f"Player ", options=options, key=f"player_{st.session_state.select_counter}")
    st.session_state.select_counter += 1

    if touch_num == 1:
        touch = st.selectbox(f"Touch {touch_num}", options=["Dig", "Pass", "Set", "Attack"], key=f"touch_{st.session_state.select_counter}", index = None)
        result = st.selectbox(f"Result {touch_num}", options=["Missed", "Error", "1", "2", "3", "Kill", "Over"], key=f"result_{st.session_state.select_counter}", index = None)
    else: 
        touch = st.selectbox(f"Touch {touch_num}", options=["Pass", "Set", "Attack"], key=f"touch_{st.session_state.select_counter}", index = None)
        result = st.selectbox(f"Result {touch_num}", options=["Error", "1", "2", "3", "Kill", "Over"], key=f"result_{st.session_state.select_counter}", index=None)
    st.session_state.select_counter += 1
    df.at[df.index[row_idx], f"touch_{touch_num}"] = f"{player}:{touch}:{result}"
    return result

def defend_to_attack():
    global df, row_idx
    st.info("Rally - Defend and attack.")
    i = st.session_state.touch_phase
    touch_result = record_touch(i)

    if st.button(f"Confirm Touch {i}"):
        if touch_result in ["Error", "Missed"]:
            point_them()
            st.session_state.touch_phase = 1
        elif touch_result == "Kill":
            point_us()
            st.session_state.touch_phase = 1
        elif touch_result == "Over":
            over_net()
            st.session_state.touch_phase = 1
        else:
            st.session_state.touch_phase += 1
        reset_phase()
        pass
            

st.subheader("Volley Tracker")

if not st.session_state.game_over:
    if st.session_state.row_idx >= len(st.session_state.df):
        add_new_row()
    row_idx = st.session_state.row_idx
    rotation = df.iloc[row_idx]["rotation"]
    current_row = df.iloc[row_idx]

    if current_row["volley_idx"] == 0:
        handle_serve()
    elif current_row["volley_idx"] == 1:
        handle_serve_receive()
    else:
        check_for_block()
        defend_to_attack()

    st.subheader("Updated Match State")
    st.dataframe(df, use_container_width=True)






