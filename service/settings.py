# import confuse
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path.name)

# Load Default configuration yaml file
# yaml_path = Path(__file__).resolve().parent.parent / "config" / "default.yaml"
# config = confuse.Configuration("SimpleSuperHeroService", __name__)
# config.set_file(str(yaml_path))
# print("config = ", config)
