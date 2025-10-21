from reactpy import component, html, use_state

@component
def LineupForm(lineup, on_lineup_change, rotation, on_rotation_change):
    def handle_position_change(position, value):
        new_lineup = dict(lineup)
        new_lineup[f"position_{position}"] = int(value)
        on_lineup_change(new_lineup)

    return html.div(
        {"class_name": "lineup-form"},
        html.h3("Starting Lineup"),
        [
            html.div(
                {"class_name": "position-input", "key": i},
                html.label(f"Position {i}"),
                html.input({
                    "type": "number",
                    "min": 1,
                    "value": lineup[f"position_{i}"],
                    "on_change": lambda event, pos=i: handle_position_change(pos, event["target"]["value"])
                })
            )
            for i in range(1, 7)
        ],
        html.div(
            {"class_name": "rotation-control"},
            html.label("Current Rotation"),
            html.input({
                "type": "number",
                "min": 1,
                "max": 6,
                "value": rotation,
                "on_change": lambda event: on_rotation_change(int(event["target"]["value"]))
            })
        )
    )