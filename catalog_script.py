import xbmc
import xbmcgui
from xbmcaddon import Addon

from core.catalog.home import CatalogWindow


if __name__ == "__main__":
    monitor = xbmc.Monitor()
    home = xbmcgui.Window(10000)
    active = "BilikodiRe.CatalogActive"
    if home.getProperty(active):
        raise SystemExit
    home.setProperty(active, "true")
    try:
        for attempt in range(40):
            if not xbmc.getCondVisibility("Window.IsActive(busydialognocancel) | Window.IsActive(busydialog)"):
                break
            if monitor.waitForAbort(0.1):
                raise SystemExit

        addon = Addon("plugin.video.bilikodiRe")
        window = CatalogWindow("home_window.xml", addon.getAddonInfo("path"))
        window.doModal()
    finally:
        home.clearProperty(active)
