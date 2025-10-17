import numpy as np
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Vollyball Stat Recorder", page_icon="🏐")

# --- Setup Game in Sidebar ---
st.sidebar.subheader("Starting Lineup")
START_LINEUP = {}
for i in range(1, 7):
    START_LINEUP[f"position_{i}"] = st.sidebar.number_input(f"Jersey # at Position {i}", min_value=1, value=i)
START_ROTATION = st.sidebar.slider("Rotation", min_value=1, max_value=6, value=1)
st.sidebar.header("Initialize Set")
GAME_ID = st.sidebar.text_input("Game ID", value="", max_chars=16, placeholder="KLA-YY-MM-DD-1")
SET_NUMBER = str(st.sidebar.number_input("Set", min_value=1, max_value=5, value=1))
GAME_SET =  f"{GAME_ID}-{SET_NUMBER}" 
FIRST_SERVE = st.sidebar.selectbox("Who is serving?", options=["us", "them"])
PLAY_TO = st.sidebar.number_input("Game to", min_value=15, value=25)

# --- Initialize Session State --- 
def reset_session_state():
    st.session_state.score_us = 0
    st.session_state.score_them = 0
    rally_step = 0 if FIRST_SERVE == "us" else 1
    st.session_state.rally_step = rally_step
    st.session_state.lineup = START_LINEUP
    st.session_state.rotation = START_ROTATION
    st.session_state.row_idx = 0
    st.session_state.game_over = False
    st.session_state.radio_counter = 0
    st.session_state.select_counter = 0
    st.session_state.touch_phase = 1
    st.session_state.rally_result = None
    st.session_state.player = None
    st.session_state.block_result = None
    index = pd.MultiIndex.from_tuples([(GAME_SET, 0, 0, rally_step)],
                                      names=["game", "score_us", "score_them", "rally_step"])
    data = {
            **START_LINEUP,
            "rotation": START_ROTATION,
            "touch_serve": None, 
            "touch_block": None,
            "touch_block_asst": None,
            'touch_1': None,
            'touch_2': None,
            'touch_3': None,
            'sanctions': None,
    }   
    st.session_state.df = pd.DataFrame([data], index=index)
#    st.session_state.phase_confirmed = False
#    st.session_state.touch_phase = 1
    pass

if "df" not in st.session_state: reset_session_state()
if st.sidebar.button("🔄 Reset Match"): reset_session_state()

# --- Define Helper Functions ---

def reset_rally_results():
    st.session_state.touch_phase = 1
    st.session_state.rally_result = None
    st.session_state.player = None
    st.session_state.block_result = None

def add_new_row():
    reset_rally_results()
    index = pd.MultiIndex.from_tuples(
        [(GAME_SET, st.session_state.score_us, st.session_state.score_them, st.session_state.rally_step)],
        names=["game", "score_us", "score_them", "rally_step"]
    )
    data = {
        **st.session_state.lineup,
        "rotation": st.session_state.rotation,
        "touch_serve": None,
        "touch_block": None,
        "touch_block_asst": None,
        "touch_1": None,
        "touch_2": None,
        "touch_3": None,
        "sanctions": None,
    }
    new_df = pd.DataFrame([data], index=index)
    st.session_state.df = pd.concat([st.session_state.df, new_df])
    st.session_state.row_idx += 1

def point_us():
    st.session_state.score_us += 1
    if st.session_state.rally_step % 2 == 1:
        st.session_state.rotation = st.session_state.rotation % 6 + 1 
    add_new_row()
    if st.session_state.score_us >= PLAY_TO and st.session_state.score_us >= st.session_state.score_them + 2: 
        st.session_state.game_over = True
        st.success("We Win!")

def point_them():
    st.session_state.score_them += 1
    st.session_state.rally_step = 1
    add_new_row()
    if st.session_state.score_them >= PLAY_TO and st.session_state.score_them >= st.session_state.score_us + 2: 
        st.session_state.game_over = True
        st.error("Game Over Man")

def over_net(check_for_point=True):
    st.session_state.rally_step +=2
    reset_rally_results()
    if check_for_point: 
        rally_result = st.radio("They Rally", options=["Error", "Return"], key=f"result_{st.session_state.radio_counter}", index=None)
        if st.button("Confirm Rally Result"):
            st.session_state.radio_counter += 1
            if rally_result == "Error": point_us()
            else: add_new_row()
    else: add_new_row()

def handle_serve():
    row_idx = len(st.session_state.df)-1
    player = st.session_state.df.iloc[row_idx][f"position_{st.session_state.rotation}"]
    st.markdown(f"🟢 **{player}** to serve:")
    if st.session_state.rally_result is None:
        st.session_state.rally_result = st.radio(
            "Result of the serve:", 
            options=["Ace", "Error", "Return"], 
            index=None,
            key=f"result_{st.session_state.radio_counter}")
    if st.session_state.rally_result is not None:
        if st.button(f"Confirm {st.session_state.rally_result}"):
            st.session_state.radio_counter += 1
            st.session_state.df.at[st.session_state.df.index[row_idx], "touch_serve"] = str(player) + ":" + st.session_state.rally_result   
            if st.session_state.rally_result == "Ace":
#                st.success("Ace! We scored a point and continue serving.")
                point_us()
            elif st.session_state.rally_result == "Error":
#                st.error("Serve Error. Opponent scores and we switch to receive.")
                point_them()
            elif st.session_state.rally_result == "Return":
#                st.info("Serve returned. Prepare for defense and attack.")
                over_net(False)  
            
def handle_serve_receive():
    if st.session_state.rally_result is None:
        st.session_state.rally_result = st.radio("Result of the serve:", options=["Over", "Error"], key=f"result_{st.session_state.radio_counter}", index=None)
    if st.session_state.rally_result is not None:
        if st.button(f"Confirm {st.session_state.rally_result}"):
            st.session_state.radio_counter += 1
            if st.session_state.rally_result == "Error":
                point_us()
            else:
                st.session_state.rally_result = None
                defend_to_attack()

def check_for_block():
    row_idx = len(st.session_state.df)-1
    def pos(i): return 6 if i % 6 == 0 else i % 6
    options = [st.session_state.df.iloc[row_idx][f"position_{pos(st.session_state.rotation + j)}"] for j in [3, 2, 1]]
    st.info("Blocked?")
    if st.session_state.block_result is None or st.session_state.player is None:
        st.session_state.player = st.selectbox("Blocker", options=options, key=f"player_{st.session_state.select_counter}")
        st.session_state.block_result = st.radio("Block:", options=["Block","Block:Kill","Block:Tip","Block:Assist","NoBlock"], key=f"result_{st.session_state.radio_counter}", index=None)
    if st.session_state.rally_result is not None and st.session_state.player is not None:
        player = st.session_state.player
        if st.session_state.block_result == "Block:Assist":
            second_blocker = st.selectbox("Second Blocker", options=[p for p in options if p != player], key=f"block2_{st.session_state.select_counter}")
        if st.button(f"Confirm {st.st.session_state.block_result}"):
            st.session_state.radio_counter += 1
            st.session_state.select_counter += 1
            if st.session_state.block_result != "NoBlock":
                st.session_state.df.at[st.session_state.df.index[row_idx], "touch_block"] = f"{player}:{st.session_state.block_result}"
            if st.session_state.block_result == "Block:Assist":
                st.session_state.df.at[st.session_state.df.index[row_idx], "touch_block_asst"] = f"{second_blocker}:Block:Assist"
            if st.session_state.block_result in ["Block:Kill", "Block:Assist"]:
                point_us()
                return True
            elif st.session_state.block_result == "Block:Error":
                point_them()
                return True
            elif st.session_state.block_result == "Block":
                over_net()
                return True
            elif st.session_state.block_result in ["Block:Tip", "NoBlock"]: 
                return False

def record_touch(touch_num):
    row_idx = len(st.session_state.df)-1
    options=[st.session_state.df.iloc[row_idx][f"position_{i}"] for i in range(1,7)]
    player = st.selectbox(f"Player ", options=options, key=f"player_{st.session_state.select_counter}")
    if touch_num == 1:
        touch = st.selectbox(f"Touch {touch_num}", options=["Dig", "Pass", "Set", "Attack"], key=f"touch_{st.session_state.select_counter}", index = None)
        st.session_state.rally_result = st.selectbox(f"Result {touch_num}", options=["Missed", "Error", "1", "2", "3", "Kill", "Over"], key=f"result_{st.session_state.select_counter}", index = None)
    else: 
        touch = st.selectbox(f"Touch {touch_num}", options=["Pass", "Set", "Attack"], key=f"touch_{st.session_state.select_counter}", index = None)
        st.session_state.rally_result = st.selectbox(f"Result {touch_num}", options=["Error", "1", "2", "3", "Kill", "Over"], key=f"result_{st.session_state.select_counter}", index=None)
    st.session_state.select_counter += 1
    st.session_state.df.at[st.session_state.df.index[row_idx], f"touch_{touch_num}"] = f"{player}:{touch}:{st.session_state.rally_result}"
    return st.session_state.rally_result

def defend_to_attack():
    blocked = check_for_block()
    if blocked == False: 
        st.info("Rally - Defend and attack.")
        if "touch_phase" not in st.session_state:
            st.session_state.touch_phase = 1
        i = st.session_state.touch_phase

        if st.session_state.rally_result is None:
            st.session_state.rally_result = record_touch(i)

        if st.session_state.rally_result is not None:
            if st.button(f"Confirm Touch {i} {st.session_state.rally_result}"):
                if st.session_state.rally_result in ["Error", "Missed"]:
                    st.session_state.touch_phase = 1
                    point_them()
                elif st.session_state.rally_result == "Kill":
                    st.session_state.touch_phase = 1
                    point_us()
                elif st.session_state.rally_result == "Over":
                    st.session_state.touch_phase = 1
                    over_net()
                else: 
                    st.session_state.rally_result = None
                    st.session_state.touch_phase += 1

# --- Display Game Status ---
st.title(f"🏐 {GAME_SET} | Us: {st.session_state.score_us}    Them: {st.session_state.score_them}")
st.dataframe(st.session_state.df.tail(5), use_container_width=True)
st.download_button("📥 Export Match Data", data=st.session_state.df.to_csv().encode("utf-8"), file_name=f"{GAME_SET}_stats.csv", mime="text/csv")
st.subheader("Volley Tracker")

if not st.session_state.game_over:
    if st.session_state.rally_step == 0:
        handle_serve()
    elif st.session_state.rally_step == 1:
        handle_serve_receive()
    else:
        defend_to_attack()