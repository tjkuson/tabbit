"""Template rendering configuration for views."""

from pathlib import Path
from typing import Final

from fastapi.templating import Jinja2Templates

_TEMPLATES_DIR: Final = Path(__file__).parent / "templates"

templates: Final = Jinja2Templates(directory=_TEMPLATES_DIR)
