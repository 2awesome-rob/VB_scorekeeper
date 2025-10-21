from reactpy import component, html, use_state

@component
def Scoreboard(score_us, score_them, game_id, set_number):
    return html.div(
        {"class_name": "scoreboard"},
        html.h2(f"Game: {game_id} - Set {set_number}"),
        html.div(
            {"class_name": "score-display"},
            html.div(
                {"class_name": "team-score"},
                html.h3("Us"),
                html.h1(score_us)
            ),
            html.div(
                {"class_name": "team-score"},
                html.h3("Them"),
                html.h1(score_them)
            )
        )
    )