from flask import Blueprint
from reactpy import component, html, use_state
from app.components.scoreboard import Scoreboard
from app.components.lineup import LineupForm
from app.components.game_controls import GameControls

bp = Blueprint("main", __name__)

@component
def App():
    # State management
    game_id, set_game_id = use_state("")
    set_number, set_set_number = use_state(1)
    score_us, set_score_us = use_state(0)
    score_them, set_score_them = use_state(0)
    rotation, set_rotation = use_state(1)
    lineup, set_lineup = use_state({f"position_{i}": i for i in range(1, 7)})

    return html.div(
        {"class_name": "container"},
        LineupForm(
            lineup=lineup,
            on_lineup_change=set_lineup,
            rotation=rotation,
            on_rotation_change=set_rotation
        ),
        Scoreboard(
            score_us=score_us,
            score_them=score_them,
            game_id=game_id,
            set_number=set_number
        ),
        GameControls(
            on_point_us=lambda: set_score_us(score_us + 1),
            on_point_them=lambda: set_score_them(score_them + 1),
            on_rotate=lambda: set_rotation((rotation % 6) + 1)
        )
    )

def register_routes(app):
    app.register_blueprint(bp)