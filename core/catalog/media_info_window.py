import typing

import xbmc
from xbmcgui import ListItem

from .source import ADDON_PATH, initial_state, request_json
from .common_window import CommonWindowXML


class MediaInfoWindow(CommonWindowXML):

    media_id: str
    media_info: typing.Any
    episode_info: typing.Any

    @staticmethod
    def new(media_id: str) -> "MediaInfoWindow":
        return MediaInfoWindow("media_info_window.xml", ADDON_PATH, media_id=media_id)

    def __init__(
        self,
        xmlFilename: str,
        scriptPath: str,
        defaultSkin: str = "Default",
        defaultRes: str = "720p",
        media_id: str = "",
    ) -> None:
        super().__init__(xmlFilename, scriptPath, defaultSkin, defaultRes)
        self.media_id = media_id

    def onInit(self) -> None:
        if self.inited:
            return
        super().onInit()

        # load media info
        # data = open(os.path.join(ADDON_PATH, "test/media_info.html"), "rb").read()
        data = initial_state(
            f"https://www.bilibili.com/bangumi/media/md{self.media_id}"
        )
        self.media_info = data["mediaInfo"]

        # self.episode_info = json.load(open(os.path.join(ADDON_PATH, "test/section.json"), "rb"))["result"]
        self.episode_info = request_json(
            "/pgc/web/season/section", {"season_id": self.media_info["season_id"]}
        )["result"]

        media_info = self.media_info
        list_item = ListItem()
        list_item.setArt({"thumb": media_info["cover"]})
        list_item.setProperties(
            {
                "media_id": str(media_info["media_id"]),
                "release_date_show": media_info["publish"]["release_date_show"],
                "time_length_show": media_info["publish"]["time_length_show"],
                "styles": " ".join([style["name"] for style in media_info["styles"]]),
            }
        )
        tag: xbmc.InfoTagVideo = list_item.getVideoInfoTag()
        tag.setMediaType("movie")
        tag.setTitle(media_info["title"])
        tag.setTagLine(media_info["alias"])
        tag.setOriginalTitle(media_info["origin_name"])
        tag.setPlot(media_info["evaluate"])
        tag.setCountries([area["name"] for area in media_info["areas"]])
        if "rating" in media_info:
            tag.setRating(media_info["rating"]["score"], media_info["rating"]["count"])
        tag.setPremiered(media_info["publish"]["pub_date"])
        # tag.setPlaycount(media_info["stat"]["views"])
        container = self.getContainer(100)
        container.reset()
        container.addItem(list_item)

        # season list
        container = self.getContainer(102)
        container.reset()
        if len(media_info["seasons"]) > 1:
            selected = 0
            for index, season in enumerate(media_info["seasons"]):
                list_item = ListItem(season["season_title"])
                list_item.setProperty("media_id", str(season["media_id"]))
                if str(season["media_id"]) == self.media_id:
                    list_item.select(True)
                    selected = index
                container.addItem(list_item)
            container.selectItem(selected)

        # episode list
        container = self.getContainer(103)
        container.reset()
        data = self.episode_info
        if "main_section" in data:
            episodes = data["main_section"]["episodes"]
            for episode in episodes:
                list_item = ListItem()
                list_item.setLabel2(episode["badge"])
                tag = list_item.getVideoInfoTag()
                tag.setTitle(episode["title"])
                tag.setTvShowTitle(episode["long_title"])
                list_item.setArt({"thumb": episode["cover"]})
                list_item.setProperties(
                    {
                        "avid": episode["aid"],
                        "cid": episode["cid"],
                        "ep_id": episode["id"],
                    }
                )
                container.addItem(list_item)

    def onClick(self, controlId: int) -> None:
        if controlId == 102:
            list_item = self.getContainer(102).getSelectedItem()
            new_media_id = list_item.getProperty("media_id")
            if self.media_id != new_media_id:
                self.media_id = new_media_id
                self.inited = False
                self.onInit()
        elif controlId == 103:
            list_item = self.getContainer(103).getSelectedItem()

            url = "plugin://plugin.video.bilikodiRe/episode/{}/{}/".format(
                list_item.getProperty("ep_id"), list_item.getProperty("cid")
            )
            xbmc.executebuiltin("PlayMedia({})".format(url))

        else:
            super().onClick(controlId)
