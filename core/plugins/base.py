import os
import importlib
import inspect
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .types.plugin import Plugin

class PluginManager:
    def __init__(self):
        self.plugins: List[Plugin] = []
        self._load_plugins()

    def _load_plugins(self):
        """
        Dynamically load plugins from the 'plugins' directory.
        Criteria:
        - Must be a directory in the first level of 'plugins/'.
        - Must contain an '__init__.py' file.
        """
        plugins_dir = "plugins"
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir, exist_ok=True)
            return

        for item in os.listdir(plugins_dir):
            item_path = os.path.join(plugins_dir, item)
            
            # Use only first level directories that have __init__.py
            if os.path.isdir(item_path):
                init_file = os.path.join(item_path, "__init__.py")
                if os.path.exists(init_file):
                    try:
                        # Import the module
                        module_name = f"plugins.{item}"
                        module = importlib.import_module(module_name)
                        
                        # Find Plugin subclasses defined in the module
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, Plugin) and 
                                obj is not Plugin):
                                self.plugins.append(obj())
                                print(f"[PluginManager] Loaded plugin: {item}")
                                break # Load only one plugin per module for now to avoid duplicates if re-imported
                    except Exception as e:
                        print(f"[PluginManager] Error loading plugin '{item}': {e}")

    @asynccontextmanager
    async def manage_lifespan(self, app: FastAPI):
        """
        FastAPI lifespan manager to initialize and terminate plugins.
        """
        # Startup
        for plugin in self.plugins:
            try:
                await plugin.initialize(app)
            except Exception as e:
                print(f"[PluginManager] Error initializing plugin '{plugin.__class__.__name__}': {e}")
        
        yield
        
        # Shutdown
        for plugin in self.plugins:
            try:
                await plugin.terminate(app)
            except Exception as e:
                print(f"[PluginManager] Error terminating plugin '{plugin.__class__.__name__}': {e}")

# Singleton Instance
plugin_manager = PluginManager()