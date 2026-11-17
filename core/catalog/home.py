import re
from urllib.parse import urlsplit

import xbmc
from xbmcgui import Dialog, ListItem, WindowXML

from .source import ADDON_PATH, load_config, request_json
from .media_info_window import MediaInfoWindow
from .video_index_window import VideoIndexWindow


class CatalogWindow(WindowXML):
    def onInit(self):
        for category in load_config("season_type.json"):
            self.getControl(100 + category["st"]).setLabel(category["name"])

    def onClick(self, control_id):
        try:
            if control_id == 99:
                self.search()
            elif 100 < control_id < 110:
                VideoIndexWindow.new(control_id - 100).doModal()
        except (KeyError, ValueError, OSError) as error:
            Dialog().ok("哔哩哔哩", str(error))

    def search(self):
        from addon import search

        dialog = Dialog()
        keyword = dialog.input("搜索哔哩哔哩").strip()
        if not keyword:
            return

        matches = []
        rows = []
        for item in search(keyword, "all", 1) or []:
            if not item:
                continue
            path = urlsplit(item.get("path", "")).path
            if not path.startswith(("/season/", "/bvplay/")):
                continue
            label = re.sub(r"</?em(?:\s[^>]*)?>", "", item["label"])
            row = ListItem(label)
            if item.get("icon"):
                row.setArt({"thumb": item["icon"]})
            rows.append(row)
            matches.append(item["path"])

        if not rows:
            dialog.ok("哔哩哔哩", "没有找到电影、番剧或视频")
            return

        selected = dialog.select("搜索结果", rows, useDetails=True)
        if selected < 0:
            return
        url = matches[selected]
        path = urlsplit(url).path.strip("/").split("/")
        if path[0] == "season":
            season = request_json("/pgc/view/web/season", {"season_id": path[1]})["result"]
            MediaInfoWindow.new(str(season["media_id"])).doModal()
        else:
            xbmc.executebuiltin("PlayMedia({})".format(url))
