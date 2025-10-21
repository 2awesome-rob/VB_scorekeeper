import pandas as pd
import streamlit as st


st.set_page_config(page_title="Volleyball Stat Recorder", page_icon="🏐")


st.sidebar.subheader("Starting Lineup")
START_LINEUP = {}
for i in range(1, 7):
    START_LINEUP[f"position_{i}"] = st.sidebar.number_input(
        f"Jersey # at Position {i}", min_value=1, value=i
    )

START_ROTATION = st.sidebar.slider("Rotation", min_value=1, max_value=6, value=1)
st.sidebar.header("Initialize Set")
GAME_ID = st.sidebar.text_input(
    "Game ID", value="", max_chars=16, placeholder="KLA-YY-MM-DD-1"
)
SET_NUMBER = str(
    st.sidebar.number_input("Set", min_value=1, max_value=5, value=1)
)
GAME_SET = f"{GAME_ID}-{SET_NUMBER}"
FIRST_SERVE = st.sidebar.selectbox("Who is serving?", options=["us", "them"])
PLAY_TO = st.sidebar.number_input("Game to", min_value=15, value=25)


def reset_rally_results():
    st.session_state.rally_result = None
    st.session_state.block_result = None
    st.session_state.block_confirmed = False
    st.session_state.return_rally_result = None
    st.session_state.touch_phase = 1
    st.session_state.player = None


def reset_session_state():
    st.session_state.radio_counter = 0
    st.session_state.select_counter = 0
    st.session_state.score_us = 0
    st.session_state.score_them = 0
    rally_step = 0 if FIRST_SERVE == "us" else 1
    st.session_state.rally_step = rally_step
    st.session_state.lineup = START_LINEUP
    st.session_state.rotation = START_ROTATION
    st.session_state.game_over = False
    reset_rally_results()

    index = pd.MultiIndex.from_tuples(
        [(GAME_SET, 0, 0, rally_step)],
        names=["game", "score_us", "score_them", "rally_step"],
    )

    data = {
        **START_LINEUP,
        "rotation": START_ROTATION,
        "touch_serve": None,
        "touch_block": None,
        "touch_block_asst": None,
        "touch_1": None,
        "touch_2": None,
        "touch_3": None,
        "sanctions": None,
    }

    st.session_state.df = pd.DataFrame([data], index=index)


def add_new_row():
    reset_rally_results()

    index = pd.MultiIndex.from_tuples(
        [
            (
                GAME_SET,
                st.session_state.score_us,
                st.session_state.score_them,
                st.session_state.rally_step,
            )
        ],
        names=["game", "score_us", "score_them", "rally_step"],
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

    df = pd.DataFrame([data], index=index)
    st.session_state.df = pd.concat([st.session_state.df, df])


def point_us():
    st.session_state.score_us += 1
    if st.session_state.rally_step % 2 == 1:
        st.session_state.rotation = st.session_state.rotation % 6 + 1

    st.session_state.rally_step = 0
    add_new_row()

    if (
        st.session_state.score_us >= PLAY_TO
        and st.session_state.score_us >= st.session_state.score_them + 2
    ):
        st.session_state.game_over = True
        st.success("We Win!")


def point_them():
    st.session_state.score_them += 1
    st.session_state.rally_step = 1
    add_new_row()

    if (
        st.session_state.score_them >= PLAY_TO
        and st.session_state.score_them >= st.session_state.score_us + 2
    ):
        st.session_state.game_over = True
        st.error("Game Over Man")


def over_net(check_for_point=True):
    st.session_state.rally_step += 2

    if check_for_point:
        if st.session_state.return_rally_result is None:
            st.session_state.return_rally_result = st.radio(
                "They Rally",
                options=["Error", "Return"],
                key=f"result_{st.session_state.radio_counter}",
                index=None,
            )

        if st.session_state.return_rally_result is not None:
            if st.button("Confirm Rally Result"):
                st.session_state.radio_counter += 1

                if st.session_state.return_rally_result == "Error":
                    point_us()
                else:
                    add_new_row()
    else:
        add_new_row()


def handle_serve():
    row_idx = len(st.session_state.df) - 1
    player = st.session_state.df.iloc[row_idx][
        f"position_{st.session_state.rotation}"
    ]

    st.markdown(f"🟢 **{player}** to serve:")

    with st.form(key=f"serve_form_{st.session_state.radio_counter}"):
        serve_result = st.radio(
            "Result of the serve:", options=["Ace", "Error", "Return"], index=None
        )

        submitted = st.form_submit_button(f"✅ Confirm {serve_result}")

        if submitted and serve_result:
            st.session_state.radio_counter += 1
            st.session_state.df.at[
                st.session_state.df.index[row_idx], "touch_serve"
            ] = f"{player}:{serve_result}"

            if serve_result == "Ace":
                point_us()
            elif serve_result == "Error":
                point_them()
            elif serve_result == "Return":
                over_net(False)


def pos(i):
    if i % 6 == 0:
        return 6
    return i % 6


def rally():
    row_idx = len(st.session_state.df) - 1

    block_options = [
        st.session_state.df.iloc[row_idx][f"position_{pos(st.session_state.rotation + j)}"]
        for j in [3, 2, 1]
    ]

    touch_options = [st.session_state.df.iloc[row_idx][f"position_{i}"] for i in range(1, 7)]

    with st.form(key=f"rally_form_{st.session_state.radio_counter}"):
        if st.session_state.rally_step == 1:
            their_result = st.radio(
                "Result of the serve:", options=["Over", "Error"], index=None
            )
        else:
            their_result = st.radio(
                "Result of their rally:", options=["Over", "Error"], index=None
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### Block")
            blocker = st.selectbox("Blocker", options=block_options, index=None)
            block_result = st.radio(
                "Block Result",
                options=["Block", "Block:Kill", "Block:Tip", "Block:Assist", "NoBlock"],
                index=4,
            )

            second_blocker = st.selectbox(
                "Second Blocker",
                options=[p for p in block_options if p != blocker],
                index=None,
            )

        with col2:
            st.markdown("### Touch 1")
            player1 = st.selectbox(
                "Player",
                options=touch_options,
                key="player1_" + str(st.session_state.select_counter),
                index=None,
            )

            touch1 = st.selectbox(
                "Touch",
                options=["Dig", "Pass", "Set", "Attack"],
                key="touch1_" + str(st.session_state.select_counter),
                index=None,
            )

            result1 = st.selectbox(
                "Result",
                options=["Missed", "Error", "1", "2", "3", "Kill", "Over"],
                key="result1_" + str(st.session_state.select_counter),
                index=None,
            )

        with col3:
            st.markdown("### Touch 2")
            player2 = st.selectbox(
                "Player",
                options=touch_options,
                key="player2_" + str(st.session_state.select_counter),
                index=None,
            )

            touch2 = st.selectbox(
                "Touch",
                options=["Pass", "Set", "Attack"],
                key="touch2_" + str(st.session_state.select_counter),
                index=None,
            )

            result2 = st.selectbox(
                "Result",
                options=["Error", "1", "2", "3", "Kill", "Over"],
                key="result2_" + str(st.session_state.select_counter),
                index=None,
            )

        with col4:
            st.markdown("### Touch 3")
            player3 = st.selectbox(
                "Player",
                options=touch_options,
                key="player3_" + str(st.session_state.select_counter),
                index=None,
            )

            touch3 = st.selectbox(
                "Touch",
                options=["Pass", "Set", "Attack"],
                key="touch3_" + str(st.session_state.select_counter),
                index=None,
            )

            result3 = st.selectbox(
                "Result",
                options=["Error", "1", "2", "3", "Kill", "Over"],
                key="result3_" + str(st.session_state.select_counter),
                index=None,
            )

        submitted = st.form_submit_button("✅ Confirm Rally")

        if submitted:
            st.session_state.radio_counter += 1
            st.session_state.select_counter += 1

            if their_result == "Error":
                point_us()

            if block_result != "NoBlock":
                st.session_state.df.at[
                    st.session_state.df.index[row_idx], "touch_block"
                ] = f"{blocker}:{block_result}"

            if block_result == "Block:Assist" and second_blocker:
                st.session_state.df.at[
                    st.session_state.df.index[row_idx], "touch_block_asst"
                ] = f"{second_blocker}:Block:Assist"

            if block_result in ["Block:Kill", "Block:Assist"]:
                point_us()
                return
            elif block_result == "Block:Error":
                point_them()
                return
            elif block_result == "Block":
                over_net()
                return

            if result1:
                st.session_state.df.at[
                    st.session_state.df.index[row_idx], "touch_1"
                ] = f"{player1}:{touch1}:{result1}"

            if result2:
                st.session_state.df.at[
                    st.session_state.df.index[row_idx], "touch_2"
                ] = f"{player2}:{touch2}:{result2}"

            if result3:
                st.session_state.df.at[
                    st.session_state.df.index[row_idx], "touch_3"
                ] = f"{player3}:{touch3}:{result3}"

            for result in [result1, result2, result3]:
                if result in ["Error", "Missed"]:
                    point_them()
                    return
                elif result == "Kill":
                    point_us()
                    return
                elif result == "Over":
                    over_net()
                    return


if "df" not in st.session_state:
    reset_session_state()

if st.sidebar.button("🔄 Reset Match"):
    reset_session_state()

st.title(f"🏐 {GAME_SET} | Us: {st.session_state.score_us}    Them: {st.session_state.score_them}")
st.dataframe(st.session_state.df.tail(5), use_container_width=True)
st.download_button(
    "📥 Export Match Data",
    data=st.session_state.df.to_csv().encode("utf-8"),
    file_name=f"{GAME_SET}_stats.csv",
    mime="text/csv",
)

st.subheader("Volley Tracker")

if not st.session_state.game_over:
    if st.session_state.rally_step == 0:
        handle_serve()
    else:
        rally()
