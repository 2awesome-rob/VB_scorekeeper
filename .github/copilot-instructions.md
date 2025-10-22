# AI Agent Instructions for VB_scorekeeper

  ## Project Overview
  This is a web application for tracking volleyball player statistics in real-time.
  To support this, it must minimize user input requirements while maximizing data accuracy and completeness. The app must be game aware, understanding volleyball rules and player rotations to support prompting the user for necessary inputs only. The game log files must be structured and exportable to support post-game analysis. The app will be run on tablets or phones during games and screen layout must be optimized for quick access and minimal navigation and intuitive game flow.

  ## Core Architecture
  -- **User Interface**: Use Streamlit or ReactPy for the web interface and organize the app into four primary tabs (mobile/tablet-first layout). The tabs should map to the app workflows and provide single-tap access to common actions. See `/.archive/vb.swift` for a reference layout and interaction patterns.
    The four tabs and their responsibilities:
     1. Team Management
       - Create/edit teams and seasons.
       - Add, edit, and remove players (name, jersey number, primary position).
       - Roster view with quick keypad for jersey numbers and drag/reorder or compact list for mobile.
       - Persist team data locally and provide import/export of team rosters (JSON/CSV).
     2. Scheduling
       - Create and manage upcoming matches (our team, opponent, date/time, set format, points-to-win).
       - Quick list of upcoming matches with date, set format, and venue.
       - Ability to select a match and tap "Start Match" to open the Game Tracking tab pre-populated with teams/lineup.
     3. Game Tracking (live match)
       - Split into compact sub-sections for quick access: Scoreboard & Controls, Serve Entry, Rally Entry, Rotation/Subs, Live Event Log.
       - Scoreboard & Controls: big, high-contrast score numbers, large Point Us / Point Them buttons, current rotation indicator, and a single "Next Rally" action.
       - Serve Entry: recognize server (position/jersey) from game state, select serve result (Ace / Error / Return) with one-tap buttons.
       - Rally Entry: streamlined 1-2-3 touch input with quick pickers for player and result; block handling with quick blocker selection and block result options.
       - Rotation & Substitutions: compact rotational diagram and one-tap substitutions; auto-apply rotation on side-out when appropriate.
       - Live Event Log: append each rally as a structured row; allow quick undo and edit of last event.
       - Minimize typing during play: favor buttons, pickers, and presets; confirm critical actions with lightweight modals only when ambiguous.
     4. Archive & Data Export
       - List completed matches with summary (scoreline, date, opponent).
       - Export match logs in JSON (primary) and CSV (optional) for post-game analysis.
       - Bulk archive and delete controls; per-match download and share actions.
  - **Game Logic**: Implement volleyball rules for scoring, rotations, and substitutions. Maintain awareness of game state to provide contextual prompts and automate data entry. See `/.archive/streamlit_app.py` for reference logic design.
  - **Data Model**: Uses Pandas Sparse DataFrame with a MultiIndex structure (see `/.archive/streamlit_app.py` for reference data model design):
    index levels:
      - Match ID (format: `<TEAM>-YY-MM-DD-<GAME>-<SET>`) where `<TEAM>` is the team abbreviation code, `YY-MM-DD` is the date, `<GAME>` is the match number of the day, and `<SET>` is the set number of the match.
      - Current scores (us/them): (int, int) — volleyball uses scores vs time to track game progress.
      - Rally step (int): tracks the progression of a rally. 0 = serve, 1 = serve receive, 2+ = subsequent possessions.
    For each row, columns include:
      - Player positions (1-6) mapped to jersey numbers
      - Current rotation (1-6)
      - Touch sequences (serve, block, 3 touches)
        - Serve (player, result)
        - Block (player, result)
        - Touch 1 to 3 (player, result)
      - Sanctions (e.g., yellow/red cards)

  ## Key Workflows

  ### Development Setup
  1. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

  2. Run the application:
  ```bash
  streamlit run VolleyStatApp/volleyStat.py
  ```

  ### State Management
  - Key state variables:
    - `score_us`, `score_them`: Current game scores
    - `rotation`: Current player rotation (1-6)
    - `rally_step`: Tracks serve/return sequence
    - `lineup`: Dictionary mapping positions to player jersey numbers

  ### Data Structure Patterns
  - Each game event is stored as a row in the DataFrame with:
    - Player positions and jersey numbers
    - Touch sequences (serve, block, 3 touches)
    - Sanctions
  - Example DataFrame schema:
  ```python
  {
      "position_1": int,  # Jersey numbers for each position
      "position_2": int,
      ...
      "rotation": int,
      "touch_serve": Optional[str],
      "touch_block": Optional[str],
      "touch_block_asst": Optional[str],
      "touch_1": Optional[str],
      "touch_2": Optional[str],
      "touch_3": Optional[str],
      "sanctions": Optional[str]
  }
  ```

  ## Common Operations
  - Use `reset_rally_results()` to clear per-rally state
  - Call `add_new_row()` to record a new game event
  - Point scoring functions (`point_us()`, `point_them()`) handle rotation changes automatically

  ## UI Schematics

  - Theme and touch targets
    - Darkmode-first theme: black or very dark background, white/high-contrast text, pink as the primary accent color for interactive controls.
    - Use large touch targets (minimum 44–48px) for primary actions (point buttons, serve/rally results).
    - Compact, high-density controls for lineup and scheduling screens; large, spaced controls for Game Tracking.

  - Layout and navigation
    - Four top-level tabs (Team Management, Scheduling, Game Tracking, Archive). Tabs should be visible at the bottom or top depending on platform conventions; keep them always one-tap away.
    - In the Game Tracking tab, split UI vertically or with collapsible sections so the most-used controls are immediately visible (Scoreboard + Quick Serve + Rally). Secondary controls (substitutions, settings) should be in a collapsible panel or a slide-over.

  - Game Tracking details (important for developers)
    - Data entry model: each rally is a row in the DataFrame (see Data Model section). Rows must include lineup snapshot, rotation, touch sequence (serve, block, touch1-3), and sanctions.
    - State machine: implement clear rally_step states (0 = serve, 1 = serve-receive, 2+ = in-rally) and a small finite-state machine that drives which UI elements are active.
    - Auto-rotation: when side-out occurs, update rotation automatically and show an animation/brief highlight of the new server.
    - Undo/confirm: allow undo of the last entry; major corrections should open a small editor for that rally row.

  - Accessibility & mobile constraints
    - Use high-contrast text and consider a dyslexia-friendly font option.
    - Support landscape mode for tablets; the Game Tracking tab should scale to a 2-column layout on wider screens (left: controls, right: live log) and collapse to a single column on phones.
    - Minimize keyboard use; prefer pickers and buttons. Provide optional number keypad for quick jersey entry when editing lineups.

  - Visual affordances and feedback
    - Provide subtle haptic or visual feedback on critical taps (point award, rotation change, substitution).
    - Use color-coded badges for event results (green for point-us, red for error, yellow for block).

  These UI details are the canonical front-end guidance for implementing the four-tab interface referenced in `/.archive/vb.swift`. Keep the Game Tracking tab focused on minimizing taps during live play and ensuring correctness of recorded events.

  ## Integration Points
  - Streamlit for web interface
  - Pandas for data management and statistics