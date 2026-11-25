import json
from pathlib import Path


REAL_BULLETINS = json.loads(
    (Path(__file__).parent / "real_bulletins.json").read_text(encoding="utf-8")
)

FORECAST_TITLE = "Forecast for Today Tonight and Tuesday. - Eastern Lake Superior"
WAVES_TITLE = "Waves for Today Tonight and Tuesday. - Eastern Lake Superior"
