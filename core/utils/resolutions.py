import os

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_extensions_app_path(deep_path: tuple[str, ...]):
    """Get the path to the app directory of the extension. app/ext/<deep_path>"""
    return os.path.join(base_path, "app", "ext", *deep_path)