# -*- coding: utf-8 -*-
"""
魔法盒子 (l98.cn) —— TVBox / 影视仓 Python 接口源
=================================================
站点本体：http://l98.cn  （「魔法影视」多源聚合实例，原生讲 TVBox 协议）
站点用 api-guard 对 /api/tvbox/* 接口做了签名护盾，本文件已完整复刻签名算法。

接口契约（已实测打通）：
  · 源列表 : GET  /api/tvbox/sources        -> [{key,name,type,api}]
  · 首页   : POST /api/tvbox/home   body={api, filter}
  · 分类   : POST /api/tvbox/category body={api, tid, page, filter, extend}
  · 详情   : POST /api/detail       body={api, ids:[vod_id]}
  · 搜索   : POST /api/search       body={api, keyword, pg}   ← 参数名必须是 keyword！
             （若误传 key/wd/kw，服务端会忽略并返回无关的默认推荐列表）
  · 播放   : vod_play_url 中的 id 形如 /api/tvbox/play/tvbox_ep_<base64>
            正确用法是把该路径整体交给 l98：
              GET {host}/api/tvbox/play/tvbox_ep_xxx  -> 返回标准 m3u8
              m3u8 内分片 /api/tvbox/media/xxx        -> 真实视频流
            故 playerContent 直接返回 {parse:0, url: host+token}。
            （注意：token 解码后的 i 对多数子源是内部 id 而非直链，不能用 i 直连！）

设计：元聚合源。l98.cn 托管了 25 个子源（河马短剧/独播库/歪比影视/爱瓜TV…），
本源把它们全部吃进来：
  - 首页导航：以「子源名 / 分类名」两级呈现，type_id 编码为  key:::真实tid
  - 分类/详情/搜索：自动按 key 路由到对应子源的 /api/tvbox/* 接口
  - 播放：解码 tvbox_ep_ token 拿到真实 mp4/m3u8 直链

可调项：
  - init(extend) 可传逗号分隔的子源 key 列表（如 "tv,source-37dc8f3871"），
    不传则用 DEFAULT_KEYS（已剔除实测 502/空的源）。传 "ALL" 加载全部。
"""

import sys
import json
import time
import base64
import re

try:
    from base.spider import Spider          # 播放器运行时提供；本地无则兜底
except Exception:
    Spider = object


# ====================== 配置 ======================
HOST = "http://l98.cn"

# 默认加载的子源 key（实测可用）
# 注：source-4eb17c91b4 / source-90e25e2716 已废弃（返回"访问新站xxx.com"公告），故剔除。
DEFAULT_KEYS = [
    "tv",                 # 爱瓜TV（电影/剧集，搜索命中好）
    "j4k",                # 4K电影
    "jd4k",               # 4K电影(备)
    "wencai",             # 文才影视（搜索命中好）
    "source-cb4888cc81",  # 剧OK影视
    "source-37dc8f3871",  # 独播库
    "source-8ee56df12f",  # 歪比影视
    "source-0ad659640c",  # 泥巴影视
    "source-e2baa3717e",  # 网易影像
    "source-05849e86e9",  # 飞流视频
    "source-aa4f0ed30b",  # 奇优动漫
    "source-616fbcbf9e",  # 瓜子APP
    "source-c6eef9d264",  # 星芽短剧
    "source-d6c318599c",  # 蛋蛋奇
    "source-d1867dcc71",  # 悟圣短剧
    "source-cd6cd838d1",  # 喜福短剧
    "source-b3e87ad824",  # 西饭短剧
    "hema",               # 河马短剧
    "jumi",               # 剧迷影视
]

# api-guard 签名参数
GUARD_SALT = "mfys-api-guard-v1"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


# ====================== 签名算法（复刻前端 FNV-1a） ======================
def _fnv1a_base36(value):
    h = 2166136261
    t = str(value or "")
    for ch in t:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    n = h & 0xFFFFFFFF
    if n == 0:
        return "0"
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while n > 0:
        s = digits[n % 36] + s
        n //= 36
    return s


def _sign(method, pathname):
    ts = str(int(time.time() * 1000))
    sig = _fnv1a_base36("|".join([GUARD_SALT, str(method).upper(), pathname, ts]))
    return ts, sig


# ====================== Spider ======================
class Spider(Spider):

    def __init__(self):
        super().__init__()
        self.host = HOST
        self.all_sources = {}      # key -> {name, type, api}
        self.selected = []         # 选中的子源 key 列表
        self.home_cache = {}       # key -> {class, list}  （首次拉取后缓存）
        self._extend = ""

    # ---------- 工具：发起受护盾保护的请求 ----------
    def _headers(self, method, path):
        ts, sig = _sign(method, path)
        return {
            "User-Agent": UA,
            "Referer": self.host + "/",
            "X-MF-TS": ts,
            "X-MF-Sign": sig,
            "X-MF-Client": "web",
            "Content-Type": "application/json;charset=UTF-8",
        }

    @staticmethod
    def _parse(resp):
        # 播放器 base.spider 的响应对象通常带 .json() / .text
        if hasattr(resp, "json") and callable(getattr(resp, "json")):
            try:
                d = resp.json()
                if isinstance(d, (dict, list)):
                    return d
                try:
                    return json.loads(d)
                except Exception:
                    pass
            except Exception:
                pass
        text = resp.text if hasattr(resp, "text") else resp
        try:
            return json.loads(text)
        except Exception:
            return {}

    def _post(self, path, body):
        headers = self._headers("POST", path)
        # base.spider 的 post 只认 data=（原始 body），不支持 json= 参数
        payload = json.dumps(body, ensure_ascii=False)
        if hasattr(self, "post") and callable(self.post):
            try:
                r = self.post(self.host + path, data=payload, headers=headers)
                return self._parse(r)
            except Exception as e:
                print("base.post 失败，转本地:", e)
        # 本地兜底（无播放器）
        return self._local_request("POST", path, body, headers)

    def _get(self, path):
        headers = self._headers("GET", path)
        if hasattr(self, "fetch") and callable(self.fetch):
            try:
                r = self.fetch(self.host + path, headers=headers)
                return self._parse(r)
            except Exception as e:
                print("base.fetch 失败，转本地:", e)
        return self._local_request("GET", path, None, headers)

    def _local_request(self, method, path, body, headers):
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.host + path, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))

    # ---------- 子源管理 ----------
    def _load_sources(self):
        if self.all_sources:
            return
        data = []
        for attempt in range(3):                    # 网络抖动重试
            try:
                data = self._get("/api/tvbox/sources").get("data", []) or []
                if data:
                    break
            except Exception as e:
                print("拉取源列表失败(第%d次):" % (attempt + 1), e)
            time.sleep(0.6)
        for s in data:
            if isinstance(s, dict) and s.get("key"):
                self.all_sources[s.get("key")] = s

    def _resolve_selected(self):
        if self.selected:
            return
        self._load_sources()
        if self._extend.strip().upper() == "ALL":
            self.selected = list(self.all_sources.keys())
        elif self._extend.strip():
            want = [k.strip() for k in self._extend.split(",") if k.strip()]
            self.selected = [k for k in want if k in self.all_sources]
        else:
            self.selected = [k for k in DEFAULT_KEYS if k in self.all_sources]
        if not self.selected:                       # 兜底：任何可用源
            self.selected = list(self.all_sources.keys()) or ["hema", "tv"]
        print("魔法盒子 选中子源:", self.selected)

    def _api_of(self, key):
        return self.all_sources.get(key, {}).get("api") or ("tvbox-py://" + key)

    def _home_of(self, key):
        """拉取（并缓存）某子源首页 {class, list}"""
        if key in self.home_cache:
            return self.home_cache[key]
        try:
            d = self._post("/api/tvbox/home", {"api": self._api_of(key), "filter": True}).get("data", {})
        except Exception as e:
            print("home 失败", key, e)
            d = {}
        self.home_cache[key] = {
            "class": d.get("class", []) or [],
            "list": d.get("list", []) or [],
        }
        return self.home_cache[key]

    # ====================== 必须实现的接口 ======================
    def getName(self):
        return "魔法盒子"

    def init(self, extend=""):
        self._extend = extend or ""
        self._resolve_selected()

    def homeContent(self, filter):
        self._resolve_selected()
        # 并发预拉各子源首页：避免 19 个源串行请求导致首页超时
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                list(ex.map(self._home_of, self.selected))
        except Exception:
            for k in self.selected:
                self._home_of(k)
        classes = []
        for key in self.selected:
            src = self.all_sources.get(key, {})
            name = src.get("name", key)
            # 推荐伪分类（返回该源首页推荐列表）
            classes.append({"type_name": "%s·推荐" % name, "type_id": "%s:::" % key})
            for c in self._home_of(key).get("class", []):
                tid = c.get("type_id")
                tname = c.get("type_name") or c.get("type") or str(tid)
                classes.append({"type_name": "%s/%s" % (name, tname), "type_id": "%s:::%s" % (key, tid)})
        return {"class": classes, "filters": {}, "list": []}

    def homeVideoContent(self):
        """首页推荐：取第一个有内容的子源推荐列表，避免首页空白"""
        self._resolve_selected()
        for key in self.selected:
            lst = self._home_of(key).get("list", [])
            if lst:
                return {"list": [self._tag(key, v) for v in lst]}
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if str(pg).isdigit() else 1
        if ":::" not in tid:
            return {"list": [], "page": pg, "pagecount": 1, "limit": 20, "total": 0}
        key, real_tid = tid.split(":::", 1)
        api = self._api_of(key)
        try:
            if real_tid == "":
                # 推荐：返回该源首页推荐列表
                data = self._home_of(key)
                data = {"list": data.get("list", []), "page": 1, "pagecount": 1, "limit": 20, "total": len(data.get("list", []))}
            else:
                data = self._post("/api/tvbox/category", {
                    "api": api, "tid": real_tid, "page": pg, "filter": bool(filter), "extend": extend or {}
                }).get("data", {})
        except Exception as e:
            print("category 失败", key, real_tid, e)
            data = {}
        raw = data.get("list", []) or []
        video_list = [self._tag(key, v) for v in raw]

        def _num(k, d, default):
            v = d.get(k)
            try:
                return int(v)
            except Exception:
                return default

        return {
            "list": video_list,
            "page": _num("page", data, pg),
            "pagecount": _num("pagecount", data, 999),
            "limit": _num("limit", data, 20),
            "total": _num("total", data, len(video_list)),
        }

    def detailContent(self, ids):
        ids = ids or []
        # 按子源分组
        groups = {}
        for raw_id in ids:
            if ":::" in raw_id:
                key, vid = raw_id.split(":::", 1)
            else:
                key, vid = "", raw_id
            groups.setdefault(key, []).append(vid)
        out = []
        for key, vids in groups.items():
            api = self._api_of(key) if key else (self.selected and self._api_of(self.selected[0]))
            if not api:
                continue
            try:
                d = self._post("/api/detail", {"api": api, "ids": vids}).get("data", {})
            except Exception as e:
                print("detail 失败", key, e)
                continue
            if isinstance(d, dict):
                out.append(d)
            elif isinstance(d, list):
                out.extend(d)
        return {"list": out}

    def searchContent(self, key, quick, pg):
        pg = int(pg) if str(pg).isdigit() else 1
        self._resolve_selected()
        kw = (key or "").strip().lower()

        def _one(skey):
            res = []
            try:
                # 注意：搜索参数名是 keyword（传 key 只会返回无关的默认推荐列表）
                data = self._post("/api/search", {
                    "api": self._api_of(skey), "keyword": key, "pg": pg
                }).get("data", [])
            except Exception as e:
                print("search 失败", skey, e)
                return res
            if not isinstance(data, list):
                return res
            for v in data:
                name = str(v.get("vod_name", ""))
                if not name:
                    continue
                # 过滤与关键词无关的默认列表/站点公告（如"访问新站xxx.com"）
                if kw and kw not in name.lower():
                    continue
                res.append(self._tag(skey, v))
            return res

        out = []
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
                for part in ex.map(_one, self.selected):
                    out.extend(part)
        except Exception:
            for s in self.selected:
                out.extend(_one(s))
        return {"list": out, "pagecount": 1, "page": pg, "limit": 20, "total": len(out)}

    def playerContent(self, flag, id, vipFlags):
        """播放：detailContent 返回的集地址形如 /api/tvbox/play/tvbox_ep_<base64>。

        【关键】不要用解码后 token 里的 i（多数子源是内部 id，不是直链）；
        正确做法是把整个 token 路径交给 l98：
          GET http://l98.cn/api/tvbox/play/tvbox_ep_xxx  -> 返回标准 m3u8
          m3u8 内分片 /api/tvbox/media/xxx              -> 真实视频流
        故直接返回 {parse:0, url: host+token}，由播放器请求即可播。
        """
        h = {"User-Agent": UA, "Referer": self.host + "/"}
        sid = str(id or "")
        if "/api/tvbox/play/" in sid:
            url = sid if sid.startswith("http") else (self.host + sid)
            return {"parse": 0, "url": url, "header": h}
        # 兼容：id 本身就是完整直链
        if sid.startswith("http"):
            return {"parse": 0, "url": sid, "header": h}
        # 兜底：尝试解码 tvbox_ep token 里可能的直链
        m = re.search(r"tvbox_ep_([A-Za-z0-9_\-]+)", sid)
        if m:
            try:
                b64 = m.group(1)
                b64 += "=" * (-len(b64) % 4)
                obj = json.loads(base64.urlsafe_b64decode(b64).decode("utf-8", "ignore"))
                real = obj.get("i") or obj.get("url") or ""
                if str(real).startswith("http"):
                    return {"parse": 0, "url": real, "header": h}
            except Exception as e:
                print("解码播放 token 失败:", e)
        return {"parse": 1, "url": sid, "header": h}

    def localProxy(self, param):
        return None

    # ---------- 给列表项打上子源标记，便于详情回查 ----------
    def _tag(self, key, v):
        if isinstance(v, dict) and v.get("vod_id"):
            v = dict(v)
            v["vod_id"] = "%s:::%s" % (key, v["vod_id"])
        return v


# ====================== 本地自测 ======================
if __name__ == "__main__":
    print("===== 魔法盒子 l98.cn 自测 =====")
    sp = Spider()
    sp.init("")  # 默认子源

    # 1) 签名自检
    ts, sig = _sign("POST", "/api/tvbox/home")
    print("[签名] ts=%s sig=%s (长度%s)" % (ts, sig, len(sig)))

    # 2) 源列表
    srcs = sp._get("/api/tvbox/sources").get("data", [])
    print("[源列表] 共 %d 个，默认选中 %d 个" % (len(srcs), len(sp.selected)))

    # 3) 首页导航
    home = sp.homeContent(False)
    print("[首页] 导航分类数: %d，示例:" % len(home.get("class", [])))
    for c in home.get("class", [])[:5]:
        print("     ", c.get("type_id"), "->", c.get("type_name"))

    # 4) 取第一个有内容的分类，测试分类
    cat = None
    for c in home.get("class", []):
        tid = c.get("type_id")
        res = sp.categoryContent(tid, 1, False, {})
        if res.get("list"):
            cat = (tid, c.get("type_name"), res)
            break
    if cat:
        print("[分类] %s 命中 %d 条，首条: %s"
              % (cat[1], len(cat[2]["list"]), cat[2]["list"][0].get("vod_name")))
        # 5) 详情
        vid = cat[2]["list"][0].get("vod_id")
        det = sp.detailContent([vid]).get("list", [])
        if det:
            d0 = det[0]
            pu = str(d0.get("vod_play_url", ""))
            print("[详情] %s 线路=%s 首集id=%s"
                  % (d0.get("vod_name"), d0.get("vod_play_from"), pu.split("#")[0].split("$")[-1][:50]))
            # 6) 播放
            pid = pu.split("#")[0].split("$")[-1]
            pc = sp.playerContent("", pid, "")
            print("[播放] parse=%s url=%s" % (pc.get("parse"), pc.get("url", "")[:60]))
    else:
        print("[分类] 未取到任何列表（子源可能临时 502）")

    # 7) 搜索
    sres = sp.searchContent("流浪地球", False, 1)
    print("[搜索] 命中 %d 条" % len(sres.get("list", [])))
    print("===== 自测结束 =====")
