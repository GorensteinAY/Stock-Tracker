"""XDG Base Directory Specification helpers."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_xdg.ipynb.

# %% auto 0
__all__ = ['xdg_cache_home', 'xdg_config_dirs', 'xdg_config_home', 'xdg_data_dirs', 'xdg_data_home', 'xdg_runtime_dir',
           'xdg_state_home']

# %% ../nbs/09_xdg.ipynb
from .utils import *

# %% ../nbs/09_xdg.ipynb
def _path_from_env(variable, default):
    value = os.environ.get(variable)
    if value and os.path.isabs(value): return Path(value)
    return default

# %% ../nbs/09_xdg.ipynb
def _paths_from_env(variable, default):
    value = os.environ.get(variable)
    if value:
        paths = [Path(o) for o in value.split(":") if os.path.isabs(o)]
        if paths: return paths
    return default

# %% ../nbs/09_xdg.ipynb
def xdg_cache_home():
    "Path corresponding to `XDG_CACHE_HOME`"
    return _path_from_env("XDG_CACHE_HOME", Path.home()/".cache")

# %% ../nbs/09_xdg.ipynb
def xdg_config_dirs():
    "Paths corresponding to `XDG_CONFIG_DIRS`"
    return _paths_from_env("XDG_CONFIG_DIRS", [Path("/etc/xdg")])

# %% ../nbs/09_xdg.ipynb
def xdg_config_home():
    "Path corresponding to `XDG_CONFIG_HOME`"
    return _path_from_env("XDG_CONFIG_HOME", Path.home()/".config")

# %% ../nbs/09_xdg.ipynb
def xdg_data_dirs():
    "Paths corresponding to XDG_DATA_DIRS`"
    return _paths_from_env( "XDG_DATA_DIRS", [Path(o) for o in "/usr/local/share/:/usr/share/".split(":")])

# %% ../nbs/09_xdg.ipynb
def xdg_data_home():
    "Path corresponding to `XDG_DATA_HOME`"
    return _path_from_env("XDG_DATA_HOME", Path.home()/".local"/"share")

# %% ../nbs/09_xdg.ipynb
def xdg_runtime_dir():
    "Path corresponding to `XDG_RUNTIME_DIR`"
    value = os.getenv("XDG_RUNTIME_DIR")
    return Path(value) if value and os.path.isabs(value) else None

# %% ../nbs/09_xdg.ipynb
def xdg_state_home():
    "Path corresponding to `XDG_STATE_HOME`"
    return _path_from_env("XDG_STATE_HOME", Path.home()/".local"/"state")
