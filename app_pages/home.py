from src.auth import current_user
from src.home_ui import render_home


render_home(current_user())
