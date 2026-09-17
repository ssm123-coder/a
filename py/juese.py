# -*- coding: utf-8 -*-
"""
TVBox 影视仓 Py 爬虫 - xHamster 中文站
FongMi / OK影视 兼容
继承 base.spider.Spider 基类，返回 dict
"""

import sys
sys.path.append('..')
from base.spider import Spider
import re
import json
import requests
from urllib.parse import quote


# ============================================================
#  站点配置
# ============================================================
SITE_DOMAINS = [
    "https://zh.xhamster1.desi",
    "https://zh.xhamster.com",
    "https://xhamster.com",
    "https://xhamster2.com",
    "https://xhamster3.com",
    "https://xhamster.desi",
    "https://xhamster18.desi",
    "https://xhamster20.desi",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://zh.xhamster1.desi/",
}

PLAYER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://zh.xhamster1.desi/",
}

TIMEOUT = 20

# 精选分类
CATEGORY_LIST = [
    {"type_id": "newest",          "type_name": "最新视频"},
    {"type_id": "best/weekly",     "type_name": "本周最佳"},
    {"type_id": "best/monthly",    "type_name": "本月最佳"},
    {"type_id": "best",            "type_name": "全部最佳"},
    {"type_id": "hd",              "type_name": "高清视频"},
    {"type_id": "4k",              "type_name": "4K视频"},
    {"type_id": "categories/shorts",    "type_name": "短视频"},
    {"type_id": "categories/asian",      "type_name": "亚洲人"},
    {"type_id": "categories/japanese",   "type_name": "日本人"},
    {"type_id": "categories/chinese",    "type_name": "中国人"},
    {"type_id": "categories/korean",     "type_name": "韩国人"},
    {"type_id": "categories/jav",        "type_name": "日本AV"},
    {"type_id": "categories/uncensored", "type_name": "无码"},
    {"type_id": "categories/milf",       "type_name": "人妻"},
    {"type_id": "categories/mom",        "type_name": "人母"},
    {"type_id": "categories/mature",     "type_name": "成熟"},
    {"type_id": "categories/teen",       "type_name": "青年"},
    {"type_id": "categories/big-tits",   "type_name": "大奶子"},
    {"type_id": "categories/anal",       "type_name": "肛交"},
    {"type_id": "categories/creampie",   "type_name": "内射"},
    {"type_id": "categories/threesome",  "type_name": "3P"},
    {"type_id": "categories/amateur",    "type_name": "素人"},
    {"type_id": "categories/homemade",   "type_name": "家庭自制"},
    {"type_id": "categories/blowjob",    "type_name": "口交"},
    {"type_id": "categories/cosplay",    "type_name": "角色扮演"},
    {"type_id": "categories/hentai",     "type_name": "成人动漫"},
    {"type_id": "categories/cartoon",    "type_name": "卡通"},
    {"type_id": "categories/3d",         "type_name": "3D"},
    {"type_id": "categories/lesbian",    "type_name": "女同"},
    {"type_id": "categories/interracial","type_name": "跨人种"},
    {"type_id": "categories/group-sex",  "type_name": "群交"},
    {"type_id": "categories/gangbang",   "type_name": "多对一群交"},
    {"type_id": "categories/bdsm",       "type_name": "捆绑SM"},
    {"type_id": "categories/webcam",     "type_name": "直播"},
    {"type_id": "categories/pov",        "type_name": "第一人称"},
    {"type_id": "categories/vintage",    "type_name": "复古"},
    {"type_id": "categories/pregnant",   "type_name": "怀孕"},
    {"type_id": "categories/latina",     "type_name": "拉丁美女"},
    {"type_id": "categories/black",     "type_name": "黑人"},
    {"type_id": "categories/indian",     "type_name": "印度"},
    {"type_id": "categories/russian",    "type_name": "俄罗斯人"},
]

SORT_FILTER = {
    "key": "sort",
    "name": "排序",
    "init": "",
    "value": [
        {"n": "默认", "v": ""},
        {"n": "最新", "v": "newest"},
        {"n": "最佳", "v": "best"},
    ]
}

QUALITY_FILTER = {
    "key": "quality",
    "name": "画质",
    "init": "",
    "value": [
        {"n": "全部", "v": ""},
        {"n": "HD",   "v": "hd"},
        {"n": "4K",   "v": "4k"},
    ]
}

DURATION_FILTER = {
    "key": "duration",
    "name": "时长",
    "init": "",
    "value": [
        {"n": "全部",     "v": ""},
        {"n": "0-10分钟",  "v": "0-10"},
        {"n": "10-30分钟", "v": "10-30"},
        {"n": "30分钟+",   "v": "30-9999"},
    ]
}


# ============================================================
#  模块级工具函数
# ============================================================
_domain_cache = {"value": None}


def _try_domains():
    """探测可用域名"""
    for domain in SITE_DOMAINS:
        try:
            resp = requests.head(domain, headers=HEADERS, timeout=10, allow_redirects=True)
            if resp.status_code < 500:
                return domain
        except Exception:
            continue
    return SITE_DOMAINS[0]


def _get_domain():
    if _domain_cache["value"] is None:
        _domain_cache["value"] = _try_domains()
    return _domain_cache["value"]


def _fetch_html(url):
    """请求页面HTML"""
    headers = HEADERS.copy()
    headers["Referer"] = _get_domain() + "/"
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        # 403/429 换UA重试
        if resp.status_code in (403, 429):
            alt = headers.copy()
            alt["User-Agent"] = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.4 Safari/605.1.15"
            )
            resp2 = requests.get(url, headers=alt, timeout=TIMEOUT)
            if resp2.status_code == 200:
                resp2.encoding = resp2.apparent_encoding or "utf-8"
                return resp2.text
    except Exception:
        pass
    return ""


def _parse_video_list(html):
    """从HTML中解析视频列表，返回 list[dict]"""
    if not html:
        return []
    videos = []
    seen = set()
    # 按 data-video-id 分割视频块
    blocks = re.split(r'(?=data-video-id="\d+")', html)
    for block in blocks[1:]:
        try:
            href_m = re.search(r'href="(https?://[^"]*?/videos/[^"?]+)"', block)
            if not href_m:
                continue
            video_url = href_m.group(1)
            if "/creators/" in video_url:
                continue
            slug_m = re.search(r'/videos/([^"?]+)', video_url)
            if not slug_m:
                continue
            vod_id = slug_m.group(1)
            if vod_id in seen:
                continue
            seen.add(vod_id)
            sb = block[:2000]

            # 提取封面图: 优先 <img src>, 回退 <noscript><img src>, 回退 aria-label 无图
            img_m = re.search(r'<img[^>]*?src="(https?://[^"]+)"', sb)
            if not img_m:
                # Googlebot UA 下图片在 noscript 标签内
                ns_m = re.search(r'<noscript>\s*<img[^>]*?src="(https?://[^"]+)"', block)
                if ns_m:
                    img_m = ns_m

            # 提取标题: 优先 alt, 回退 aria-label
            alt_m = re.search(r'<img[^>]*?alt="([^"]*)"', sb)
            if alt_m:
                vod_name = alt_m.group(1)
            else:
                aria_m = re.search(r'aria-label="([^"]*)"', sb)
                vod_name = aria_m.group(1) if aria_m else vod_id

            # 提取时长
            dur_m = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', sb)

            videos.append({
                "vod_id": vod_id,
                "vod_name": vod_name,
                "vod_pic": (img_m.group(1) if img_m else ""),
                "vod_remarks": (dur_m.group(1) if dur_m else ""),
            })
        except Exception:
            continue
    # 方案2: 从 <a> 标签提取
    if not videos:
        for match in re.finditer(r'<a[^>]*href="(https?://[^"]*?/videos/[^"?]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
            video_url = match.group(1)
            if "/creators/" in video_url:
                continue
            slug_m = re.search(r'/videos/([^"?]+)', video_url)
            if not slug_m:
                continue
            vod_id = slug_m.group(1)
            if vod_id in seen:
                continue
            seen.add(vod_id)
            content = match.group(2)
            img_m = re.search(r'<img[^>]*?src="(https?://[^"]+)"', content)
            alt_m = re.search(r'<img[^>]*?alt="([^"]*)"', content)
            if not img_m:
                ns_m = re.search(r'<noscript>\s*<img[^>]*?src="(https?://[^"]+)"', content)
                if ns_m:
                    img_m = ns_m
            pos = match.end()
            ctx = html[pos:pos+500]
            dur_m = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', ctx)
            videos.append({
                "vod_id": vod_id,
                "vod_name": (alt_m.group(1) if alt_m else vod_id),
                "vod_pic": (img_m.group(1) if img_m else ""),
                "vod_remarks": (dur_m.group(1) if dur_m else ""),
            })
    return videos


def _parse_m3u8(html):
    """从详情页HTML提取m3u8播放地址，并转换为H264编码以提升兼容性"""
    if not html:
        return ""
    # <link rel="preload" href="...m3u8" ...>
    m = re.search(r'<link[^>]*?rel="preload"[^>]*?href="([^"]+\.m3u8[^"]*)"', html, re.IGNORECASE)
    if m:
        url = m.group(1)
        # 网站默认返回 AV1 编码的 m3u8，很多播放器不支持 AV1 解码
        # 将 URL 中的 av1 替换为 h264，获取 H.264 编码版本，兼容性最好
        url = url.replace(".av1.", ".h264.")
        return url
    # 直接搜索 m3u8
    for m in re.finditer(r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)', html):
        url = m.group(1)
        if "thumb-" not in url and "preview" not in url.lower():
            url = url.replace(".av1.", ".h264.")
            return url
    return ""


def _parse_mp4_list(html):
    """从详情页HTML提取MP4直链列表"""
    if not html:
        return []
    seen = set()
    result = []
    for m in re.finditer(r'(https?://[^"\'<>\s]+/\d+p\.h264\.mp4[^"\'<>\s]*)', html):
        url = m.group(1)
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def _parse_page_count(html):
    """从HTML解析总页数"""
    if not html:
        return 1
    max_page = 1
    for m in re.finditer(r'href="[^"]*?(?:/categories/|/search/|/newest|/best/|/hd|/4k|/shorts)[^"]*?/(\d+)"', html):
        try:
            p = int(m.group(1))
            if p > max_page:
                max_page = p
        except ValueError:
            continue
    return min(max_page, 9999)


def _parse_title(html):
    if not html:
        return ""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if t:
            return t
    m = re.search(r'<title>(.*?)(?:\s*\|\s*xHamster)?</title>', html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""


def _parse_thumbnail(html):
    if not html:
        return ""
    m = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', html, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'<link[^>]*rel="preload"[^>]*href="([^"]+)"[^>]*as="image"', html, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


# ============================================================
#  Spider 主类 - 继承 base.spider.Spider
# ============================================================
class Spider(Spider):

    def getName(self):
        return "xHamster中文"

    def init(self, extend=""):
        pass

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        if not url:
            return False
        return bool(re.match(r'.*\.(m3u8|mp4|flv|ts)', url, re.IGNORECASE))

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        """首页: 分类列表 + 首页视频 (返回 dict)"""
        result = {}
        classes = []
        for cat in CATEGORY_LIST:
            classes.append({
                "type_id": cat["type_id"],
                "type_name": cat["type_name"],
            })
        result["class"] = classes

        if filter:
            filters = {}
            for cat in CATEGORY_LIST:
                tid = cat["type_id"]
                cf = [SORT_FILTER.copy()]
                if tid.startswith("categories/"):
                    cf.append(QUALITY_FILTER.copy())
                cf.append(DURATION_FILTER.copy())
                filters[tid] = cf
            result["filters"] = filters

        domain = _get_domain()
        html = _fetch_html(domain + "/")
        result["list"] = _parse_video_list(html)
        return result

    def homeVideoContent(self):
        """首页推荐视频 (返回 dict)"""
        domain = _get_domain()
        html = _fetch_html(domain + "/")
        return {"list": _parse_video_list(html)}

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 (返回 dict)"""
        result = {
            "list": [],
            "page": 1,
            "pagecount": 1,
            "limit": 36,
            "total": 0,
        }
        try:
            page = int(pg) if pg else 1
        except (ValueError, TypeError):
            page = 1
        result["page"] = page

        if extend is None:
            extend = {}
        if isinstance(extend, str):
            try:
                extend = json.loads(extend) if extend else {}
            except Exception:
                extend = {}

        sort = extend.get("sort", "") or ""
        quality = extend.get("quality", "") or ""
        duration = extend.get("duration", "") or ""

        # 构建URL路径
        url_path = tid
        if quality and tid.startswith("categories/"):
            parts = tid.split("/")
            if len(parts) == 2:
                url_path = tid + "/" + quality

        if sort and tid.startswith("categories/"):
            url_path = tid + "/" + sort

        domain = _get_domain()
        if page > 1:
            url = domain + "/" + url_path + "/" + str(page)
        else:
            url = domain + "/" + url_path

        html = _fetch_html(url)
        if html:
            videos = _parse_video_list(html)
            # 时长筛选
            if duration:
                try:
                    min_min, max_min = duration.split("-")
                    min_min = int(min_min)
                    max_min = int(max_min)
                    filtered = []
                    for v in videos:
                        remarks = v.get("vod_remarks", "")
                        if remarks:
                            p = remarks.split(":")
                            if len(p) == 2:
                                tm = int(p[0])
                            elif len(p) == 3:
                                tm = int(p[0]) * 60 + int(p[1])
                            else:
                                continue
                            if min_min <= tm <= max_min:
                                filtered.append(v)
                        else:
                            filtered.append(v)
                    videos = filtered
                except Exception:
                    pass
            result["list"] = videos
            result["pagecount"] = _parse_page_count(html)
            result["total"] = result["pagecount"] * result["limit"]
        return result

    def detailContent(self, ids):
        """视频详情 (返回 dict)"""
        if not ids:
            return {"list": []}
        vod_id = ids[0] if isinstance(ids, list) else ids
        domain = _get_domain()
        url = domain + "/videos/" + vod_id
        html = _fetch_html(url)
        if not html:
            return {"list": []}

        title = _parse_title(html) or vod_id
        pic = _parse_thumbnail(html)
        m3u8_url = _parse_m3u8(html)

        # 只使用 m3u8 (HLS) 播放
        # MP4 直链绑定了请求时服务器IP (data=IP-dvp)，用户播放器IP不同会403
        play_list = []
        if m3u8_url:
            play_list.append("HLS播放$" + m3u8_url)
        play_url = "#".join(play_list) if play_list else ""

        desc = ""
        dm = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html, re.IGNORECASE)
        if dm:
            desc = dm.group(1)

        return {
            "list": [{
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": "xHamster",
                "vod_play_url": play_url,
            }]
        }

    def searchContent(self, key, quick, pg="1"):
        """搜索 (返回 dict)，支持2参数和3参数调用"""
        if not key:
            return {"list": []}
        try:
            page = int(pg) if pg else 1
        except (ValueError, TypeError):
            page = 1

        domain = _get_domain()
        keyword = quote(key.strip())
        if page > 1:
            url = domain + "/search/" + keyword + "/" + str(page)
        else:
            url = domain + "/search/" + keyword

        html = _fetch_html(url)
        if not html:
            return {"list": []}
        videos = _parse_video_list(html)
        return {"list": videos}

    def playerContent(self, flag, id, vipFlags):
        """播放解析 (返回 dict)"""
        if not id:
            return {"parse": 0, "url": ""}
        play_url = id.strip()
        result = {
            "parse": 0,
            "playUrl": "",
            "url": play_url,
            "header": json.dumps(PLAYER_HEADERS),
        }
        return result

    def localProxy(self, param):
        return [200, "text/plain", b"", ""]
