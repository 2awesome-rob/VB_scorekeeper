import pandas as pd
from dataclasses import asdict

from VolleyStatApp.volleyStat import Rally


def test_rallyrow_asdict_and_fields():
    row = Rally(
        position_1=1,
        position_2=2,
        position_3=3,
        position_4=4,
        position_5=5,
        position_6=6,
        rotation=1,
        touch_serve="1:Ace",
    )
    d = asdict(row)
    assert d["position_1"] == 1
    assert d["touch_serve"] == "1:Ace"
    assert "touch_1" in d


def test_add_row_to_dataframe_and_undo(tmp_path):
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
    df = pd.DataFrame(columns=cols)
    row = Rally(
        position_1=10,
        position_2=11,
        position_3=12,
        position_4=13,
        position_5=14,
        position_6=15,
        rotation=2,
        touch_1="10:Pass:OK",
        touch_2="11:Set:OK",
        touch_3="12:Attack:Kill",
    )
    d = asdict(row)
    df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
    assert len(df) == 1
    # simulate undo
    df = df.iloc[:-1]
    assert df.empty
