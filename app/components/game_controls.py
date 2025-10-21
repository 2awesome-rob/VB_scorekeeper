from reactpy import component, html

@component
def GameControls(on_point_us, on_point_them, on_rotate):
    return html.div(
        {"class_name": "game-controls"},
        html.button(
            {
                "class_name": "point-btn point-us",
                "on_click": lambda event: on_point_us()
            },
            "Point for Us"
        ),
        html.button(
            {
                "class_name": "point-btn point-them",
                "on_click": lambda event: on_point_them()
            },
            "Point for Them"
        ),
        html.button(
            {
                "class_name": "rotate-btn",
                "on_click": lambda event: on_rotate()
            },
            "Rotate"
        )
    )