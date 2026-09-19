# -*- coding: utf-8 -*-
"""
可可影视 (kkys01.com) TVBox / 影视仓 Python 接口源
==================================================
由 CatVod T4(JS) 源「可可影视.js」(opencode, 2026-07-08) 移植而来。

站点特征：
  - 服务端渲染的非标 MacCMS（自定义模板），纯 HTML 解析。
  - cdndefend 防护盾：首次请求返回 HTTP 850 + 一段 SHA1 PoW 挑战页，
    算出 cdndefend_js_cookie 后带上即可放行。本源用 hashlib 复现该 PoW。
      挑战算法：seed = 页面里的 40 位 HEX 种子；n1 = int(seed[0],16)
        枚举 i=0,1,2... 直到 sha1(seed+i)[n1]==0xb0 且 [n1+1]==0x0b
        cookie 值 = seed + i
  - 分类：/show/{tid}-{类型}-{地区}-{语言}-{年份}-{排序}-{页}.html
  - 详情：/detail/{id}.html（线路 .source-item-label，集数 .episode-list/.episode-item）
  - 播放：/play/{id}-{sid}-{eid}.html  页面里 const playSource = { src: "https://...m3u8" } 明文直链
  - 搜索：/search?k={词}&t={token}（token 轮换，运行时从首页刷新）
  - 封面独立 CDN：主站 /vod1/... 有防盗链，须走 vres.zyxpedu.com

铁律落实：header 一律 dict；禁用 self.post(json=)；播放地址存相对路径、
playerContent 用 _fix_url 拼 Host（无双重 host）；三层分隔符 $$$ / # / $ 正确。
"""

import re
import json
import hashlib
import html as html_parser
from urllib.parse import quote, unquote

try:
    from base.spider import Spider
except Exception:
    # 独立调试时可缺省 base.spider，仅用于语法检查
    class Spider:
        def fetch(self, *a, **k):
            raise NotImplementedError("base.spider required in TVBox runtime")

# ---- 站点常量 ----
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
IMG_HOST = "https://vres.zyxpedu.com"
SEARCH_TOKEN_DEFAULT = "qRFNl5N8XwhSO0I8cY/+ww=="   # 运行时从首页刷新

CLASSES = [
    {"type_id": "1", "type_name": "电影"},
    {"type_id": "2", "type_name": "连续剧"},
    {"type_id": "3", "type_name": "动漫"},
    {"type_id": "4", "type_name": "综艺纪录"},
    {"type_id": "6", "type_name": "短剧"},
]
FILTER_CLASS = ["剧情", "喜剧", "动作", "爱情", "恐怖", "惊悚", "犯罪", "科幻",
                "悬疑", "奇幻", "冒险", "战争", "历史", "古装", "家庭", "传记",
                "武侠", "动画", "儿童", "职场"]
FILTER_AREA = ["中国大陆", "中国香港", "中国台湾", "美国", "日本", "韩国", "英国",
               "法国", "德国", "印度", "泰国", "丹麦", "瑞典", "巴西", "加拿大",
               "俄罗斯", "意大利", "西班牙", "澳大利亚", "其他"]
FILTER_LANG = ["国语", "粤语", "英语", "日语", "韩语", "法语", "其他"]
FILTER_YEAR = ["2026", "2025", "2024", "2023", "2022", "2021", "2020",
               "2010_2019", "2000_2009", "1990_1999", "1980_1989", "0_1979"]


class Spider(Spider):
    Host = "https://www.kkys01.com"

    # ---------------- 初始化 ----------------

    def init(self, extend=""):
        if isinstance(extend, str) and re.match(r"^https?://", extend.strip()):
            self.Host = extend.strip().rstrip("/")
        self.cdn_cookie = ""          # 过盾 cookie 值（运行时算出）
        self.search_token = SEARCH_TOKEN_DEFAULT
        self.FILTERS = self._build_filters()
        self.headers = {
            "User-Agent": UA,
            "Referer": self.Host + "/",
            "Accept": "text/html,application/xhtml+xml,*/*",
        }
        # 预热：过一次盾，把 cdndefend cookie 算出来
        try:
            self._get_html(self.Host + "/")
        except Exception:
            pass

    def getName(self):
        return "可可影视"

    # ---------------- 接口实现 ----------------

    def homeContent(self, filter):
        return {"class": CLASSES, "filters": self.FILTERS}

    def homeVideoContent(self):
        html = self._get_html(self.Host + "/")
        return {"list": self._parse_list(html)[:40]}

    def categoryContent(self, tid, pg, filter, extend):
        tid = str(tid or "1")
        try:
            pg = int(pg)
        except Exception:
            pg = 1
        if pg < 1:
            pg = 1
        extend = self._parse_extend(extend)
        url = self._show_url(tid, pg, extend)
        html = self._get_html(url)
        videos = self._parse_list(html)
        # 每页满 18 视为有下一页
        pagecount = pg + 1 if len(videos) >= 18 else pg
        return {
            "page": pg,
            "pagecount": pagecount,
            "limit": len(videos) or 18,
            "total": pagecount * 18,
            "list": videos,
        }

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, list) else ids
        vid = re.sub(r"\D", "", str(vid).split(",")[0])
        html = self._get_html(self.Host + "/detail/" + vid + ".html")
        if not html:
            return {"list": []}

        # 标题
        hm = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", html)
        name = self._text_clean(hm.group(1)) if hm else ""
        name = re.sub(r"𝕜𝕜𝕪𝕤𝟘𝟙\.𝕔𝕠𝕞", "", name)
        name = re.sub(r"可可影视[^ ]*", "", name).strip()
        if not name:
            tm = re.search(r"<title>([^<]+?)-", html)
            if tm:
                name = tm.group(1).strip()

        # 封面
        pm = (re.search(r'class="detail-pic"[\s\S]*?data-original="([^"]+)"', html)
              or re.search(r'<img[^>]+class="[^"]*cover[^"]*"[^>]+data-original="([^"]+)"', html))
        pic = pm.group(1) if pm else ""

        # 简介
        dm = re.search(r'class="[^"]*(?:detail-desc|content-desc|desc-text|vod-content)[^"]*"[^>]*>([\s\S]*?)</div>', html)
        desc = self._text_clean(dm.group(1)) if dm else ""

        vod = {
            "vod_id": vid,
            "vod_name": name,
            "vod_pic": self._fix_pic(pic),
            "vod_content": desc,
        }

        # 线路名（按顺序）
        froms = [self._text_clean(fm.group(1))
                 for fm in re.finditer(r'source-item-label">([^<]+)<', html)]

        # 集数分组：每个 <div class="episode-list"> 对应一条线路（顺序一致）
        play_from, play_url = [], []
        idx = 0
        for lgm in re.finditer(r'<div class="episode-list"[^>]*>([\s\S]*?)</div>', html):
            block = lgm.group(1)
            eps = []
            for em in re.finditer(r'<a\s+href="(/play/[^"]+\.html)"[^>]*>([\s\S]*?)</a>', block):
                ep_url = em.group(1)
                ep_name = self._text_clean(em.group(2)) or (len(eps) + 1)
                eps.append(str(ep_name) + "$" + ep_url)
            if eps:
                from_name = froms[idx] if idx < len(froms) else ("线路" + str(idx + 1))
                play_from.append(from_name)
                play_url.append("#".join(eps))
            idx += 1

        if play_from:
            vod["vod_play_from"] = "$$$".join(play_from)
            vod["vod_play_url"] = "$$$".join(play_url)
        else:
            vod["vod_play_from"] = "提示"
            vod["vod_play_url"] = "暂无播放源$"
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        page_url = self._fix_url(id)
        html = self._get_html(page_url)

        # 部分线路（如"超清1"）的 playSource 用 \uXXXX 转义混淆，先整体解码
        decoded = re.sub(r"\\u([0-9a-fA-F]{4})",
                         lambda m: chr(int(m.group(1), 16)), html)

        url = ""
        m = re.search(r'playSource\s*=\s*\{[\s\S]{0,200}?[\'"]?src[\'"]?\s*:\s*"([^"]*)"', decoded)
        if m:
            url = m.group(1)
        if not url:
            m2 = re.search(r'"?url"?\s*[:=]\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"', decoded, re.I)
            if m2:
                url = m2.group(1)
        if not url:
            m3 = re.search(r"https?://[^\"'\s\\]+?\.m3u8[^\"'\s\\]*", decoded)
            if m3:
                url = m3.group(0)
        url = url.replace(r"\/", "/").strip()

        if url and re.match(r"^https?://", url):
            return {"parse": 0, "url": url,
                    "header": {"User-Agent": UA, "Referer": self.Host + "/"}}
        # src 为空的线路（如"4K"）为 APP 独占，网页端不下发地址
        return {"parse": 0, "url": "", "header": {},
                "msg": "该线路为APP专属，暂无法播放，请换其他线路"}

    def searchContent(self, key, quick, pg):
        try:
            pg = int(pg)
        except Exception:
            pg = 1
        if pg < 1:
            pg = 1
        token = self._get_search_token()
        url = (self.Host + "/search?k=" + quote(key)
               + (f"&page={pg}" if pg > 1 else "") + "&t=" + quote(token))
        html = self._get_html(url)
        videos = self._parse_list(html)
        if not videos and "search-result-info" not in html:
            token2 = self._extract_search_token(html)
            if token2 and token2 != token:
                self.search_token = token2
                url = (self.Host + "/search?k=" + quote(key)
                       + (f"&page={pg}" if pg > 1 else "") + "&t=" + quote(token2))
                html = self._get_html(url)
                videos = self._parse_list(html)
        limit = 18
        pc = self._search_page_count(html, pg, limit)
        return {"list": videos, "page": pg, "pagecount": pc,
                "limit": limit, "total": pc * limit}

    # ---------------- 请求（自动过盾） ----------------

    def _raw_req(self, url, cookie=None):
        """发起一次 GET，返回 (code, body)。优先 base.fetch，失败回退 requests/urllib。"""
        hdr = dict(self.headers)
        if cookie:
            hdr["Cookie"] = "cdndefend_js_cookie=" + cookie
        # 1) base spider fetch
        try:
            r = self.fetch(url, headers=hdr)
            code = getattr(r, "status_code", 200)
            body = self._resp_text(r)
            if body or code:
                return code, body
        except Exception:
            pass
        # 2) requests 回退
        try:
            import requests
            r = requests.get(url, headers=hdr, timeout=15, verify=False)
            return r.status_code, r.text
        except Exception:
            pass
        # 3) urllib 回退
        try:
            import urllib.request, ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers=hdr)
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            return resp.getcode(), resp.read().decode("utf-8", "ignore")
        except Exception:
            pass
        return 0, ""

    @staticmethod
    def _resp_text(r):
        if isinstance(r, str):
            return r
        if hasattr(r, "text") and isinstance(r.text, str):
            return r.text
        if hasattr(r, "content"):
            try:
                return r.content.decode("utf-8", "ignore")
            except Exception:
                return ""
        return ""

    @staticmethod
    def _is_challenge(body):
        return bool(body) and "cdndefend" in body and "cdndefend_js_cookie=" in body

    @staticmethod
    def _extract_seed(body):
        m = re.search(r"'([0-9A-F]{40})'", body or "")
        return m.group(1) if m else ""

    @staticmethod
    def _solve_challenge(seed):
        """SHA1 PoW：枚举 i 直到 sha1(seed+i)[n1]==0xb0 且 [n1+1]==0x0b。"""
        n1 = int(seed[0], 16)
        for i in range(9000000):
            h = hashlib.sha1((seed + str(i)).encode("utf-8")).digest()
            if h[n1] == 0xb0 and h[n1 + 1] == 0x0b:
                return seed + str(i)
        return ""

    def _get_html(self, url):
        """带过盾的 GET，返回 HTML。"""
        cookie = self.cdn_cookie
        code, body = self._raw_req(url, cookie)
        # 850 或命中挑战页 -> 解挑战重试
        if code == 850 or self._is_challenge(body):
            seed = self._extract_seed(body)
            if not seed:
                _, b0 = self._raw_req(self.Host + "/", "")
                seed = self._extract_seed(b0)
            if seed:
                new_cookie = self._solve_challenge(seed)
                if new_cookie:
                    self.cdn_cookie = new_cookie
                    code, body = self._raw_req(url, new_cookie)
                    # 若仍是挑战（cookie 过期/种子换了），再解一次
                    if code == 850 or self._is_challenge(body):
                        seed2 = self._extract_seed(body)
                        if seed2:
                            c2 = self._solve_challenge(seed2)
                            if c2:
                                self.cdn_cookie = c2
                                code, body = self._raw_req(url, c2)
        return body

    # ---------------- 解析 ----------------

    def _parse_list(self, html):
        """解析影片列表卡片（分类/首页 v-item 与 搜索 search-result-item 通用）。"""
        if not html:
            return []
        seen = set()
        out = []

        # ---- 分类/首页卡片：<a href="/detail/xxx.html" class="v-item"> ... </a></div> ----
        for m in re.finditer(
            r'<a\s+href="/detail/(\d+)\.html"\s+class="v-item">([\s\S]*?)</a>\s*</div>',
            html,
        ):
            vid = m.group(1)
            if vid in seen:
                continue
            seen.add(vid)
            block = m.group(2)

            pic = self._pick_cover(block)
            rm = re.search(r'class="v-item-bottom"[\s\S]*?<span>([\s\S]*?)</span>', block)
            remark = self._text_clean(rm.group(1)) if rm else ""

            name = ""
            for tm in re.finditer(r'<div class="v-item-title"([^>]*)>([\s\S]*?)</div>', block):
                if re.search(r"display:\s*none", tm.group(1)):
                    continue
                t = self._text_clean(tm.group(2))
                if not t or re.search(r"kekys|可可影视", t):
                    continue
                name = t
                break
            if not name:
                continue

            out.append({
                "vod_id": vid,
                "vod_name": name,
                "vod_pic": self._fix_pic(pic),
                "vod_remarks": remark,
            })
        if out:
            return out

        # ---- 搜索卡片：<a href="/detail/xxx.html" class="search-result-item"> ... ----
        for sm in re.finditer(
            r'<a\s+href="/detail/(\d+)\.html"\s+class="search-result-item">'
            r'([\s\S]*?)<div class="title">([\s\S]*?)</div>([\s\S]*?)</a>',
            html,
        ):
            sid = sm.group(1)
            if sid in seen:
                continue
            seen.add(sid)
            head = sm.group(2)
            sname = self._text_clean(sm.group(3))
            if not sname:
                continue
            spic = self._pick_cover(head)
            hm = re.search(r'class="search-result-item-header"[\s\S]*?<div>([\s\S]*?)</div>', head)
            sremark = self._text_clean(hm.group(1)) if hm else ""
            out.append({
                "vod_id": sid,
                "vod_name": sname,
                "vod_pic": self._fix_pic(spic),
                "vod_remarks": sremark,
            })
        return out

    @staticmethod
    def _pick_cover(block):
        """从卡片 HTML 里挑真实封面（跳过 logo 占位图）。"""
        for u in re.findall(r'data-original="([^"]+)"', block):
            if "logo_placeholder" not in u and "logo.png" not in u and "empty-box" not in u:
                return u
        return ""

    # ---------------- 通用工具 ----------------

    @staticmethod
    def _text_clean(s):
        if s is None:
            return ""
        s = str(s)
        s = re.sub(r"<[^>]+>", "", s)
        s = (s.replace("&nbsp;", " ").replace("&amp;", "&")
             .replace("&quot;", '"').replace("&#39;", "'"))
        s = re.sub(r"&#\d+;", "", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def _fix_url(self, u):
        u = (u or "").strip()
        if not u:
            return ""
        if u.startswith("//"):
            return "https:" + u
        if u.startswith("/"):
            # 用当前 Host 拼接（避免写死域名导致双重 host）
            return self.Host + u
        return u

    def _fix_pic(self, u):
        u = (u or "").strip()
        if not u:
            return ""
        if u.startswith("//"):
            return "https:" + u
        if u.startswith("/"):
            return IMG_HOST + u   # /vod1/... -> 图片 CDN（主站防盗链）
        return u

    @staticmethod
    def _decode_url(s):
        s = (s or "").replace("&amp;", "&")
        try:
            return unquote(s)
        except Exception:
            return s

    @staticmethod
    def _parse_extend(extend):
        if not extend:
            return {}
        if isinstance(extend, str):
            try:
                return json.loads(extend)
            except Exception:
                return {}
        return extend

    def _ext_value(self, extend, key):
        if not isinstance(extend, dict):
            return ""
        v = extend.get(key) or extend.get(quote(key))
        return str(v) if v else ""

    def _show_url(self, tid, pg, extend):
        seg = [
            str(tid),
            self._ext_value(extend, "class") or self._ext_value(extend, "genre"),
            self._ext_value(extend, "area"),
            self._ext_value(extend, "lang"),
            self._ext_value(extend, "year"),
            self._ext_value(extend, "sort") or "1",
            str(pg),
        ]
        seg = [quote(s) for s in seg]
        return self.Host + "/show/" + "-".join(seg) + ".html"

    def _extract_search_token(self, html):
        m = re.search(r'<input\b[^>]*name=["\']t["\'][^>]*value=["\']([^"\']+)["\']', html, re.I)
        if not m:
            m = re.search(r'<input\b[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']t["\']', html, re.I)
        if not m:
            m = re.search(r'/search\?k=[^"\']*?(?:&amp;|&)t=([^"\'&]+)', html, re.I)
        return self._decode_url(m.group(1)) if m else ""

    def _get_search_token(self):
        html = self._get_html(self.Host + "/")
        token = self._extract_search_token(html)
        if token:
            self.search_token = token
        return self.search_token

    @staticmethod
    def _search_page_count(html, pg, limit):
        m = re.search(r'找到<span class="highlight-text">\s*(\d+)\s*</span>', html, re.I)
        if m:
            pc = max(1, (int(m.group(1)) + limit - 1) // limit)
            return max(pg, pc)
        if "page-item-next" in html:
            return pg + 1
        return pg

    @staticmethod
    def _build_filters():
        def fv(values, all_name="全部"):
            out = [{"n": all_name, "v": ""}]
            for name in values:
                label = name
                if name == "2010_2019":
                    label = "10年代"
                elif name == "2000_2009":
                    label = "00年代"
                elif name == "1990_1999":
                    label = "90年代"
                elif name == "1980_1989":
                    label = "80年代"
                elif name == "0_1979":
                    label = "更早"
                out.append({"n": label, "v": name})
            return out

        ret = {}
        for c in CLASSES:
            ret[c["type_id"]] = [
                {"key": "class", "name": "类型", "value": fv(FILTER_CLASS)},
                {"key": "area", "name": "地区", "value": fv(FILTER_AREA)},
                {"key": "lang", "name": "语言", "value": fv(FILTER_LANG)},
                {"key": "year", "name": "年份", "value": fv(FILTER_YEAR)},
                {"key": "sort", "name": "排序", "value": [
                    {"n": "综合", "v": "1"}, {"n": "最新", "v": "2"},
                    {"n": "最热", "v": "3"}, {"n": "评分", "v": "4"}]},
            ]
        return ret
