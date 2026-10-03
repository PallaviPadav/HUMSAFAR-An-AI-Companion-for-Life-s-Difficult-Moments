from pathlib import Path
import os
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]: %(message)s")


list_files = [
    "app.py",
    "config.py",
    "agents/LG.py",
    "requirements.txt",
    "graph/state.py",
    "models/user.py",
    "tools/activity_tools.py",
    "services/conversation_service.py",
    "frontend/templates/base.html",
    "frontend/templates/home.html",
    "frontend/templates/chat.html",
    "frontend/static/css/",
    "frontend/static/js/",
    "frontend/static/images/",
    "tests/test_agents.py",
]

for filepath in list_files:
    path = Path(filepath)
    dir, file = os.path.split(path)

    if dir != "":
        os.makedirs(dir, exist_ok=True)

        if file != "":
            with open(path, "w+") as filename:
                pass
        logging.info(f"Created folder : {dir}, file: {file}")

    elif file != "":
        with open(file, "w+") as filename:
            pass
        logging.info(f"Created file :{file}")
