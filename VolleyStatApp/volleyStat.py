"""A clean, single-file Streamlit app for volleyball scorekeeping.

This version is written in one atomic update to avoid duplication and syntax
errors that appeared during earlier iterative patches.
"""


from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st


@dataclass
class RallyRow:
    position_1: int
    position_2: int
    position_3: int
    position_4: int
    position_5: int
    position_6: int
    rotation: int
    touch_serve: Optional[str] = None
    touch_block: Optional[str] = None
    touch_block_asst: Optional[str] = None
    touch_1: Optional[str] = None
    touch_2: Optional[str] = None
    touch_3: Optional[str] = None
    sanctions: Optional[str] = None
    point: Optional[str] = None


st.set_page_config(page_title="VolleyStat", layout="wide")
st.title("🏐 VolleyStat")

tabs = st.tabs([
    "Team Management",
    "Game Scheduling",
    "Live Tracking",
    "Archive & Export",
])


def ensure_state() -> None:
    """Ensure all necessary session state variables are initialized."""
    if "teams" not in st.session_state:
        st.session_state.teams = []
    if "matches" not in st.session_state:
        st.session_state.matches = []
    if "archived_matches" not in st.session_state:
        st.session_state.archived_matches = []
    if "current_match" not in st.session_state:
        st.session_state.current_match = None
    if "lineup" not in st.session_state:
        st.session_state.lineup = {f"position_{i}": i for i in range(1, 7)}
    if "rotation" not in st.session_state:
        st.session_state.rotation = 1
    if "score_us" not in st.session_state:
        st.session_state.score_us = 0
    if "score_them" not in st.session_state:
        st.session_state.score_them = 0
    if "events" not in st.session_state:
        st.session_state.events = []
    if "df" not in st.session_state:
        cols = [f"position_{i}" for i in range(1, 7)] + [
            "rotation",
            "touch_serve",
            "touch_block",
            "touch_block_asst",
            "touch_1",
            "touch_2",
            "touch_3",
            "sanctions",
            "point",
        ]
        st.session_state.df = pd.DataFrame(columns=cols)


ensure_state()


# Team Management
with tabs[0]:
    st.header("Team Management")
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Create Team")
        team_name = st.text_input("Team name")
        season = st.text_input("Season")
        if st.button("Create Team") and team_name:
            st.session_state.teams.append({"name": team_name, "season": season, "players": []})
            st.success("Team created")

        st.markdown("---")
        st.subheader("Teams & Rosters")
        for t_idx, team in enumerate(st.session_state.teams):
            with st.expander(f"{team['name']} ({team.get('season','')})"):
                st.write("Roster")
                for p_idx, p in enumerate(team["players"]):
                    cols = st.columns([1, 3, 1])
                    cols[0].write(f"#{p['jersey']}")
                    cols[1].write(p["name"])
                    if cols[2].button("Remove", key=f"remove_{t_idx}_{p_idx}"):
                        team["players"].pop(p_idx)
                        st.experimental_rerun()

                st.markdown("Add player")
                pname = st.text_input("Name", key=f"pname{t_idx}")
                pjersey = st.number_input("Jersey", min_value=1, key=f"pjersey{t_idx}")
                ppos = st.text_input("Position", key=f"ppos{t_idx}")
                if st.button("Add Player", key=f"addplayer{t_idx}") and pname:
                    if any(x["jersey"] == pjersey for x in team["players"]):
                        st.error("Duplicate jersey")
                    else:
                        team["players"].append({"name": pname, "jersey": int(pjersey), "position": ppos})
                        st.success("Player added")

    with right:
        st.subheader("Select Team")
        team_names = [t["name"] for t in st.session_state.teams]
        sel = st.selectbox("Team", options=[""] + team_names)
        if sel:
            team = next(t for t in st.session_state.teams if t["name"] == sel)
            st.write(f"Players: {len(team['players'])}")


# Scheduling
with tabs[1]:
    st.header("Scheduling")
    with st.form("add_match"):
        our_team = st.selectbox("Our Team", options=[""] + [t["name"] for t in st.session_state.teams])
        opponent = st.text_input("Opponent")
        match_date = st.date_input("Date", value=date.today())
        set_format = st.selectbox(
            "Set Format", ["Best of 5", "Best of 3", "Always Play 3"]
        )
        points_to_win = st.selectbox("Points to Win", [25, 15])
        submit = st.form_submit_button("Add Match")
        if submit and our_team and opponent:
            match_dict = {
                "our_team": our_team,
                "opponent": opponent,
                "date": match_date.isoformat(),
                "set_format": set_format,
                "points_to_win": int(points_to_win),
            }
            st.session_state.matches.append(match_dict)
            st.success("Match scheduled")

    st.markdown("---")
    st.subheader("Upcoming Matches")
    for m_idx, match in enumerate(st.session_state.matches):
        cols = st.columns([3, 1, 1])
        cols[0].write(f"{match['our_team']} vs {match['opponent']} — {match['date']}")
        if cols[1].button("Start Match", key=f"start_{m_idx}"):
            st.session_state.current_match = match
            team = next(
                (t for t in st.session_state.teams if t["name"] == match["our_team"]),
                None,
            )
            if team:
                players = sorted(team["players"], key=lambda p: p["jersey"])[:6]
                for i in range(1, 7):
                    if i <= len(players):
                        jersey = players[i - 1]["jersey"]
                    else:
                        jersey = i
                    st.session_state.lineup[f"position_{i}"] = jersey
            st.experimental_rerun()


# Game Tracking
with tabs[2]:
    st.header("Game Tracking")
    if not st.session_state.current_match:
        st.info("Start a match from Scheduling to begin tracking")
    else:
        st.subheader(f"{st.session_state.current_match['our_team']} vs {st.session_state.current_match['opponent']}")
        left, mid, right = st.columns([1, 2, 1])

        with left:
            st.markdown("### Scoreboard")
            st.markdown(f"**Us:** {st.session_state.score_us} — **Them:** {st.session_state.score_them}")
            if st.button("Point Us"):
                st.session_state.score_us += 1
                st.session_state.events.append({"point": "us"})
            if st.button("Point Them"):
                st.session_state.score_them += 1
                st.session_state.events.append({"point": "them"})
            if st.button("Undo Last"):
                if st.session_state.events:
                    last = st.session_state.events.pop()
                    if last.get("point") == "us":
                        st.session_state.score_us = max(0, st.session_state.score_us - 1)
                    elif last.get("point") == "them":
                        st.session_state.score_them = max(0, st.session_state.score_them - 1)
                    if not st.session_state.df.empty:
                        st.session_state.df = st.session_state.df.iloc[:-1]
                    st.success("Undid last event")

        with mid:
            st.markdown("### Serve Entry")
            server_pos = st.selectbox("Server position", options=list(range(1, 7)), index=st.session_state.rotation - 1)
            server_jersey = st.session_state.lineup.get(f"position_{server_pos}")
            serve_result = st.selectbox("Serve result", ["Ace", "Error", "Return"])
            if st.button("Record Serve"):
                row = RallyRow(
                    **st.session_state.lineup,
                    rotation=st.session_state.rotation,
                    touch_serve=f"{server_jersey}:{serve_result}",
                )
                if serve_result == "Ace":
                    row.point = "us"
                    st.session_state.score_us += 1
                elif serve_result == "Error":
                    row.point = "them"
                    st.session_state.score_them += 1
                st.session_state.events.append(asdict(row))
                st.session_state.df = pd.concat(
                    [st.session_state.df, pd.DataFrame([asdict(row)])],
                    ignore_index=True,
                )
                st.success("Serve recorded")

            st.markdown("---")
            st.markdown("### Rally Entry")
            c1, c2, c3 = st.columns(3)
            with c1:
                player1 = st.selectbox(
                    "Touch 1 - Player",
                    options=list(st.session_state.lineup.values()),
                    index=0,
                )
                touch1 = st.selectbox(
                    "Touch 1 - Type",
                    ["Dig", "Pass", "Set", "Attack"],
                )
                result1 = st.selectbox(
                    "Touch 1 - Result",
                    ["OK", "Error", "Kill", "Over"],
                )
            with c2:
                player2 = st.selectbox(
                    "Touch 2 - Player",
                    options=list(st.session_state.lineup.values()),
                    index=1,
                )
                touch2 = st.selectbox(
                    "Touch 2 - Type",
                    ["Pass", "Set", "Attack"],
                )
                result2 = st.selectbox(
                    "Touch 2 - Result",
                    ["OK", "Error", "Kill", "Over"],
                )
            with c3:
                player3 = st.selectbox(
                    "Touch 3 - Player",
                    options=list(st.session_state.lineup.values()),
                    index=2,
                )
                touch3 = st.selectbox(
                    "Touch 3 - Type",
                    ["Pass", "Set", "Attack"],
                )
                result3 = st.selectbox(
                    "Touch 3 - Result",
                    ["OK", "Error", "Kill", "Over"],
                )

            if st.button("Record Rally"):
                row = RallyRow(
                    **st.session_state.lineup,
                    rotation=st.session_state.rotation,
                )
                row.touch_1 = f"{player1}:{touch1}:{result1}"
                row.touch_2 = f"{player2}:{touch2}:{result2}"
                row.touch_3 = f"{player3}:{touch3}:{result3}"
                if (
                    result1 == "Error"
                    or result2 == "Error"
                    or result3 == "Error"
                ):
                    row.point = "them"
                    st.session_state.score_them += 1
                elif (
                    result1 == "Kill"
                    or result2 == "Kill"
                    or result3 == "Kill"
                ):
                    row.point = "us"
                    st.session_state.score_us += 1
                st.session_state.events.append(asdict(row))
                st.session_state.df = pd.concat(
                    [st.session_state.df, pd.DataFrame([asdict(row)])],
                    ignore_index=True,
                )
                st.success("Rally recorded")

        with right:
            st.markdown("### Rotation & Subs")
            for i in range(1, 7):
                st.session_state.lineup[f"position_{i}"] = st.number_input(
                    f"Pos {i}",
                    value=int(st.session_state.lineup.get(f"position_{i}", i)),
                    min_value=1,
                    key=f"pos{i}",
                )
            st.markdown("---")
            st.markdown("### Live Event Log")
            st.dataframe(st.session_state.df.tail(10), use_container_width=True)

# ----------------
# Archive & Export
# ----------------
with tabs[3]:
    st.header("Archive & Export")
    st.subheader("Completed Matches")
    for a_idx, match in enumerate(st.session_state.archived_matches):
        st.write(f"{match.get('our_team')} vs {match.get('opponent')} — {match.get('date')}")
        csv = pd.DataFrame(match.get("events", [])).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Match JSON/CSV",
            data=csv,
            file_name=f"{match.get('our_team')}_{match.get('date')}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.subheader("Export Current Match")
    if st.session_state.df.empty:
        st.info("No events recorded yet.")
    else:
        csv = st.session_state.df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Current Match CSV", data=csv, file_name="current_match.csv", mime="text/csv")
