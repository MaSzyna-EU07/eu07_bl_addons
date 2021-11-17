import eu07_tools

from common import preferences

def get_root(abspath=""):
    try:
        root = eu07_tools.utils.find_asset_root(abspath)
    except ValueError:
        root = preferences.get_preferences().root
        if not root:
            raise ValueError(f"Can't find root path for {abspath}")

    return root


def uilist_safe_index_after_delete(uilist, index):
    return min(max(0, index - 1), len(uilist) - 1)


