import html
import json
import re
import threading
import time
import urllib.parse
from base.spider import Spider

"""
枫叶影视 —— 多镜像合一 TVBox / 影视仓 Python 接口源
支持站点（均为"枫叶4K影院"同模板镜像，内容一致）：
  - https://maihaolian.com
  - https://www.chuodong.com
  - https://www.tjtcdl.com
设计目标：任何一个站点存活，源都能正常使用（自动选活主机）。

==================== 逆向要点（重要） ====================
1) 站点为 苹果CMS(maccms) 架构，列表走 JSON API：
     /index.php/ajax/data.html?mid=1&tid={分类ID}&page={页码}
   返回标准 maccms vod 列表（vod_id/vod_name/vod_pic/type_id 等）。
2) 服务端【忽略】 data.html 的 wd 搜索参数（任何关键词都返回全量），
   且前端搜索走第三方 cupfox，cupfox 搜索页被【验证码墙】拦截，自动化无法过。
   => 搜索改为【本地内存索引】：init 时同步预热基础索引（保证搜索即时可用），
      后台 daemon 继续加深，searchContent 兜底重试；做子串匹配（同金桔影视思路）。
2.5) vod_pic 字段含 HTML 实体（&amp; 等），TVBox 直连会失败，已统一 html.unescape 解码。
3) 详情页为 HTML：/detail/{id}.html（maihaolian/chuodong）或 /chabeihu/{id}.html（tjtcdl）。
   详情页含 /play/{id}-{sid}-{nid}.html 播放链接，按 sid 分组即多条播放线路。
4) 播放页 /play/{id}-{sid}-{nid}.html 内含 `var player_aaaa={...}`，
   其中 url 字段即【明文 m3u8 直链】（encrypt=0），playerContent 直接提取返回。
5) ⚠️ tjtcdl 播放页为另一套 JS 模板，主播放器纯运行时渲染，无静态 m3u8、无可用播放 API，
   无 JS 环境的 spider 无法提取其播放地址——若仅 tjtcdl 存活，浏览/搜索/详情可用，
   但播放为 best-effort（返回播放页交由 TVBox 解析）。其余两站播放完整可用。

铁律落实：全程 self.fetch()；不覆盖 __init__；header 为 dict；不使用 self.post(json=)。
"""

# ---- 候选主机（顺序即优先级：工作模板站点优先） ----
HOSTS = [
    "https://maihaolian.com",
    "https://www.chuodong.com",
    "https://www.tjtcdl.com",
]

# 分类映射（首页导航提取：1电影/2电视剧/3综艺/4动漫/5热门短剧，三站一致）
CATE_LIST = [
    {"type_id": "1", "type_name": "电影"},
    {"type_id": "2", "type_name": "电视剧"},
    {"type_id": "3", "type_name": "综艺"},
    {"type_id": "4", "type_name": "动漫"},
    {"type_id": "5", "type_name": "热门短剧"},
]

# 本地索引爬虫参数（温和，避免触发站点 WAF 验证码墙）
CRAWL_COLD = 3      # 冷启动每类爬取页数（init 并发预热，保证搜索即时可用）
CRAWL_MAX = 10      # 单类最多页数（后台 daemon 加深，扩大搜索覆盖面）
CRAWL_DELAY = 0.3   # 爬取间隔(秒)
TEST_VOD_ID = "96683"  # 用于探测详情页路径的已知影片 id

# ---- 共享索引（三站内容一致，全进程只建一份） ----
_index_lock = threading.Lock()
_index = []          # [{"id","name","pic","type_id","remarks"}, ...]
_index_ids = set()
_index_building = False
_index_done = False


class Spider(Spider):

    def init(self, extend=""):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://maihaolian.com/",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        }
        # 用户可通过 extend 指定优先主机（必须以 http 开头）
        prefer = ""
        if isinstance(extend, str) and extend.strip() and re.match(r"^https?://", extend.strip()):
            prefer = extend.strip().rstrip("/")
        self.host = self._pick_host(prefer)
        self.detail_path = self._detect_detail_path()
        # 同步预热基础索引（轻量：每类冷启动若干页），保证 TVBox 一搜索就有热播内容可用
        self._crawl_cold_sync()
        # 后台 daemon 线程继续加深索引（覆盖更多历史影片）
        self._start_crawler()

    def getName(self):
        return "枫叶影视"

    # ============ 主机选活 ============
    def _fetch(self, url, headers=None, retry=1):
        h = headers if headers else self.header
        try:
            resp = self.fetch(url, headers=h)
        except Exception:
            resp = None
        if resp is None and retry > 0:
            # 当前主机可能挂了，重新选活再试一次
            self.host = self._pick_host()
            url2 = url.replace(self._host_of(url), self.host, 1) if self._host_of(url) else url
            try:
                resp = self.fetch(url2, headers=h)
            except Exception:
                resp = None
        return resp

    @staticmethod
    def _host_of(url):
        m = re.match(r"^(https?://[^/]+)", url)
        return m.group(1) if m else ""

    def _test_host(self, host):
        url = host + "/index.php/ajax/data.html?mid=1&tid=1&page=1"
        try:
            resp = self.fetch(url, headers=self.header)
        except Exception:
            return False
        if resp is None:
            return False
        try:
            if hasattr(resp, "text"):
                txt = resp.text
            else:
                txt = resp.content.decode("utf-8", "ignore")
            return '"code":1' in txt or '"code": 1' in txt
        except Exception:
            return False

    def _pick_host(self, prefer=""):
        ordered = ([prefer] if prefer else []) + [h for h in HOSTS if h != prefer]
        for h in ordered:
            if self._test_host(h):
                self.header["Referer"] = h + "/"
                return h
        # 全挂则退回到首选/第一个，至少保证结构可用
        return prefer or HOSTS[0]

    def _detect_detail_path(self):
        for path in ("detail", "chabeihu"):
            url = "%s/%s/%s.html" % (self.host, path, TEST_VOD_ID)
            resp = self._fetch(url)
            if resp is None:
                continue
            html = self._text(resp)
            if html and "/play/" in html and "系统安全验证" not in html:
                return path
        return "detail"

    @staticmethod
    def _text(resp):
        if resp is None:
            return ""
        try:
            if hasattr(resp, "text"):
                return resp.text or ""
        except Exception:
            pass
        try:
            return resp.content.decode("utf-8", "ignore")
        except Exception:
            return ""

    # ============ homeContent ============
    def homeContent(self, filter):
        return {"class": CATE_LIST, "filters": {}}

    # ============ categoryContent ============
    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg)
        except Exception:
            pg = 1
        url = "%s/index.php/ajax/data.html?mid=1&tid=%s&page=%d" % (self.host, tid, pg)
        resp = self._fetch(url)
        txt = self._text(resp)
        if not txt:
            return {"list": [], "page": pg, "pagecount": 1, "limit": 10, "total": 0}
        try:
            d = json.loads(txt)
        except Exception:
            return {"list": [], "page": pg, "pagecount": 1, "limit": 10, "total": 0}
        items = [self._card_to_vod(x) for x in (d.get("list") or [])]
        items = [x for x in items if x]
        pag = d.get("pagination") or {}
        total = pag.get("total") or d.get("total") or 0
        limit = pag.get("limit") or d.get("limit") or 10
        pagecount = (int(total) + limit - 1) // limit if total else 1
        return {
            "list": items, "page": pg, "pagecount": pagecount,
            "limit": limit, "total": int(total),
        }

    @staticmethod
    def _card_to_vod(x):
        vid = x.get("vod_id")
        if not vid:
            return None
        pic = x.get("vod_pic") or ""
        pic = html.unescape(pic).replace("\\/", "/")
        name = html.unescape(x.get("vod_name") or "")
        remarks = x.get("vod_remarks") or ""
        if not remarks and x.get("vod_year"):
            remarks = str(x.get("vod_year"))
        if not remarks and x.get("vod_area"):
            remarks = x.get("vod_area")
        return {
            "vod_id": str(vid),
            "vod_name": name,
            "vod_pic": pic,
            "vod_remarks": remarks,
        }

    # ============ searchContent（本地索引） ============
    def searchContent(self, key, quick, pg="1"):
        try:
            pg = int(pg)
        except Exception:
            pg = 1
        results = self._local_search(key, pg)
        if not results and not _index:
            # 基础索引都还没建起来（可能首轮被 WAF 拦），同步补一轮再搜，确保搜索可用
            self._crawl_cold_sync()
            results = self._local_search(key, pg)
        return {
            "list": results, "page": pg, "pagecount": 1, "limit": 20, "total": len(results),
        }

    def _local_search(self, key, pg, limit=20):
        key = (key or "").strip().lower()
        if not key:
            return []
        with _index_lock:
            pool = list(_index)
        scored = []
        for it in pool:
            name = it["name"].lower()
            idx = name.find(key)
            if idx < 0:
                continue
            # 前缀匹配优先
            score = 0 if idx == 0 else 1
            scored.append((score, name, it))
        scored.sort(key=lambda t: (t[0], t[1]))
        start = (pg - 1) * limit
        page = scored[start:start + limit]
        return [self._card_to_vod({
            "vod_id": it["id"], "vod_name": it["name"],
            "vod_pic": it["pic"], "vod_remarks": it.get("remarks", ""),
        }) for _, _, it in page]

    # ============ detailContent ============
    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        vid = str(ids[0])
        html = self._load_detail(vid)
        if not html:
            return {"list": []}
        sources = self._parse_play(html, vid)
        if not sources:
            return {"list": []}
        play_from = "$$$".join(s["name"] for s in sources)
        play_url = "$$$".join(s["urls"] for s in sources)
        # 标题/海报/演员等从详情页补充
        title = self._meta(html, "title")
        pic = self._meta(html, "pic") or (sources[0]["pic"] if sources[0].get("pic") else "")
        return {
            "list": [{
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_play_from": play_from,
                "vod_play_url": play_url,
            }]
        }

    def _load_detail(self, vid):
        path = getattr(self, "detail_path", "detail")
        # 依次尝试当前主机两种路径；遇验证码墙则切换其它存活主机重试（镜像同内容同 id）
        hosts = [self.host] + [h for h in HOSTS if h != self.host]
        for host in hosts:
            for p in (path, "chabeihu" if path == "detail" else "detail"):
                url = "%s/%s/%s.html" % (host, p, vid)
                resp = self._fetch(url)
                html = self._text(resp)
                if not html:
                    continue
                if "系统安全验证" in html:
                    continue  # 验证码墙，换主机/路径
                if "/play/" in html:
                    self.host = host
                    self.detail_path = p
                    self.header["Referer"] = host + "/"
                    return html
        return ""

    def _parse_play(self, html, vid):
        """解析详情页 /play/{id}-{sid}-{nid}.html 链接，按 sid 分组为多条线路。"""
        links = re.findall(r'href="(/play/(\d+)-(\d+)-(\d+)\.html)"[^>]*>([^<]*)</a>', html)
        if not links:
            # 兜底：不带环绕标签的裸链接
            links = [(m.group(0),) + m.groups() for m in
                     re.finditer(r'(/play/(\d+)-(\d+)-(\d+)\.html)', html)]
        groups = {}
        for href, _vid, sid, nid, *rest in links:
            text = rest[0] if rest else ""
            groups.setdefault(sid, []).append((int(nid), text.strip(), href))
        sources = []
        for sid in sorted(groups.keys(), key=lambda x: int(x)):
            eps = sorted(groups[sid], key=lambda t: t[0])
            parts = []
            for nid, text, href in eps:
                label = text if text else ("第%02d集" % nid)
                parts.append("%s$%s" % (label, href))
            # 抓取首集配图（详情页海报）
            pic = self._meta(html, "pic")
            sources.append({
                "name": "线路" + sid,
                "urls": "#".join(parts),
                "pic": pic,
            })
        return sources

    @staticmethod
    def _meta(doc, field):
        if field == "title":
            m = re.search(r'<title>([^<]*?)[_|-]', doc)
            if m:
                return m.group(1).strip()
            m = re.search(r'<title>([^<]*)</title>', doc)
            return m.group(1).strip() if m else ""
        if field == "pic":
            m = re.search(r'"vod_pic"\s*:\s*"([^"]+)"', doc)
            if not m:
                m = re.search(r'data-src="(https?://[^"]+\.(?:jpg|jpeg|png|webp))"', doc)
            if m:
                return html.unescape(m.group(1)).replace("\\/", "/")
        return ""

    # ============ playerContent ============
    def playerContent(self, flag, id, vipFlags):
        if not id:
            return {"parse": 0, "url": ""}
        # id 即自包含的 /play/{id}-{sid}-{nid}.html 路径（三站镜像同 id）
        if id.startswith("http"):
            rel = id
            hosts = [self._host_of(id) or self.host]
        else:
            rel = id if id.startswith("/") else "/" + id
            hosts = [self.host] + [h for h in HOSTS if h != self.host]
        for host in hosts:
            url = host + rel if not id.startswith("http") else rel
            # 播放页带详情页 Referer，降低验证码墙触发概率
            vid_m = re.search(r"/play/(\d+)-", rel)
            ref = (host + "/%s/%s.html" % (getattr(self, "detail_path", "detail"), vid_m.group(1))) if vid_m else (host + "/")
            resp = self._fetch(url, headers={**self.header, "Referer": ref})
            html = self._text(resp)
            if not html or "系统安全验证" in html:
                continue
            m3u8 = self._extract_m3u8(html)
            if m3u8:
                return {"parse": 0, "url": m3u8,
                        "header": {"User-Agent": self.header["User-Agent"], "Referer": host + "/"}}
        # tjtcdl 等 JS 渲染站点无静态 m3u8：交回播放页由 TVBox 解析（best-effort）
        return {"parse": 1, "url": self.host + rel}

    @staticmethod
    def _extract_m3u8(html):
        if not html:
            return ""
        # 优先解析 player_aaaa JSON（encrypt=0 明文；encrypt=2 为 base64）
        # 手工括号配对，避免嵌套 {} 与非贪婪截断问题
        i = html.find("var player_")
        if i >= 0:
            seg = html[i:]
            j = seg.find("{")
            if j >= 0:
                depth = 0
                end = -1
                for k in range(j, len(seg)):
                    if seg[k] == "{":
                        depth += 1
                    elif seg[k] == "}":
                        depth -= 1
                        if depth == 0:
                            end = k
                            break
                if end > 0:
                    try:
                        import base64
                        d = json.loads(seg[j:end + 1])
                        url = (d.get("url") or "").replace("\\/", "/")
                        enc = str(d.get("encrypt", "0"))
                        if url:
                            if enc == "2":
                                try:
                                    url = base64.b64decode(url).decode("utf-8", "ignore")
                                except Exception:
                                    pass
                            if ".m3u8" in url or url.startswith("http"):
                                return url
                    except Exception:
                        pass
        # 兜底：页面内明文 m3u8
        m2 = re.search(r'https?://[^\s"\'\\]+?\.m3u8', html)
        if m2:
            return m2.group(0)
        return ""

    # ============ 本地索引爬虫 ============
    def _start_crawler(self):
        global _index_building
        with _index_lock:
            # 基础索引已由 _crawl_cold_sync 建立；仅在未在进行且未全部完成时启动加深
            if _index_building or _index_done:
                return
            _index_building = True
        t = threading.Thread(target=self._crawl_worker, daemon=True)
        t.start()

    def _crawl_once(self, tid, page):
        url = "%s/index.php/ajax/data.html?mid=1&tid=%s&page=%d" % (self.host, tid, page)
        resp = self._fetch(url)
        txt = self._text(resp)
        if not txt:
            return []
        try:
            d = json.loads(txt)
        except Exception:
            return []
        out = []
        for x in (d.get("list") or []):
            vid = x.get("vod_id")
            if not vid:
                continue
            name = (x.get("vod_name") or "").strip()
            if not name:
                continue
            pic = html.unescape(x.get("vod_pic") or "").replace("\\/", "/")
            remarks = x.get("vod_remarks") or ""
            out.append({"id": str(vid), "name": name, "pic": pic, "type_id": x.get("type_id"),
                        "remarks": remarks})
        return out

    def _crawl_cold_sync(self):
        """同步建立基础索引（每类 CRAWL_COLD 页），init 调用，保证搜索即时可用。
        用线程池并发各分类，压缩 init 耗时，避免 TVBox 源加载超时。
        不延迟、不置 _index_done（加深交给 daemon）。若全被 WAF 拦导致 _index 仍空，
        searchContent 会兜底再次触发。"""
        global _index_building
        with _index_lock:
            if _index_building or _index:
                return
            _index_building = True

        def _work(tid):
            for pg in range(1, CRAWL_COLD + 1):
                items = self._crawl_once(tid, pg)
                self._merge(items)
                if not items:
                    break

        try:
            threads = [threading.Thread(target=_work, args=(c["type_id"],)) for c in CATE_LIST]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        finally:
            with _index_lock:
                _index_building = False

    def _crawl_worker(self):
        """后台加深：从 CRAWL_COLD+1 爬到 CRAWL_MAX，覆盖更多历史影片。"""
        global _index_done, _index_building
        with _index_lock:
            _index_building = True
        try:
            for cate in CATE_LIST:
                tid = cate["type_id"]
                for pg in range(CRAWL_COLD + 1, CRAWL_MAX + 1):
                    items = self._crawl_once(tid, pg)
                    self._merge(items)
                    if not items:
                        break
                    time.sleep(CRAWL_DELAY)
        finally:
            with _index_lock:
                _index_building = False
                _index_done = True

    @staticmethod
    def _merge(items):
        with _index_lock:
            for it in items:
                if it["id"] not in _index_ids:
                    _index_ids.add(it["id"])
                    _index.append(it)


"""
==============================================================================
部署 tv.json 示例：
{
  "key": "枫叶影视",
  "name": "枫叶影视",
  "type": 3,
  "api": "./py/枫叶影视.py",
  "searchable": 1,
  "filterable": 0,
  "changeable": 1,
  "playerType": 2
}

说明：
- 多镜像合一：内置 maihaolian / chuodong / tjtcdl 三个枫叶影院镜像，init 时自动选活，
  任一站点存活即可使用；可在 extend 字段手动指定优先主机。
- 列表/分类走 苹果CMS 标准 JSON API（/index.php/ajax/data.html），稳定可用。
- 搜索：因服务端忽略 wd 且前端 cupfox 搜索被验证码墙拦截，改为本地内存索引。
  init 时【并发预热】基础索引（保证 TVBox 一搜索就有热播内容可用），后台 daemon 继续
  加深覆盖更多影片；若首轮被 WAF 拦导致索引为空，searchContent 会兜底同步再建一轮。
  支持子串/前缀匹配。覆盖以【近期/热播】为主（数百~千部），经典老片因服务端无搜索
  接口、排在深页，需走分类浏览——这是站点客观限制，非代码缺陷。
- 图片：vod_pic 字段含 HTML 实体（&amp; 等），TVBox 直连会失败，已统一 html.unescape
  解码；实测解码后图片（百度图床）无 Referer 也可 200 访问，TVBox 可正常加载。
- 详情：解析 /play/{id}-{sid}-{nid}.html 链接，按 sid 分组为多线路；
  详情路径自动适配 /detail/ 与 /chabeihu/（tjtcdl 变种）。
- 播放：提取播放页 var player_aaaa 的明文 m3u8 直链（encrypt=0/2 均已处理）。
  注意 tjtcdl 播放页为 JS 渲染、无静态 m3u8，若仅该站存活则播放为 best-effort。
==============================================================================
"""
