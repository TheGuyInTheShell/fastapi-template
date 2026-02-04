"""
CLI module generator for creating FastAPI plugin structures.
"""
import os
from pathlib import Path


def create_plugin_init_template(name: str) -> str:
    """Generate __init__.py template for plugins"""
    class_name = "".join(word.capitalize() for word in name.replace("_", " ").split()) + "Plugin"
    return f'''from core.plugins.types.plugin import Plugin
from fastapi import FastAPI
from .settings import settings, Settings

class {class_name}(Plugin):
    """
    {name.capitalize()} Plugin implementation.
    """

    async def initialize(self, app: FastAPI, config: Settings = settings):
        """
        Logic to run when the plugin is loaded during application startup.
        """
        try:
            print(f"[{class_name}] Initializing...")
            # Your initialization logic here
            
        except Exception as e:
            print(f"[{class_name}] Error initializing: {{e}}")
        
    async def terminate(self, app: FastAPI):
        """
        Logic to run when the application is shutting down.
        """
        try:
            print(f"[{class_name}] Terminating...")
            # Your cleanup logic here
            
        except Exception as e:
            print(f"[{class_name}] Error during termination: {{e}}")
'''


def create_plugin_settings_template(name: str) -> str:
    """Generate settings.py template for plugins"""
    return f'''import os
from dotenv import load_dotenv

# Load local .env file if it exists
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Settings:
    """
    Settings for the {name.capitalize()} plugin.
    Values are loaded from environment variables.
    """
    api_key: str = ""
    enabled: bool = True

    def __init__(self):
        self.api_key = os.getenv("{name.upper()}_API_KEY", "")
        self.enabled = os.getenv("{name.upper()}_ENABLED", "true").lower() == "true"


settings = Settings()
'''


def generate_plugin(name: str):
    """
    Generate a complete plugin structure.
    """
    # Get the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    base_path = project_root / "plugins" / name

    # Create directory structure
    base_path.mkdir(parents=True, exist_ok=True)
    print(f"[+] Created directory: {base_path}")

    # Create files
    files = {
        '__init__.py': create_plugin_init_template(name),
        'settings.py': create_plugin_settings_template(name),
        '.env.example': f"{name.upper()}_API_KEY=your_key_here\n{name.upper()}_ENABLED=true\n",
    }

    for filename, content in files.items():
        file_path = base_path / filename
        if file_path.exists():
            print(f"[SKIP] Already exists: {file_path.relative_to(project_root)}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {file_path.relative_to(project_root)}")

    print(f"\n[SUCCESS] Plugin '{name}' generated successfully!")
    print(f"[INFO] Location: {base_path}")
    print(f"\n[HINT] Next steps:")
    print(f"   1. Review plugins/{name}/__init__.py")
    print(f"   2. The plugin will be automatically loaded if registered in core/plugins/manager.py or similar mechanism")
