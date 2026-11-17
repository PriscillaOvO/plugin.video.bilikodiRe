import json
import os
import re

from xbmcaddon import Addon

from core import core, secret

ADDON_PATH = Addon().getAddonInfo("path")


def load_config(filename):
    with open(os.path.join(ADDON_PATH, "resources", "data", filename), encoding="utf-8") as config:
        return json.load(config)


def request_json(path, params):
    response = core.http.get("https://api.bilibili.com" + path, params=params,
                             headers=core.heads, cookies=secret.get_cooks(), timeout=10)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise ValueError(payload.get("message") or "影视请求失败")
    return payload


def initial_state(url):
    response = core.http.get(url, headers=core.heads, cookies=secret.get_cooks(), timeout=10)
    response.raise_for_status()
    marker = re.search(r"window\.__INITIAL_STATE__\s*=\s*", response.text)
    if marker is None:
        raise ValueError("哔哩哔哩未返回影视目录")
    return json.JSONDecoder().raw_decode(response.text, marker.end())[0]
