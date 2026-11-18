#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网盘聚合.py — 17 站聚合版

胶囊行 = 玩偶/木偶/多多/欧歌/二小/虎斑/快映/花卷/夸父/123/卡卡/即刻/指南/双星/爱盼/觅盘/趣盘

import sys
import os
import json
import time
import hashlib
import re
import threading
import queue as _queue
from urllib.parse import quote, unquote, urlencode
from concurrent.futures import ThreadPoolExecutor, wait, as_completed

import requests
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except Exception:
    HTTPAdapter = None
    Retry = None

sys.path.append('..')
try:
    from base.spider import Spider
except ImportError:
    class Spider:
        def init(self, extend=""):
            pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

MOBILE_UA = ("Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 "
             "MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36")
PC_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
         "uc-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 "
         "Safari/537.36 Channel/pckk_other_ch")
TV_UA = ("Mozilla/5.0 (Linux; U; Android 12; zh-cn; V2238A Build/V417IR) "
         "AppleWebKit/533.1 (KHTML, like Gecko) Mobile Safari/533.1")
DART_UA = "Dart/2.19(dart:io)"

VIDEO_EXT = ('.mp4', '.mkv', '.ts', '.iso', '.rmvb', '.avi', '.mov', '.mpeg', '.mpg',
             '.wmv', '.3gp', '.asf', '.m4v', '.flv', '.vob', '.strm', '.tp', '.f4v',
             '.webm', '.m2ts', '.ogv')

PAN_RES = [
    ("UC",   re.compile(r"https?://drive\.uc\.cn/s/[0-9a-zA-Z]+(?:\?pwd=\w+)?")),
    ("夸克",  re.compile(r"https?://pan\.quark\.cn/s/[0-9a-zA-Z]+(?:\?pwd=\w+)?")),
    ("百度",  re.compile(r"https?://pan\.baidu\.com/s/[0-9a-zA-Z_\-]+(?:\?pwd=\w+)?")),
    ("123",  re.compile(r"https?://(?:www\.)?(?:123pan|123684|123865|123912|123592)\.(?:com|cn)/s/[\w\-]+(?:\?[^\"'<>\s]*)?")),
    ("迅雷",  re.compile(r"https?://pan\.xunlei\.com/s/[\w\-]+")),
    ("天翼",  re.compile(r"https?://cloud\.189\.cn/(?:t/|web/share\?code=)[\w]+")),
    ("阿里",  re.compile(r"https?://(?:www\.)?(?:aliyundrive|alipan)\.com/s/[\w]+")),
    ("移动",  re.compile(r"https?://caiyun\.139\.com/[\w/]+")),
]


def make_session(ua=MOBILE_UA):
    s = requests.Session()
    s.headers.update({"User-Agent": ua})
    if HTTPAdapter is not None and Retry is not None:
        try:
            retry = Retry(total=1, backoff_factor=0.2, status_forcelist=[429, 500, 502, 503])
            adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=32)
            s.mount("https://", adapter)
            s.mount("http://", adapter)
        except Exception:
            pass
    return s


def _ensure_url(site):

    if site.get("_url_ok"):
        return
    ok = False
    for u in site["site"]:
        try:
            site["session"].head(u, timeout=1.5, allow_redirects=True)
            site["url"] = u
            ok = True
            break
        except Exception:
            continue
    site["_url_ok"] = True
    if not ok:

        site["_dead_until"] = time.time() + 300


def http_get(session, url, timeout=8, headers=None, binary=False):
    r = session.get(url, timeout=timeout, headers=headers or {})
    r.encoding = 'utf-8'
    return r.content if binary else r.text


class UCDrive:
    PC_API = "https://pc-api.uc.cn/1/clouddrive"
    OPEN_API = "https://open-api-drive.uc.cn"
    SHARE_RE = re.compile(r"https?://drive\.uc\.cn/s/([0-9a-zA-Z]+)(?:\?pwd=(\w+))?")

    def __init__(self, cookie=""):
        self.cookie = cookie
        self._stoken_cache = {}
        self._machine_code = None

    def _headers_common(self):
        return {"Referer": "https://drive.uc.cn", "Cookie": self.cookie or "", "User-Agent": PC_UA}

    def _headers_anon(self):
        return {"User-Agent": PC_UA, "Accept-Encoding": "identity", "Referer": "https://drive.uc.cn"}

    def _post_json(self, url, body, headers=None, timeout=20):
        hdrs = {"User-Agent": PC_UA, "Content-Type": "application/json; charset=utf-8"}
        if headers:
            hdrs.update(headers)
        resp = requests.post(url, json=body, headers=hdrs, timeout=timeout)
        resp.encoding = "utf-8"
        return resp.text

    def share_token(self, pwd_id, passcode=""):
        url = f"{self.PC_API}/share/sharepage/token?__t={int(time.time() * 1000)}"
        body = {"pwd_id": pwd_id, "passcode": passcode or ""}
        text = self._post_json(url, body, self._headers_common())
        data = json.loads(text)
        stoken = (data.get("data") or {}).get("stoken", "")
        if stoken:
            self._stoken_cache[pwd_id] = stoken
        return data, stoken

    def _get_stoken(self, pwd_id, passcode=""):
        if pwd_id in self._stoken_cache:
            return self._stoken_cache[pwd_id]
        _, stoken = self.share_token(pwd_id, passcode)
        return stoken

    def list_videos(self, share_url, passcode="", limit=0):
        """返回 [{'fid','file_name','size','share_fid_token','pwd_id','stoken'}]
        limit>0 时找到 limit 个视频即停（验证场景免整树遍历）"""
        m = self.SHARE_RE.search(share_url or "")
        if not m:
            return []
        pwd_id, url_pwd = m.group(1), m.group(2)
        pc = passcode or url_pwd or ""
        try:
            stoken = self._get_stoken(pwd_id, pc)
        except Exception:
            return []
        if not stoken:
            return []
        out = []
        self._walk(pwd_id, stoken, "0", out, depth=0, limit=limit)
        return out

    def _walk(self, pwd_id, stoken, pdir_fid, out, depth, limit=0):
        if depth > 12 or (limit and len(out) >= limit):
            return
        page = 1
        while True:
            url = (f"{self.PC_API}/share/sharepage/detail?pr=UCBrowser&fr=pc"
                   f"&pwd_id={pwd_id}&stoken={quote(stoken)}&pdir_fid={pdir_fid}"
                   f"&force=0&_page={page}&_size=50&_sort=file_type:asc,file_name:asc")
            r = requests.get(url, headers=self._headers_common(), timeout=10)
            r.encoding = "utf-8"
            data = r.json()
            items = (data.get("data") or {}).get("list") or []
            if not items:
                break
            for it in items:
                if it.get("dir"):
                    self._walk(pwd_id, stoken, it.get("fid", "0"), out, depth + 1, limit)
                elif it.get("file") and it.get("category") in (1, 2):
                    out.append({"fid": it.get("fid", ""),
                                "file_name": it.get("file_name", "未命名"),
                                "size": it.get("size", 0),
                                "share_fid_token": it.get("share_fid_token", ""),
                                "pwd_id": pwd_id, "stoken": stoken})
                if limit and len(out) >= limit:
                    return
            if len(items) < 50:
                break
            page += 1


    def download_url_anon(self, pwd_id, fid, fid_token):

        try:
            stoken = self._get_stoken(pwd_id) or ""
        except Exception:
            stoken = ""
        body = {"fids": [fid], "fids_token": [fid_token], "pwd_id": pwd_id,
                "stoken": stoken, "speedup_session": ""}
        url = f"{self.PC_API}/file/download?pr=UCBrowser&fr=pc"
        text = self._post_json(url, body, self._headers_anon())
        data = json.loads(text)
        arr = data.get("data") or []
        if not arr:
            return ""
        return arr[0].get("download_url", "") or ""

    def play_anonymous(self, pwd_id, fid, fid_token):
"
        dl = self.download_url_anon(pwd_id, fid, fid_token)
        if not dl:
            return {"parse": 0, "url": "", "header": self._headers_anon()}
        return {"parse": 0, "url": dl,
                "header": {"User-Agent": PC_UA, "Accept-Encoding": "identity", "Referer": dl + "\\"}}

    def stream_alive(self, dl, timeout=6):

        if not dl:
            return False
        try:
            r = requests.get(dl, headers={"User-Agent": PC_UA, "Accept-Encoding": "identity",
                                          "Referer": dl + "\\", "Range": "bytes=0-0"},
                             stream=True, timeout=timeout)
            ok = r.status_code in (200, 206)
            r.close()
            return ok
        except Exception:
            return False


class QuarkDrive:
    PC_API = "https://drive-pc.quark.cn/1/clouddrive"
    SHARE_RE = re.compile(r"https?://pan\.quark\.cn/s/([0-9a-zA-Z]+)(?:\?pwd=(\w+))?")

    DL_PR = "pc"

    def __init__(self, cookie=""):
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": PC_UA})
        self._stoken_cache = {}

    def _headers(self):
        h = {"Referer": "https://pan.quark.cn", "User-Agent": PC_UA}
        if self.cookie:
            h["Cookie"] = self.cookie
        return h

    def cookie_header(self):

        parts = []
        ck = getattr(self.session, "cookies", None)
        try:
            if isinstance(ck, dict):
                parts += ["%s=%s" % (k, v) for k, v in ck.items()]
            else:
                for c in ck:
                    parts.append("%s=%s" % (c.name, c.value))
        except Exception:
            pass
        if self.cookie:
            parts.append(self.cookie)
        return "; ".join(parts)

    def _post_json(self, url, body, headers=None, timeout=20):
        hdrs = {"User-Agent": PC_UA, "Content-Type": "application/json; charset=utf-8"}
        if headers:
            hdrs.update(headers)
        resp = self.session.post(url, json=body, headers=hdrs, timeout=timeout)
        resp.encoding = "utf-8"
        return resp.text


    def share_token(self, pwd_id, passcode=""):
        url = f"{self.PC_API}/share/sharepage/token?__t={int(time.time() * 1000)}"
        body = {"pwd_id": pwd_id, "passcode": passcode or ""}
        try:
            text = self._post_json(url, body, self._headers())
            data = json.loads(text)
        except Exception:
            return {}, ""
        stoken = (data.get("data") or {}).get("stoken", "")
        if stoken:
            self._stoken_cache[pwd_id] = stoken
        return data, stoken

    def _get_stoken(self, pwd_id, passcode=""):
        if pwd_id in self._stoken_cache:
            return self._stoken_cache[pwd_id]
        _, stoken = self.share_token(pwd_id, passcode)
        return stoken

    def list_videos(self, share_url, passcode="", limit=0):
        """免登列出分享里的视频：[{'fid','file_name','size','share_fid_token','pwd_id','stoken'}]"""
        m = self.SHARE_RE.search(share_url or "")
        if not m:
            return []
        pwd_id, url_pwd = m.group(1), m.group(2)
        pc = passcode or url_pwd or ""
        try:
            stoken = self._get_stoken(pwd_id, pc)
        except Exception:
            return []
        if not stoken:
            return []
        out = []
        self._walk(pwd_id, stoken, "0", out, depth=0, limit=limit)
        return out

    def _walk(self, pwd_id, stoken, pdir_fid, out, depth, limit=0):
        if depth > 12 or (limit and len(out) >= limit):
            return
        page = 1
        while True:
            url = (f"{self.PC_API}/share/sharepage/detail?pr=ucpro&fr=pc"
                   f"&pwd_id={pwd_id}&stoken={quote(stoken)}&pdir_fid={pdir_fid}"
                   f"&force=0&_page={page}&_size=50&_sort=file_type:asc,file_name:asc")
            try:
                r = self.session.get(url, headers=self._headers(), timeout=10)
                r.encoding = "utf-8"
                data = r.json()
            except Exception:
                break
            items = (data.get("data") or {}).get("list") or []
            if not items:
                break
            for it in items:
                if it.get("dir"):
                    self._walk(pwd_id, stoken, it.get("fid", "0"), out, depth + 1, limit)
                elif it.get("file") and it.get("category") in (1, 2):
                    out.append({"fid": it.get("fid", ""),
                                "file_name": it.get("file_name", "未命名"),
                                "size": it.get("size", 0),
                                "share_fid_token": it.get("share_fid_token", ""),
                                "pwd_id": pwd_id, "stoken": stoken})
                if limit and len(out) >= limit:
                    return
            if len(items) < 50:
                break
            page += 1


    def _warm_session(self, pwd_id, stoken):

        names = set()
        ck = getattr(self.session, "cookies", None)
        try:
            if isinstance(ck, dict):
                names = set(ck.keys())
            else:
                names = {c.name for c in ck}
        except Exception:
            pass
        if "__pugs" in names:
            return
        try:
            self._walk(pwd_id, stoken, "0", [], depth=0, limit=1)
        except Exception:
            pass

    def download_info(self, pwd_id, fid, fid_token):

        try:
            stoken = self._get_stoken(pwd_id) or ""
        except Exception:
            stoken = ""
        self._warm_session(pwd_id, stoken)
        body = {"fids": [fid], "fids_token": [fid_token], "pwd_id": pwd_id, "stoken": stoken}
        url = f"{self.PC_API}/file/download?pr={self.DL_PR}&fr=pc"
        try:
            text = self._post_json(url, body, self._headers())
            data = json.loads(text)
        except Exception:
            return {}
        arr = data.get("data") or []
        if not arr:
            return {}
        it = arr[0]
        return {"url": it.get("download_url", "") or "",
                "size": int(it.get("size") or 0),
                "name": it.get("file_name", "")}

    def download_url_anon(self, pwd_id, fid, fid_token):

        return self.download_info(pwd_id, fid, fid_token).get("url", "") or ""

    def play_anonymous(self, pwd_id, fid, fid_token):

        dl = self.download_url_anon(pwd_id, fid, fid_token)
        if not dl:
            return {"parse": 0, "url": "", "header": self._headers()}
        h = {"User-Agent": PC_UA, "Accept-Encoding": "identity", "Referer": "https://pan.quark.cn"}
        ck = self.cookie_header()
        if ck:
            h["Cookie"] = ck
        return {"parse": 0, "url": dl, "header": h}

    def stream_alive(self, dl, timeout=6):
 
        if not dl:
            return False
        h = {"User-Agent": PC_UA, "Accept-Encoding": "identity",
             "Referer": "https://pan.quark.cn", "Range": "bytes=0-0"}
        ck = self.cookie_header()
        if ck:
            h["Cookie"] = ck
        try:
            try:
                r = self.session.get(dl, headers=h, stream=True, timeout=timeout)
            except TypeError:

                r = self.session.get(dl, headers=h, timeout=timeout)
            ok = r.status_code in (200, 206)
            try:
                r.close()
            except Exception:
                pass
            return ok
        except Exception:
            return False



class LocalStreamProxy:
    _inst = None

    @classmethod
    def instance(cls):
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def __init__(self):
        self._srv = None
        self._port = 0
        self._items = {}
        self._seq = 0
        self._lock = threading.Lock()
        self.thread = 64        # 并发连接数（夸克每连接约 0.1MB/s ⇒ 64 连接≈5.4MB/s）
        self.block = 65536      # 单连接每块的字节数（长连接上顺序 Range 请求）

    # ---------- 服务端 ----------
    def _ensure_server(self):
        if self._srv is not None:
            return True
        try:
            import http.server as _hs
            import socketserver as _ss
            outer = self

            class _Handler(_hs.BaseHTTPRequestHandler):
                protocol_version = "HTTP/1.1"

                def log_message(self, *a):
                    pass

                def do_HEAD(self):
                    self.do_GET()

                def do_GET(self):
                    outer._handle(self)

            class _Server(_ss.ThreadingMixIn, _hs.HTTPServer):
                daemon_threads = True
                allow_reuse_address = True

            self._srv = _Server(("127.0.0.1", 0), _Handler)
            self._port = self._srv.server_address[1]
            threading.Thread(target=self._srv.serve_forever,
                             kwargs={"poll_interval": 0.3}, daemon=True).start()
            return True
        except Exception:
            self._srv = None
            return False

    def base_url(self):
        return "http://127.0.0.1:%d" % self._port

    def register(self, url, headers=None, size=0, refresh=None):
        """refresh：可选回调 () -> (new_url, new_headers)；夸克匿名会话 cookie 会过期（CDN 412），
        拉块失败时靠它换一条新直链续命"""
        if not url or not self._ensure_server():
            return ""
        with self._lock:
            self._seq += 1
            sid = "%08x" % ((self._seq * 2654435761) & 0xFFFFFFFF)
            self._items[sid] = {"url": url, "headers": dict(headers or {}),
                                "size": int(size or 0), "refresh": refresh}
            if len(self._items) > 96:      # 只保留最近的，防长时间运行内存涨
                for k in list(self._items.keys())[:48]:
                    self._items.pop(k, None)
        return sid

    def _total_size(self, it):
        """上游总长：从 Range: bytes=0-0 的 Content-Range 里取"""
        if it.get("size"):
            return it["size"]
        try:
            h = dict(it["headers"])
            h["Range"] = "bytes=0-0"
            r = requests.get(it["url"], headers=h, stream=True, timeout=(8, 12))
            m = re.search(r"/(\d+)\s*$", r.headers.get("Content-Range") or "")
            if m:
                it["size"] = int(m.group(1))
            ct = r.headers.get("Content-Type")
            if ct:
                it["ctype"] = ct
            try:
                r.close()
            except Exception:
                pass
        except Exception:
            pass
        return it.get("size") or 0

    @staticmethod
    def _parse_range(hdr, total):
        start, end = 0, (total - 1 if total else 0)
        if hdr:
            m = re.search(r"bytes=(\d*)-(\d*)", hdr)
            if m:
                s, e = m.group(1), m.group(2)
                if s == "" and e:
                    n = int(e)
                    start = max(0, total - n)
                    end = total - 1
                else:
                    start = int(s or 0)
                    end = int(e) if e else (total - 1 if total else start)
        if total and end >= total:
            end = total - 1
        if end < start:
            end = start
        return start, end

    # ---------- 上游拉流 ----------
    def _maybe_refresh(self, it):

        if not it.get("refresh"):
            return False
        lock = it.setdefault("_rlock", threading.Lock())
        with lock:
            if time.time() - it.get("_refreshed_at", 0) < 15:   # 刚刷新过（或别的线程刚试过）
                return bool(it.get("url"))
            it["_refreshed_at"] = time.time()
            try:
                url, headers = it["refresh"]() or ("", {})
                if url:
                    it["url"] = url
                    it["headers"] = dict(headers or {})
                    return True
            except Exception:
                pass
            return False

    def _fetch_block(self, sess, it, start, end):

        sh = int(it.get("shift") or 0)      # PNG 伪装头：上游取流整体右移 sh 字节
        want = end - start + 1
        for attempt in range(3):
            try:
                h = dict(it["headers"])
                h["Range"] = "bytes=%d-%d" % (start + sh, end + sh)
                r = sess.get(it["url"], headers=h, stream=True, timeout=(10, 30))
                if r.status_code not in (200, 206):
                    try:
                        r.close()
                    except Exception:
                        pass
                    if self._maybe_refresh(it):
                        continue          # 拿到新直链，重试这一块
                    return b""
                buf, got = [], 0
                for c in r.iter_content(65536):
                    if not c:
                        continue
                    buf.append(c)
                    got += len(c)
                    if got >= want:
                        break
                try:
                    r.close()
                except Exception:
                    pass
                if got >= want:
                    return b"".join(buf)[:want]
            except Exception:
                pass
        return b""

    def _sniff(self, it):

        if "_sniffed" in it:
            return
        it["_sniffed"] = True
        head = b""
        try:
            head = self._fetch_range(it, 0, 511) or b""
        except Exception:
            pass
        it["shift"], it["ctype"] = self._sniff_head(head, it.get("url") or "")

    @staticmethod
    def _sniff_head(head, url):

        shift, ctype = 0, ""
        if head:
            i = head.find(b"\x1a\x45\xdf\xa3", 0, 48)          # EBML → MKV
            j = head.find(b"ftyp", 0, 48)                     # MP4 box 类型（前 4 字节是 box size）
            if j >= 4 and not (8 <= int.from_bytes(head[j - 4:j], "big") <= 64):
                j = -1                                        # 伪 ftyp（box size 不合理）
            if i >= 0 and (j < 4 or i <= j - 4):
                shift, ctype = i, "video/x-matroska"
            elif j >= 4:
                shift = j - 4
                ctype = "video/quicktime" if head[j + 4:j + 6] == b"qt" else "video/mp4"
            elif head[:3] == b"FLV":
                ctype = "video/x-flv"
            elif len(head) >= 377 and head[0] == 0x47 and head[188] == 0x47 and head[376] == 0x47:
                ctype = "video/mp2t"
            elif head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
                ctype = "audio/mpeg"
        if not ctype:
            ctype = LocalStreamProxy._ext_mime(url)
        return shift, ctype

    @staticmethod
    def _ext_mime(url):

        ext = os.path.splitext((url or "").split("?")[0].lower())[1]
        return {".mp4": "video/mp4", ".mkv": "video/x-matroska", ".flv": "video/x-flv",
                ".ts": "video/mp2t", ".m3u8": "application/vnd.apple.mpegurl",
                ".avi": "video/x-msvideo", ".mov": "video/quicktime"}.get(ext, "video/mp4")

    def _fetch_range(self, it, start, end):

        sess = requests.Session()
        try:
            sess.trust_env = False
        except Exception:
            pass
        try:
            return self._fetch_block(sess, it, start, end)
        finally:
            try:
                sess.close()
            except Exception:
                pass

    def _pump(self, it, wfile, start, end):

        total = end - start + 1
        W = max(1, min(int(self.thread or 64), 128))
        B = max(32768, int(self.block or 65536))
        nblocks = (total + B - 1) // B
        if nblocks <= 0:
            return
        cond = threading.Condition()
        ready = {}
        state = {"next": 0, "stop": False}

        def worker(w):
            sess = None
            try:
                sess = requests.Session()
                sess.trust_env = False
            except Exception:
                sess = None
            try:
                idx = w
                while True:
                    with cond:
                        while not state["stop"] and idx < nblocks and idx >= state["next"] + W:
                            cond.wait(0.3)
                        if state["stop"] or idx >= nblocks:
                            break
                    s = start + idx * B
                    e = min(end, s + B - 1)
                    data = self._fetch_block(sess, it, s, e) if sess is not None else b""
                    with cond:
                        ready[idx] = data
                        cond.notify_all()
                    idx += W
            finally:
                try:
                    if sess is not None:
                        sess.close()
                except Exception:
                    pass

        for w in range(min(W, nblocks)):
            threading.Thread(target=worker, args=(w,), daemon=True).start()
        try:
            while True:
                with cond:
                    while (state["next"] < nblocks and state["next"] not in ready
                           and not state["stop"]):
                        cond.wait(0.3)
                    if state["stop"] or state["next"] >= nblocks:
                        break
                    idx = state["next"]
                    data = ready.pop(idx)
                    state["next"] = idx + 1
                    cond.notify_all()
                if not data:
                    break
                wfile.write(data)
                wfile.flush()
        except Exception:
            pass
        finally:
            with cond:
                state["stop"] = True
                cond.notify_all()

    # ---------- 请求处理 ----------
    def _handle(self, handler):
        try:
            path = handler.path.split("?")[0].strip("/")
            parts = path.split("/")
            if len(parts) != 2 or parts[0] not in ("s", "probe"):
                handler.send_response(404)
                handler.send_header("Content-Length", "0")
                handler.end_headers()
                return
            mode, sid = parts
            with self._lock:
                it = self._items.get(sid)
            if not it:
                handler.send_response(404)
                handler.send_header("Content-Length", "0")
                handler.end_headers()
                return
            if mode == "probe":      # 连通性自检（只拉 256B，验证上游+代理都通；大了白等起播）
                body = self._fetch_range(it, 0, 255)
                handler.send_response(200 if body else 502)
                handler.send_header("Content-Type", "application/octet-stream")
                handler.send_header("Content-Length", str(len(body)))
                handler.end_headers()
                if body:
                    handler.wfile.write(body)
                return
            self._sniff(it)      # 真实格式 + PNG 伪装头偏移（扩展名不可信）
            total = self._total_size(it) - int(it.get("shift") or 0)
            if total <= 0:
                handler.send_response(502)
                handler.send_header("Content-Length", "0")
                handler.end_headers()
                return
            start, end = self._parse_range(handler.headers.get("Range"), total)
            length = end - start + 1
            has_range = bool(handler.headers.get("Range"))
            handler.send_response(206 if has_range else 200)
            handler.send_header("Content-Type", it.get("ctype") or self._ext_mime(it.get("url") or ""))
            handler.send_header("Accept-Ranges", "bytes")
            handler.send_header("Content-Length", str(length))
            if has_range:
                handler.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, total))
            handler.end_headers()
            self._pump(it, handler.wfile, start, end)
        except Exception:
            try:
                handler.send_response(500)
                handler.send_header("Content-Length", "0")
                handler.end_headers()
            except Exception:
                pass


class Pan123:
    SHARE_RE = re.compile(r"https?://(?:www\.)?(?:123pan|123684|123865|123912|123592)\.(?:com|cn)/s/([\w\-]+)")

    def _headers(self):
        return {"referer": "https://www.123pan.com", "origin": "https://www.123pan.com",
                "platform": "open_platform", "user-agent": DART_UA, "app-version": "3"}

    def _parse(self, share_url):
        m = self.SHARE_RE.search(share_url or "")
        if not m:
            return "", ""
        key = m.group(1)
        if key.endswith(".html"):
            key = key[:-5]
        pwd = ""
        pm = re.search(r"[?&](?:pwd|SharePwd)=(\w+)", share_url or "")
        if pm:
            pwd = pm.group(1)
        return key, pwd

    def list_videos(self, share_url):

        key, pwd = self._parse(share_url)
        if not key:
            return []
        out = []
        self._walk(key, pwd, 0, out, depth=0)
        return out

    def _walk(self, key, pwd, parent_id, out, depth):
        if depth > 12:
            return
        page = 1
        while True:
            url = (f"https://www.123pan.cn/b/api/share/get?limit=100&Page={page}&next=-1"
                   f"&orderBy=file_name&orderDirection=asc&parentFileId={parent_id}"
                   f"&shareKey={key}&SharePwd={pwd}")
            r = requests.get(url, headers=self._headers(), timeout=15)
            r.encoding = "utf-8"
            try:
                data = r.json()
            except Exception:
                break
            items = ((data.get("data") or {}).get("InfoList")) or []
            if not items:
                break
            for it in items:
                cat = it.get("Category", -1)
                name = it.get("FileName", "")
                if cat == 2 or name.lower().endswith(VIDEO_EXT):
                    out.append({"file_id": it.get("FileId", ""),
                                "file_name": name or "未命名",
                                "size": it.get("Size", 0),
                                "etag": it.get("Etag", ""),
                                "s3key": it.get("S3KeyFlag", ""),
                                "download_url": it.get("DownloadUrl", "")})
                elif it.get("Type") == 1 or it.get("Type") == 0 and not it.get("DownloadUrl"):
                    self._walk(key, pwd, it.get("FileId", 0), out, depth + 1)
            if len(items) < 100:
                break
            page += 1

    @staticmethod
    def play_direct(download_url):
        u = (download_url or "").replace("_24_24", "")
        u = u.replace("&cache_type=1&w=24&h=24&trade_key=123pan-thumbnail&type=video", "")
        return {"parse": 0, "url": u,
                "header": {"referer": "https://www.123pan.com", "origin": "https://www.123pan.com",
                           "platform": "android", "user-agent": DART_UA, "app-version": "3"}}



SITES = [
    {"id": "木偶",  "name": "木偶", "type": "webshare",
     "site": ["https://123.666291.xyz", "https://666.666291.xyz",
              "https://www.muou.site", "https://www.muou.asia"]},
     {"id": "玩偶",  "name": "玩偶", "type": "wogg",
     "site": ["https://www.wogg.net", "https://wogg.xxooo.cf", "https://woggpan.xxooo.cf"]},
    {"id": "多多",  "name": "多多", "type": "webshare",
     "site": ["https://tv.yydsys.top", "https://tv.yydsys.cc", "https://tv.214521.xyz"]},
    {"id": "欧歌",  "name": "欧歌", "type": "webshare",
     "site": ["https://woog.nxog.eu.org", "https://woog.nxog.fun", "https://woog.430520.xyz"]},
    {"id": "二小",  "name": "二小", "type": "webshare",
     "site": ["https://www.2xiaopan.top", "https://2xiaopan.top",
              "https://www.erxiaozhan.top", "https://www.2xiaozhan.top", "https://wexwp.cc"]},
    {"id": "虎斑",  "name": "虎斑", "type": "webshare", "site": ["http://38.76.197.172:16969"]},
    {"id": "快映",  "name": "快映", "type": "webshare", "site": ["http://38.76.197.172:12521"]},
    {"id": "花卷",  "name": "花卷", "type": "webshare", "site": ["https://www.hjzhencai.top"]},
    {"id": "夸父",  "name": "夸父", "type": "bbs", "site": ["https://www.kfzy.net"],
     "search_style": "path",
     "uc_cats": {"1": "9", "2": "1", "3": "4", "4": "3"},  # 电影/剧集/综艺/动漫
     "cats": [{"n": "剧集", "v": "1"}, {"n": "短剧", "v": "2"}, {"n": "动漫", "v": "3"},
              {"n": "综艺", "v": "4"}, {"n": "电影", "v": "9"}]},
    {"id": "123",   "name": "123", "type": "bbs",
     "site": ["https://123panfx.com", "https://pan1.me"],
     "search_style": "query",
     "uc_cats": {"1": "2", "2": "48", "3": "52", "4": "37"},  # 电影/剧集/综艺/动漫
     "cats": [{"n": "电影", "v": "2"}, {"n": "剧集", "v": "48"}, {"n": "4K原盘", "v": "56"},
              {"n": "综艺", "v": "52"}, {"n": "动漫", "v": "37"}]},
    {"id": "卡卡",  "name": "卡卡", "type": "kkpan", "site": ["https://www.kkpans.com"]},
    {"id": "即刻",  "name": "即刻", "type": "jike", "site": ["https://api.uuuka.com"]},
    {"id": "指南",  "name": "指南", "type": "zhinan", "site": ["https://4kzn.cc"]},
    {"id": "双星",  "name": "双星", "type": "shuangxing", "site": ["https://1.star2.cn"]},
    {"id": "爱盼",  "name": "爱盼", "type": "aipan", "site": ["https://www.aipan.me"]},
    {"id": "觅盘",  "name": "觅盘", "type": "mipan", "site": ["https://www.mipan.so"]},
    {"id": "趣盘",  "name": "趣盘", "type": "qupan", "site": ["https://b.funletu.com"]},
    {"id": "盘搜",  "name": "盘搜", "type": "pansou", "site": ["https://pansou.noisework.cn"]},
    {"id": "盘搜2", "name": "盘搜2", "type": "pansou", "site": ["https://so.252035.xyz"]},
]

FILTERS_WEBSHARE = {
    "cateId": [{"n": "电影", "v": "1"}, {"n": "剧集", "v": "2"}, {"n": "综艺", "v": "3"},
               {"n": "动漫", "v": "4"}, {"n": "纪录片", "v": "5"}, {"n": "短剧", "v": "26"}],
    "class": [{"n": "全部", "v": ""}, {"n": "Netflix", "v": "Netflix"},
              {"n": "惊悚", "v": "惊悚"}, {"n": "悬疑", "v": "悬疑"}, {"n": "剧情", "v": "剧情"},
              {"n": "灾难", "v": "灾难"}, {"n": "冒险", "v": "冒险"}, {"n": "动作", "v": "动作"},
              {"n": "科幻", "v": "科幻"}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"},
              {"n": "奇幻", "v": "奇幻"}, {"n": "恐怖", "v": "恐怖"}, {"n": "战争", "v": "战争"},
              {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "古装", "v": "古装"},
              {"n": "武侠", "v": "武侠"}, {"n": "权谋", "v": "权谋"}, {"n": "家庭", "v": "家庭"},
              {"n": "历史", "v": "历史"}, {"n": "传记", "v": "传记"}, {"n": "警匪", "v": "警匪"},
              {"n": "江湖", "v": "江湖"}, {"n": "职场", "v": "职场"}, {"n": "音乐", "v": "音乐"},
              {"n": "歌舞", "v": "歌舞"}, {"n": "运动", "v": "运动"}, {"n": "励志", "v": "励志"},
              {"n": "同xing", "v": "同xing"}, {"n": "换身", "v": "换身"}],
    "area": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"},
             {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
             {"n": "日本", "v": "日本"}, {"n": "英国", "v": "英国"}, {"n": "泰国", "v": "泰国"},
             {"n": "法国", "v": "法国"}, {"n": "印度", "v": "印度"}, {"n": "西班牙", "v": "西班牙"},
             {"n": "俄罗斯", "v": "俄罗斯"}, {"n": "加拿大", "v": "加拿大"},
             {"n": "澳大利亚", "v": "澳大利亚"}, {"n": "意大利", "v": "意大利"},
             {"n": "德国", "v": "德国"}, {"n": "其他", "v": "其他"}],
    "year": [{"n": "全部", "v": ""}] + [{"n": str(y), "v": str(y)} for y in range(2026, 1999, -1)],
    "by": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "高分好评", "v": "score"}],
}

FILTERS_WOGG = {
    "cateId": [
               {"n": "综艺", "v": "zongyi"}, {"n": "动漫", "v": "dongman"},
               {"n": "纪录片", "v": "jilupian"}],
    "class": [{"n": "全部", "v": ""}, {"n": "动作", "v": "动作"}, {"n": "喜剧", "v": "喜剧"},
              {"n": "爱情", "v": "爱情"}, {"n": "科幻", "v": "科幻"}, {"n": "恐怖", "v": "恐怖"},
              {"n": "剧情", "v": "剧情"}, {"n": "战争", "v": "战争"}, {"n": "警匪", "v": "警匪"},
              {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "奇幻", "v": "奇幻"},
              {"n": "武侠", "v": "武侠"}, {"n": "冒险", "v": "冒险"}, {"n": "枪战", "v": "枪战"},
              {"n": "悬疑", "v": "悬疑"}, {"n": "惊悚", "v": "惊悚"}, {"n": "经典", "v": "经典"},
              {"n": "青春", "v": "青春"}, {"n": "文艺", "v": "文艺"}, {"n": "古装", "v": "古装"},
              {"n": "历史", "v": "历史"}, {"n": "运动", "v": "运动"}, {"n": "纪录片", "v": "纪录片"}],
    "area": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"},
             {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "法国", "v": "法国"},
             {"n": "英国", "v": "英国"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"},
             {"n": "德国", "v": "德国"}, {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"},
             {"n": "意大利", "v": "意大利"}, {"n": "西班牙", "v": "西班牙"},
             {"n": "加拿大", "v": "加拿大"}, {"n": "其他", "v": "其他"}],
    "year": [{"n": "全部", "v": ""}] + [{"n": str(y), "v": str(y)} for y in range(2026, 1999, -1)],
    "by": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "高分好评", "v": "score"}],
}


def _abs(base, href):
    if not href:
        return ""
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base + href
    if href.startswith("http"):
        return href
    return base + "/" + href


PLAY2DETAIL_RE = re.compile(r"/(?:index\.php/)?vod/play/id/(\d+)[^\"']*")


def _to_detail_url(url):
    """苹果CMS 播放页链接 → 详情页链接"""
    m = PLAY2DETAIL_RE.search(url or "")
    if not m:
        return url
    base = url.split("/index.php")[0].split("/vod/")[0]
    return f"{base}/index.php/vod/detail/id/{m.group(1)}.html"


def _extract_pans(text):
    """从任意 HTML/JSON 文本里提取网盘链接 → {pan名: [url,...]}"""
    found = {}
    for name, rx in PAN_RES:
        for m in rx.finditer(text or ""):
            u = m.group(0).rstrip("\\\"'.,;)")
            if u not in found.setdefault(name, []):
                found[name].append(u)
    return found


# ----- 苹果CMS 模板（webshare / wogg） -----
def maccms_categories(site):
    if site["type"] == "wogg":
        return FILTERS_WOGG["cateId"]
    return FILTERS_WEBSHARE["cateId"]


CAT_ALIASES = {
    "1":  ("电影", "影片"),
    "2":  ("剧集", "电视剧", "连续剧"),
    "3":  ("综艺", "娱乐"),
    "4":  ("动漫", "动画", "卡通"),
    "5":  ("纪录片", "纪录"),
    "26": ("短剧", "微短剧"),
}
_CAT_SKIP_PREFIX = ("更多", "全部", "查看", "首页")


def webshare_type_map(site):

    if "_typemap" in site:
        return site["_typemap"]
    tmap = None
    try:
        _ensure_url(site)
        pairs = []
        for path in ("/", "/index.php/vod/show/id/1.html"):
            try:
                html = http_get(site["session"], site["url"] + path, timeout=8)
            except Exception:
                continue
            if BeautifulSoup is not None:
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.select("a[href*='/vod/type/id/'], a[href*='/vod/show/id/']"):
                    m = re.search(r"/id/(\d+)", a.get("href", ""))
                    name = (a.get("title") or a.get_text(strip=True) or "").strip()
                    if m and name:
                        pairs.append((m.group(1), name))
            else:
                for m in re.finditer(r'<a[^>]*href="[^"]*/vod/(?:type|show)/id/(\d+)[^"]*"[^>]*>(.*?)</a>',
                                     html, re.S):
                    name = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                    if name:
                        pairs.append((m.group(1), name))
            if pairs:
                break
        clean, seen = [], set()
        for rid, name in pairs:
            name = name.replace("\xa0", "").replace("&nbsp;", "").strip()
            if not name or name.startswith(_CAT_SKIP_PREFIX) or (rid, name) in seen:
                continue
            seen.add((rid, name))
            clean.append((rid, name))
        if clean:
            tmap = {}
            for std, aliases in CAT_ALIASES.items():
                for rid, name in clean:  # 页面顺序，首个命中优先
                    if any(a in name for a in aliases):
                        tmap.setdefault(std, rid)
                        break
            if not tmap:

                ids = {rid for rid, _ in clean}
                if {"1", "2", "3", "4"} <= ids:
                    tmap = {"1": "1", "2": "2", "3": "3", "4": "4"}
    except Exception:
        tmap = None
    site["_typemap"] = tmap
    return tmap


def resolve_webshare_cat(site, std_id):

    tmap = webshare_type_map(site)
    if tmap is None:
        return str(std_id)  # 探测失败，退回旧行为
    return tmap.get(str(std_id))


def maccms_category_url(site, cat_id, pg, extend):
    extend = extend or {}
    cls = quote(extend.get("class", "") or "")
    area = quote(extend.get("area", "") or "")
    year = extend.get("year", "") or ""
    by = extend.get("by", "") or ""
    if site["type"] == "wogg":
        # 标准 vodshow 位序：id-area-by-class-lang-letter-level-page-year
        return f"{site['url']}/vodshow/{cat_id}-{area}-{by}-{cls}-----{pg}---{year}.html"
    if cls or area or year or by:
        # 苹果CMS 命名段路由，空段省略（实测有效），规范顺序 area/by/class/id/page/year
        u = f"{site['url']}/index.php/vod/show"
        if area:
            u += f"/area/{area}"
        if by:
            u += f"/by/{by}"
        if cls:
            u += f"/class/{cls}"
        u += f"/id/{cat_id}/page/{pg}"
        if year:
            u += f"/year/{year}"
        return u + ".html"
    return f"{site['url']}/index.php/vod/show/id/{cat_id}/page/{pg}.html"


def maccms_parse_list(site, html):
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    vods = []
    for item in soup.select(".module-item"):
        link = item.select_one(".module-item-pic a") or item.select_one("a")
        if link is None and item.name == "a" and item.get("href"):
            link = item  # 花卷等模板：.module-item 直接挂在 <a> 上
        title = item.select_one(".module-item-title") or item.select_one(".module-poster-item-title")
        pic = item.select_one(".module-item-pic img") or item.select_one("img")
        remark = item.select_one(".module-item-text") or item.select_one(".module-item-note")
        if link and (title or link.get("title")):
            vods.append({
                "vod_id": _to_detail_url(_abs(site["url"], link.get("href", ""))),
                "vod_name": (title.get_text(strip=True) if title else "") or link.get("title", ""),
                "vod_pic": (pic.get("data-src") or pic.get("data-original") or pic.get("src")) if pic else "",
                "vod_remarks": remark.get_text(strip=True) if remark else "",
            })
    if not vods:  # wogg 布局差异兜底
        for item in soup.select(".module-card-item, .module-search-item, .module-items .module-item"):
            link = item.select_one("a")
            pic = item.select_one("img")
            if link and link.get("href"):
                name = link.get("title") or (pic.get("alt") if pic else "") or link.get_text(strip=True)
                vods.append({"vod_id": _to_detail_url(_abs(site["url"], link["href"])),
                             "vod_name": name,
                             "vod_pic": (pic.get("data-src") or pic.get("src")) if pic else "",
                             "vod_remarks": ""})
    return vods


def maccms_category(site, tid, pg, extend):
    cat_id = (extend or {}).get("cateId") or maccms_categories(site)[0]["v"]
    if site["type"] == "webshare":
        cat_id = resolve_webshare_cat(site, cat_id)
        if cat_id is None:
            return []  # 该站没有这个分类（如木偶无短剧），不再错显其他内容
    html = http_get(site["session"], maccms_category_url(site, cat_id, pg, extend or {}))
    return maccms_parse_list(site, html)


def maccms_search(site, key, pg):
    if site["type"] == "wogg":
        url = f"{site['url']}/vodsearch/-------------.html?wd={quote(key)}&submit="
        html = http_get(site["session"], url)
        return maccms_parse_list(site, html)
    url = f"{site['url']}/index.php/vod/search/page/{pg}/wd/{quote(key)}.html"
    html = http_get(site["session"], url)
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    vods = []
    for card in soup.select(".module-search-item"):
        link = card.select_one("a")
        title = card.select_one("h3") or card.select_one(".module-item-title")
        pic = card.select_one("img")
        remark = card.select_one(".video-info-aux") or card.select_one(".module-item-text")
        if link and title:
            vods.append({
                "vod_id": _to_detail_url(_abs(site["url"], link.get("href", ""))),
                "vod_name": title.get_text(strip=True),
                "vod_pic": (pic.get("data-src") or pic.get("src")) if pic else "",
                "vod_remarks": remark.get_text(strip=True) if remark else "",
            })
    if not vods:
        vods = maccms_parse_list(site, html)
    return vods


def maccms_detail_pans(site, detail_url):
    """从详情页提取各网盘分享链接"""
    html = http_get(site["session"], _to_detail_url(detail_url), timeout=10)
    found = {}
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        for row in soup.select(".module-row-text"):
            link_elem = row.select_one("[data-clipboard-text]")
            if link_elem:
                url = link_elem.get("data-clipboard-text", "")
                for name, rx in PAN_RES:
                    if rx.search(url):
                        found.setdefault(name, [])
                        if url not in found[name]:
                            found[name].append(url)
    if not found:  # 兜底：整页正则
        found = _extract_pans(html)
    return found, html


# ----- 卡卡（kkpans API） -----
def kkpan_search(site, key, pg):
    url = f"{site['url']}/api/resources/public?page={pg}&limit=24&search={quote(key)}"
    data = json.loads(http_get(site["session"], url))
    return [{"vod_id": f"kk:{it.get('id')}",
             "vod_name": it.get("file_name", ""),
             "vod_pic": "",
             "vod_remarks": str(round((it.get("file_size") or 0) / 1073741824, 1)) + "G"}
            for it in (data.get("data") or [])]


def kkpan_category(site, tid, pg, extend):
    url = f"{site['url']}/api/resources/public?page={pg}&limit=24"
    data = json.loads(http_get(site["session"], url))
    return [{"vod_id": f"kk:{it.get('id')}",
             "vod_name": it.get("file_name", ""),
             "vod_pic": "",
             "vod_remarks": (it.get("created_at") or "")[:10]}
            for it in (data.get("data") or [])]


def kkpan_detail(site, real_id):
    rid = real_id.split(":", 1)[-1]
    data = json.loads(http_get(site["session"], f"{site['url']}/api/resources/public/{rid}"))
    d = data.get("data") or {}
    pans = {}
    link = d.get("share_link", "")
    if link:
        for name, rx in PAN_RES:
            if rx.search(link):
                pans[name] = [link]
    if not pans:
        pans = _extract_pans(json.dumps(d, ensure_ascii=False))
    return pans, d.get("description", "") or d.get("file_name", "")


# ----- 即刻（uuuka API） -----
def jike_search(site, key, pg):
    data = json.loads(http_get(site["session"], f"{site['url']}/api/search?keyword={quote(key)}"))
    items = ((data.get("data") or {}).get("items")) or []
    return [{"vod_id": it.get("source_link", ""),
             "vod_name": re.sub(r"</?em>", "", it.get("title", "")),
             "vod_pic": "",
             "vod_remarks": it.get("update_time", "")[:16]}
            for it in items if it.get("source_link")]


def pansou_search(site, key, pg):
    data = json.loads(http_get(site["session"], f"{site['url']}/api/search?kw={quote(key)}"))
    mbt = ((data.get("data") or {}).get("merged_by_type")) or {}
    vods = []
    for it in (mbt.get("uc") or [])[:30]:
        if it.get("password"):
            continue  # 带提取码的免登解不了，跳过
        u = (it.get("url") or "").strip()
        if "drive.uc.cn/s/" not in u:
            continue
        vods.append({"vod_id": u, "vod_name": (it.get("note") or u).strip(),
                     "vod_pic": "", "vod_remarks": "UC免登"})
    return vods


def jike_category(site, tid, pg, extend):
    data = json.loads(http_get(site["session"], f"{site['url']}/api/contents/?page={pg}"))
    items = ((data.get("data") or {}).get("items")) or []
    return [{"vod_id": it.get("source_link", ""),
             "vod_name": re.sub(r"</?em>", "", it.get("title", "")),
             "vod_pic": "",
             "vod_remarks": it.get("update_time", "")[:16]}
            for it in items if it.get("source_link")]


# ----- 趣盘（funletu API） -----
def qupan_search(site, key, pg):
    body = {"keyword": key, "categoryid": 0, "filetypeid": 1, "courseid": 1,
            "page": pg, "pageSize": 15, "sortBy": "sort", "order": "desc", "offset": 0}
    r = site["session"].post(f"{site['url']}/search", json=body, timeout=8,
                             headers={"Origin": "https://b.funletu.com",
                                      "Referer": "https://b.funletu.com/search"})
    data = r.json()
    if data.get("code") != 200:
        return []
    vods = []
    for it in ((data.get("data") or {}).get("list") or []):
        u = it.get("url", "")
        if not u:
            continue
        vods.append({"vod_id": u,
                     "vod_name": re.sub(r"</?em>", "", it.get("title", "")),
                     "vod_pic": "",
                     "vod_remarks": it.get("updatetime", "")})
    return vods


# ----- 爱盼（aipan API） -----
def aipan_search(site, key, pg):
    data = json.loads(http_get(site["session"], f"{site['url']}/api/movies/search?q={quote(key)}"))
    return [{"vod_id": f"ap:{m.get('id')}",
             "vod_name": m.get("title", ""),
             "vod_pic": m.get("cover", ""),
             "vod_remarks": m.get("subtitle", "") or str(m.get("rate", ""))}
            for m in (data.get("movies") or [])]


def aipan_category(site, tid, pg, extend):
    data = json.loads(http_get(site["session"],
                               f"{site['url']}/api/movies/list?page={pg}&pageSize=30"))
    items = data.get("movies") or (data.get("data") or {}).get("movies") or []
    return [{"vod_id": f"ap:{m.get('id')}",
             "vod_name": m.get("title", ""),
             "vod_pic": m.get("cover", ""),
             "vod_remarks": str(m.get("rate", ""))}
            for m in items]


def aipan_detail(site, real_id):
    rid = real_id.split(":", 1)[-1]
    data = json.loads(http_get(site["session"], f"{site['url']}/api/movies/detail/{rid}"))
    pans = {}
    for pl in (data.get("panLinks") or []):
        u = pl.get("url") or pl.get("link") or ""
        if u:
            for name, rx in PAN_RES:
                if rx.search(u):
                    pans.setdefault(name, [])
                    if u not in pans[name]:
                        pans[name].append(u)
    if not pans:
        pans = _extract_pans(json.dumps(data, ensure_ascii=False))
    return pans, data.get("synopsis", "")


# ----- 觅盘（mipan，已换 PanSou 系后端，需 token） -----
def _mipan_token(site):
    if site.get("_token"):
        return site["_token"]
    try:
        r = site["session"].get(f"{site['url']}/api/token", timeout=5)
        d = r.json()
        site["_token"] = d.get("token") or (d.get("data") or {}).get("token", "")
    except Exception:
        site["_token"] = ""
    return site["_token"]


def mipan_search(site, key, pg):
    token = _mipan_token(site)
    if not token:
        return []
    # 新后端关键字参数是 kw（旧的 keyword 被忽略会返回全站 dump）；
    # 结果是 {"data": {"total": N, "merged_by_type": {uc: [...], "123": [...], ...}}}
    r = site["session"].post(f"{site['url']}/api/search",
                             json={"kw": key, "page": pg},
                             headers={"x-mipan-token": token}, timeout=8)
    data = r.json()
    d = data.get("data") or {}
    if isinstance(d, list):  # 旧版扁平列表兜底
        pairs = [(None, it) for it in d]
    else:
        mbt = d.get("merged_by_type") or {}
        pairs = [(typ, it) for typ, arr in mbt.items() for it in (arr or [])]
    vods, seen = [], set()
    for typ, it in pairs:
        if not isinstance(it, dict):
            continue
        raw = it.get("url") or it.get("link") or ""
        pwd = it.get("password") or ""
        u, pan = "", ""
        for name, rx in PAN_RES:
            m = rx.search(raw)
            if m:
                u, pan = m.group(0), name
                break
        if pan not in ("UC", "123"):
            continue  # 其余网盘需登录转存，免登播不了，不出
        if pan == "UC" and pwd and "?pwd=" not in u:
            u += f"?pwd={pwd}"  # 提取码并进链接，下游 UC 解析/验播都认
        if u in seen:
            continue
        seen.add(u)
        title = re.sub(r"</?em>", "", it.get("note") or it.get("title") or it.get("name") or "")
        vods.append({"vod_id": u, "vod_name": title.strip() or u, "vod_pic": "",
                     "vod_remarks": (it.get("datetime") or it.get("time") or "")[:16]})
        if len(vods) >= 30:
            break
    return vods


# ----- 指南（wordpress） -----
ZHINAN_CATS = [{"n": "最新", "v": "zuixin"}, {"n": "电影", "v": "dianying"},
               {"n": "剧集", "v": "juji"}, {"n": "TOP250", "v": "top250"}]


def zhinan_category(site, tid, pg, extend):
    cat = (extend or {}).get("cateId") or "zuixin"
    url = f"{site['url']}/books/{cat}" + (f"/page/{pg}" if pg > 1 else "")
    html = http_get(site["session"], url)
    return _wp_parse(site, html)


def zhinan_search(site, key, pg):
    html = http_get(site["session"], f"{site['url']}/?s={quote(key)}" + (f"&paged={pg}" if pg > 1 else ""))
    return _wp_parse(site, html)


def _wp_parse(site, html):
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    vods = []
    for a in soup.select("a[href*='/book']"):
        href = a.get("href", "")
        if not re.search(r"/book[^/]*/\d+[^/]*\.html$|/books?/\d+", href):
            continue
        img = a.select_one("img")
        title = a.get("title") or (img.get("alt") if img else "") or a.get_text(strip=True)
        if not title or len(title) < 2:
            continue
        vods.append({"vod_id": _abs(site["url"], href), "vod_name": title,
                     "vod_pic": (img.get("src") or img.get("data-src")) if img else "",
                     "vod_remarks": ""})
    seen, out = set(), []
    for v in vods:
        if v["vod_id"] not in seen:
            seen.add(v["vod_id"])
            out.append(v)
    return out


# ----- 双星（star2.cn） -----
def shuangxing_search(site, key, pg):
    html = http_get(site["session"], f"{site['url']}/search/?keyword={quote(key)}&page={pg}")
    return _html_link_parse(site, html)


def shuangxing_category(site, tid, pg, extend):
    html = http_get(site["session"], f"{site['url']}/?page={pg}")
    return _html_link_parse(site, html)


def _html_link_parse(site, html):
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    vods, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("javascript", "#", "mailto")):
            continue
        title = a.get_text(strip=True)
        if not title or len(title) < 4:
            img = a.find("img")
            title = (img.get("alt") or "") if img else ""
        if not title or len(title) < 4:
            continue
        full = _abs(site["url"], href)
        if full in seen or full.rstrip("/") == site["url"]:
            continue
        seen.add(full)
        img = a.find("img")
        vods.append({"vod_id": full, "vod_name": title[:80],
                     "vod_pic": (img.get("src") or img.get("data-src")) if img else "",
                     "vod_remarks": ""})
    return vods[:60]


# ----- Xiuno BBS 论坛站（夸父 / 123分享，移植自 PanWebShareKF/PanWebShare123） -----
BBS_REPLY_TEXTS = ["感谢楼主分享！", "这个资源太棒了！", "已收藏，谢谢！",
                   "不错的资源，支持一下", "楼主辛苦了！", "内容很有用，感谢分享"]
ALERT_SEL = ("div.message > div > div.alert, div.message > div.alert, "
             "div.message > section > div.alert, div.message > h5 > div.alert")


def _bbs_headers(site):
    h = {"Referer": site["url"], "Accept-Language": "zh-CN,zh;q=0.9"}
    h.update(site.get("extra_headers") or {})
    return h


def bbs_category(site, tid, pg, extend):
    cat = (extend or {}).get("cateId") or site["cats"][0]["v"]
    html = http_get(site["session"], f"{site['url']}/forum-{cat}-{pg}.htm",
                    headers=_bbs_headers(site))
    return _bbs_parse(site, html)


def bbs_search(site, key, pg):
    if site.get("search_style") == "path":
        url = f"{site['url']}/search-{quote(key)}-{pg}.htm"
    else:
        url = f"{site['url']}/search.htm?keyword={quote(key)}&page={pg}"
    html = http_get(site["session"], url, headers=_bbs_headers(site))
    return _bbs_parse(site, html)


def _bbs_parse(site, html):
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    vods = []
    for li in soup.select("ul.threadlist > li"):
        if (li.select_one("i") or {}).get("data-placement", "") == "top" if li.select_one("i") else False:
            continue
        a = li.select_one("div > div.subject > a, div > div.style3_subject > a")
        if not a:
            continue
        title = a.get_text(strip=True)
        if not title or "福利" in title:
            continue
        img = li.select_one("a > img")
        pic = img.get("src", "") if img else ""
        if pic and not pic.startswith("http"):
            pic = site["url"] + "/" + pic.lstrip("/")
        vods.append({"vod_id": _abs(site["url"], a.get("href", "")),
                     "vod_name": title, "vod_pic": pic, "vod_remarks": ""})
    return vods[:60]


def _bbs_unlock_and_fetch(site, page_url):
    """回复解锁隐藏内容后返回页面 HTML（无 cookie 时直接返回原页）"""
    html = http_get(site["session"], page_url, timeout=15, headers=_bbs_headers(site))
    if not site.get("extra_headers") or "<立即回复>" not in html:
        return html
    m = re.search(r"thread-(\d+)", page_url)
    if not m:
        return html
    import random
    body = {"doctype": "1", "return_html": "0", "quotepid": "",
            "message": random.choice(BBS_REPLY_TEXTS), "quick_reply_message": "4"}
    h = _bbs_headers(site)
    h["X-Requested-With"] = "XMLHttpRequest"
    try:
        site["session"].post(f"{site['url']}/post-create-{m.group(1)}-1.htm",
                             data=body, headers=h, timeout=15)
        html = http_get(site["session"], page_url, timeout=15, headers=_bbs_headers(site))
    except Exception:
        pass
    return html


def page_detail_pans(site, page_url):
    html = _bbs_unlock_and_fetch(site, page_url)
    text = html
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        alerts = soup.select(ALERT_SEL)
        if alerts:
            parts = []
            for al in alerts:
                for a in al.select("a[href]"):
                    href = a.get("href", "")
                    if "/s/" in href or "/t/" in href:
                        parts.append(href + " " + al.get_text(" ", strip=True))
                parts.append(al.get_text(" ", strip=True))
            text = "\n".join(parts) or html
    # 链接+提取码合并为 ?pwd=
    text = re.sub(r"(https?://[^\s\"'<>]+)[\s\S]{0,30}?提取码[\s:：]*([a-zA-Z0-9]{4})",
                  lambda mm: mm.group(1) + "?pwd=" + mm.group(2), text)
    return _extract_pans(text), html


# ---------------------------------------------------------------------------
# 聚合 Spider
# ---------------------------------------------------------------------------
class Spider(Spider):
    def getDependence(self):
        return []

    def init(self, extend=""):
        try:
            ext = json.loads(extend) if isinstance(extend, str) and extend else (extend or {})
        except Exception:
            ext = {}
        self.uc = UCDrive(ext.get("uc_cookie", "") or ext.get("cookie", ""))
        self.quark = QuarkDrive(ext.get("quark_cookie", "") or ext.get("cookie", ""))
        self.pan123 = Pan123()
        # mode："" = 聚合模式；"uc" = UC免登专站；"quark" = 夸克免登专站；
        #        "uc,quark"（也认 "uc+quark" / "uc quark" / "pan"）= UC+夸克双模式专站
        # 按分隔符切成独立词再精确匹配，避免子串误命中（如 "uck" 误开 UC）
        tokens = {x for x in str(ext.get("mode", "")).lower()
                  .replace("+", ",").replace("，", ",").replace(" ", ",").split(",") if x}
        self.mode_pans = set()
        if tokens & {"uc", "pan"}:
            self.mode_pans.add("UC")
        if tokens & {"quark", "pan"}:
            self.mode_pans.add("夸克")
        self.pan_only = bool(self.mode_pans)           # 免登专站（UC 或 UC+夸克）
        self.fast_filter = str(ext.get("fast", "1")) == "1"  # 仅聚合模式"仅UC免登"筛选用；免登专站搜索/推荐恒为强检测
        # 夸克游客直链被服务端按"单连接"限速（实测恒定 0.10MB/s；并发线性叠加：
        # 16→1.2、32→2.4、64→4.6、96→6.5、128→9.2 MB/s），所以用本地并发代理把
        # 单连接限速叠成多连接。accel=0 完全走裸直链；accel_thread 调并发数。
        self.accel_on = str(ext.get("accel", "1")).strip().lower() not in ("0", "false", "no", "off")
        self.proxy = LocalStreamProxy.instance()
        try:
            self.proxy.thread = max(1, min(128, int(ext.get("accel_thread", "96") or 96)))
        except Exception:
            self.proxy.thread = 96
        self._play_cache = {}  # UC/夸克链接有效性缓存 {url: (可播, 时间戳, TTL)}
        self._slow_cache = {}  # 直链"是否被限速"判定缓存 {url: (slow, 时间戳)}
        self._link_cache = {}  # 详情页UC/夸克链接缓存 {real_id: ({kind: [url,...]}, 时间戳)}
        self.sites = {}
        for s in SITES:
            inst = dict(s)
            inst["session"] = make_session()
            ck = ext.get(f"{s['id']}cookie", "")
            if s["type"] == "bbs" and ck:
                inst["extra_headers"] = {"Cookie": ck}
            inst["url"] = s["site"][0]  # 先用首个镜像，真正请求时才懒探测
            self.sites[s["id"]] = inst

    def getName(self):
        if self.mode_pans == {"UC"}:
            return "UC免登"
        if self.mode_pans == {"夸克"}:
            return "夸克免登"
        if self.mode_pans:
            return "UC+夸克免登"
        return "网盘"

    # ---------- UC免登专站：有效性验证 ----------
    UC_SRC = ["木偶", "玩偶", "多多", "欧歌", "二小", "花卷", "虎斑", "快映", "夸父", "123", "卡卡"]
    SEARCH_TIMEOUT = 10  # 搜索/分类取候选总时限（秒），慢站直接放弃不再拖全局
    VERIFY_TIMEOUT = 12  # 统一验播时限（秒），时限内验出多少算多少

    @staticmethod
    def _site_dead(site):
        """熔断：探测/请求失败过的站，5 分钟内直接跳过（防止死站每次都拖满超时）"""
        return time.time() < site.get("_dead_until", 0)

    @staticmethod
    def _mark_dead(site, secs=300):
        site["_dead_until"] = time.time() + secs

    def _uc_playable(self, url):
        """强检测：分享未过期 + 能匿名展开出视频 + 匿名直链可取 + CDN 头探测可连。
        可播缓存 6h；不可播只缓存 10 分钟（防网络抖动误杀后长期消失）"""
        ent = self._play_cache.get(url)
        if ent and time.time() - ent[1] < (ent[2] if len(ent) > 2 else 6 * 3600):
            return ent[0]
        ok = False
        try:
            items = self.uc.list_videos(url, limit=1)
            if items:
                it = items[0]
                dl = self.uc.download_url_anon(it["pwd_id"], it["fid"], it["share_fid_token"])
                ok = bool(dl) and self.uc.stream_alive(dl)
        except Exception:
            ok = False
        self._play_cache[url] = (ok, time.time(), 6 * 3600 if ok else 600)
        return ok

    def _quark_playable(self, url):
        """夸克强检测（与 UC 完全对称）：分享未过期 + 匿名展开出视频 + 匿名直链可取 + CDN 头探测可连。
        可播缓存 6h；不可播只缓存 10 分钟（防网络抖动误杀后长期消失）"""
        ent = self._play_cache.get(url)
        if ent and time.time() - ent[1] < (ent[2] if len(ent) > 2 else 6 * 3600):
            return ent[0]
        ok = False
        try:
            items = self.quark.list_videos(url, limit=1)
            if items:
                it = items[0]
                dl = self.quark.download_url_anon(it["pwd_id"], it["fid"], it["share_fid_token"])
                # 不再多跑一次 CDN 头探测：播放时代理有 412 自愈刷新兜底，这里省 ~0.5-1s/候选
                ok = bool(dl)
        except Exception:
            ok = False
        self._play_cache[url] = (ok, time.time(), 6 * 3600 if ok else 600)
        return ok

    def _playable(self, url, kind):
        """按网盘类型走对应的强检测"""
        return self._quark_playable(url) if kind == "夸克" else self._uc_playable(url)

    def _vod_pan_links(self, site, real_id):
        """取某条目的 UC / 夸克 分享链接（30 分钟缓存）=> {"UC":[...], "夸克":[...]}"""
        ent = self._link_cache.get(real_id)
        if ent and time.time() - ent[1] < 1800:
            return ent[0]
        try:
            t = site["type"]
            if t in ("pansou", "mipan", "qupan", "jike"):
                # 链接型站点：vod_id 本身就是分享链接，直接判类型即可，别再当网页去抓
                links = {"UC": [], "夸克": []}
                for kind, rx in PAN_RES:
                    if kind in ("UC", "夸克") and rx.search(real_id):
                        links[kind].append(real_id)
            elif t == "kkpan":
                pans, _ = kkpan_detail(site, real_id)
                links = {"UC": pans.get("UC") or [], "夸克": pans.get("夸克") or []}
            elif t in ("webshare", "wogg"):
                pans, _ = maccms_detail_pans(site, real_id)
                links = {"UC": pans.get("UC") or [], "夸克": pans.get("夸克") or []}
            elif t == "aipan":
                pans, _ = aipan_detail(site, real_id)
                links = {"UC": pans.get("UC") or [], "夸克": pans.get("夸克") or []}
            else:
                pans, _ = page_detail_pans(site, real_id)
                links = {"UC": pans.get("UC") or [], "夸克": pans.get("夸克") or []}
        except Exception:
            links = {"UC": [], "夸克": []}
        self._link_cache[real_id] = (links, time.time())
        return links

    def _verify_pan(self, site, vods, check_play=True, kinds=("UC",)):
        """只留带（UC/夸克）免登链接的条目；check_play 时进一步验证分享未过期能播"""
        def work(v):
            all_links = self._vod_pan_links(site, v["vod_id"])
            links = []
            for k in kinds:
                links += all_links.get(k) or []
            if not links:
                return False
            if not check_play:
                return True
            # 逐网盘类型试：任一类型能播即算可播
            for k in kinds:
                for u in (all_links.get(k) or [])[:2]:
                    if self._playable(u, k):
                        return True
            return False
        with ThreadPoolExecutor(max_workers=16) as ex:
            keep = list(ex.map(work, vods))
        return [v for v, k in zip(vods, keep) if k]

    def _verify_uc(self, site, vods, check_play=True):
        """只留带 UC 链接的条目；check_play 时进一步验证分享未过期能播"""
        return self._verify_pan(site, vods, check_play=check_play, kinds=("UC",))

    def _verify_mixed(self, vods, check_play=True, timeout=VERIFY_TIMEOUT, workers=16):
        """跨站统一验 UC（vods 需带 _sid0 标记站源）。
        旧做法是每个站各自起一个线程池顺序验，慢站会把整轮拖满；
        这里全候选共享一个池 + 全局时限，as_completed 先验完先出，超时直接收尾"""
        out = []
        kinds = tuple(sorted(self.mode_pans)) if self.mode_pans else ("UC",)
        # 每条候选的强检测次数随网盘类型数线性增长（每类型最多试 2 条链接），
        # 双模式时限同步放大，避免验不完被整体超时砍掉、结果偏少
        timeout = timeout * max(1, len(kinds))
        def work(v):
            site = self.sites.get(v.get("_sid0", ""))
            if not site:
                return None
            try:
                all_links = self._vod_pan_links(site, v["vod_id"])
                links = []
                for k in kinds:
                    links += all_links.get(k) or []
                if not links:
                    return None
                if not check_play:
                    return v
                for k in kinds:
                    for u in (all_links.get(k) or [])[:2]:
                        if self._playable(u, k):
                            return v
                return None
            except Exception:
                return None
        ex = ThreadPoolExecutor(max_workers=workers)
        try:
            futs = [ex.submit(work, v) for v in vods]
            for f in as_completed(futs, timeout=timeout):
                try:
                    r = f.result()
                    if r is not None:
                        out.append(r)
                except Exception:
                    pass
        except Exception:
            pass  # as_completed 超时抛 TimeoutError，已验出的照出
        finally:
            ex.shutdown(wait=False)
        return out

    def isVideoFormat(self, url):
        return url.lower().endswith(VIDEO_EXT)

    def manualVideoCheck(self):
        return False

    def localProxy(self, params):
        return []

    # ---------- 主页：UC专站=内容分类；聚合=18站胶囊，maccms系带完整筛选 ----------
    UC_CLASSES = [{"type_id": "UC首页", "type_name": "推荐"},
                  {"type_id": "1", "type_name": "电影"}, {"type_id": "2", "type_name": "剧集"},
                  {"type_id": "3", "type_name": "综艺"}, {"type_id": "4", "type_name": "动漫"},
                  {"type_id": "5", "type_name": "纪录片"}, {"type_id": "26", "type_name": "短剧"}]
    # UC 专站分类 → 玩偶(wogg) 的 slug 映射
    WOGG_CAT_MAP = {"1": "dianying", "2": "juji", "3": "zongyi",
                    "4": "dongman", "5": "jilupian", "26": "duanjv"}

    def _maccms_filter_rows(self, site=None):
        f = FILTERS_WOGG if (site and site["type"] == "wogg") else FILTERS_WEBSHARE
        return [{"key": "cateId", "name": "分类", "value": f["cateId"]},
                {"key": "by", "name": "排序", "value": f["by"]},
                {"key": "class", "name": "类型", "value": f["class"]},
                {"key": "area", "name": "地区", "value": f["area"]},
                {"key": "year", "name": "年份", "value": f["year"]}]

    def homeContent(self, filter):
        if self.pan_only:
            res = {"class": self.UC_CLASSES}
            if filter:
                rows = [r for r in self._maccms_filter_rows() if r["key"] != "cateId"]
                res["filters"] = {c["type_id"]: rows for c in self.UC_CLASSES if c["type_id"] != "UC首页"}
            return res
        classes = []
        for s in SITES:
            classes.append({"type_id": s["id"], "type_name": s["name"]})
        res = {"class": classes}
        if filter:
            filters = {}
            for s in SITES:
                if s["type"] in ("webshare", "wogg"):
                    rows = self._maccms_filter_rows(s)
                    rows.append({"key": "uc", "name": "资源",
                                 "value": [{"n": "全部", "v": "0"}, {"n": "仅UC免登", "v": "1"}]})
                    rows.append({"key": "quark", "name": "夸克",
                                 "value": [{"n": "不限", "v": "0"}, {"n": "仅夸克免登", "v": "1"}]})
                    filters[s["id"]] = rows
                elif s["type"] == "bbs" and s.get("cats"):
                    filters[s["id"]] = [{"key": "cateId", "name": "分类", "value": s["cats"]}]
                elif s["type"] == "zhinan":
                    filters[s["id"]] = [{"key": "cateId", "name": "分类", "value": ZHINAN_CATS}]
            res["filters"] = filters
        return res

    def homeVideoContent(self):
        return {"list": []}

    # ---------- 分类：UC专站按内容分类并行聚合；聚合模式按站点分发 ----------
    def _uc_fetch_site(self, site, tid, pg, extend):
        """单站取一页分类（UC专站用），wogg 走 slug 映射；UC首页 不设 cateId 用站点默认"""
        if self._site_dead(site):
            return site, []
        _ensure_url(site)
        if self._site_dead(site):
            return site, []
        try:
            t = site["type"]
            if t in ("webshare", "wogg"):
                ext = dict(extend or {})
                if str(tid) in self.WOGG_CAT_MAP:
                    ext["cateId"] = self.WOGG_CAT_MAP[str(tid)] if t == "wogg" else str(tid)
                else:
                    ext.pop("cateId", None)
                vods = maccms_category(site, tid, pg, ext)
            elif t == "kkpan":
                vods = kkpan_category(site, tid, pg, extend or {})
            else:
                return site, []
        except Exception:
            self._mark_dead(site)
            vods = []
        return site, vods[:12]

    def categoryContent(self, tid, pg, filter, extend):
        if self.pan_only:
            pool = [self.sites[i] for i in self.UC_SRC if i in self.sites]
            # 推荐/内容分类统一全站并行拉取（推荐旧版轮流单站 → 整页只有木偶一家，已改）
            # 推荐页各站交叉混排，第 1 屏就是多来源；分类页保持原顺序
            ex = ThreadPoolExecutor(max_workers=max(1, len(pool)))
            futs = [ex.submit(self._uc_fetch_site, s, tid, pg, {} if tid == "UC首页" else extend)
                    for s in pool]
            buckets, vods = [], []
            try:
                done, _ = wait(futs, timeout=self.SEARCH_TIMEOUT)
                for f in done:
                    try:
                        site, vs = f.result()
                        for v in vs:
                            v["_sid0"] = site["id"]
                        if vs:
                            buckets.append(vs)
                    except Exception:
                        pass
            finally:
                ex.shutdown(wait=False)
            if tid == "UC首页":
                while buckets:
                    rest = []
                    for b in buckets:
                        vods.append(b.pop(0))
                        if b:
                            rest.append(b)
                    buckets = rest
            else:
                for b in buckets:
                    vods.extend(b)
            if not vods:
                return {"list": [], "page": int(pg or 1), "pagecount": 1, "limit": 90, "total": 0}
            # 跨站统一验播：共享线程池 + 全局时限，先验完先出，慢站不再拖满整轮
            # 分类/推荐首载全冷（链接缓存、验播缓存都空），16 线程 × 12s 验不完 → 首屏空、要手动刷新；
            # 这里把并发提到 32，时限按候选数自适应（封顶 20s），首载一次出齐
            vt = min(20, max(self.VERIFY_TIMEOUT, len(vods) // 6))
            ok_vods = self._verify_mixed(vods, check_play=True, timeout=vt, workers=32)
            for v in ok_vods:
                sid = v.pop("_sid0", "")
                v["vod_id"] = f"{sid}@{v['vod_id']}"
                v["vod_remarks"] = f"{sid} | {v.get('vod_remarks', '')}".strip(" |")
            return {"list": ok_vods, "page": int(pg or 1), "pagecount": 999, "limit": 90, "total": 999999}
        site = self.sites.get(tid)
        if not site:
            return {"list": []}
        _ensure_url(site)
        try:
            t = site["type"]
            if t in ("webshare", "wogg"):
                vods = maccms_category(site, tid, pg, extend or {})
            elif t == "kkpan":
                vods = kkpan_category(site, tid, pg, extend or {})
            elif t == "jike":
                vods = jike_category(site, tid, pg, extend or {})
            elif t == "aipan":
                vods = aipan_category(site, tid, pg, extend or {})
            elif t == "zhinan":
                vods = zhinan_category(site, tid, pg, extend or {})
            elif t == "shuangxing":
                vods = shuangxing_category(site, tid, pg, extend or {})
            elif t == "bbs":
                vods = bbs_category(site, tid, pg, extend or {})
            else:
                vods = []
        except Exception:
            vods = []
        # "仅UC免登"筛选：默认只查有无 UC 链接（快）；fast=0 时逐条试播（准但慢）
        ext = extend or {}
        if site["type"] in ("webshare", "wogg", "kkpan") and vods:
            if str(ext.get("uc")) == "1":
                vods = self._verify_pan(site, vods, check_play=not self.fast_filter, kinds=("UC",))
            if str(ext.get("quark")) == "1":
                vods = self._verify_pan(site, vods, check_play=not self.fast_filter, kinds=("夸克",))
        for v in vods:
            v["vod_id"] = f"{site['id']}@{v['vod_id']}"
        return {"list": vods, "page": pg, "pagecount": 999, "limit": 90, "total": 999999}

    # ---------- 搜索：一次搜全部站，带总时限，慢站直接放弃 ----------
    def _site_search(self, site, key, pg):
        """按站点类型分发搜索（不验证、不标记）"""
        t = site["type"]
        if t in ("webshare", "wogg"):
            return maccms_search(site, key, pg)
        if t == "kkpan":
            return kkpan_search(site, key, pg)
        if t == "jike":
            return jike_search(site, key, pg)
        if t == "aipan":
            return aipan_search(site, key, pg)
        if t == "qupan":
            return qupan_search(site, key, pg)
        if t == "pansou":
            return pansou_search(site, key, pg)
        if t == "mipan":
            return mipan_search(site, key, pg)
        if t == "zhinan":
            return zhinan_search(site, key, pg)
        if t == "shuangxing":
            return shuangxing_search(site, key, pg)
        if t == "bbs":
            return bbs_search(site, key, pg)
        return []

    def searchContent(self, key, quick, pg="1"):
        if self.pan_only:
            # UC专站搜索：全部站点都搜，候选统一过 UC 强检测（检测本身不变），结果不去重。
            # 先并行只取候选，再共享线程池限时验播：慢站不再把整轮拖满还被整体丢弃
            def fetch(site):
                if self._site_dead(site):
                    return []
                _ensure_url(site)
                try:
                    vods = self._site_search(site, key, pg)
                except Exception:
                    self._mark_dead(site)
                    vods = []
                for v in vods[:12]:
                    v["_sid0"] = site["id"]
                return vods[:12]
            cands = self._run_parallel(list(self.sites.values()), fetch, self.SEARCH_TIMEOUT)
            ok = self._verify_mixed(cands, check_play=True, timeout=self.VERIFY_TIMEOUT)  # 强检测：只留真能播的
            for v in ok:
                sid = v.pop("_sid0", "")
                v["vod_id"] = f"{sid}@{v['vod_id']}"
                v["vod_remarks"] = f"{sid} | {v.get('vod_remarks', '')}".strip(" |")
            return {"list": ok}
        def do(site):
            if self._site_dead(site):
                return []
            _ensure_url(site)
            try:
                vods = self._site_search(site, key, pg)
                for v in vods:
                    v["vod_id"] = f"{site['id']}@{v['vod_id']}"
                    v["vod_remarks"] = f"{site['id']} | {v.get('vod_remarks', '')}".strip(" |")
                return vods
            except Exception:
                self._mark_dead(site)
                return []
        return {"list": self._run_parallel(list(self.sites.values()), do, self.SEARCH_TIMEOUT)}

    @staticmethod
    def _run_parallel(items, fn, timeout):
        """并行执行 fn(item)，timeout 秒内没收完的慢任务直接丢弃"""
        merged = []
        ex = ThreadPoolExecutor(max_workers=max(1, len(items)))
        try:
            futs = [ex.submit(fn, it) for it in items]
            done, _ = wait(futs, timeout=timeout)
            for f in done:
                try:
                    merged.extend(f.result())
                except Exception:
                    pass
        finally:
            ex.shutdown(wait=False)
        return merged

    # ---------- 详情：通用网盘链接提取 + UC/123 展开 ----------
    def detailContent(self, array):
        if not array:
            return {"list": []}
        vod_id = array[0]
        if "@" not in vod_id:
            # 推送的原始分享链接：直接当网盘链接展开（UC/123 免登直链）
            pans = {}
            for name, rx in PAN_RES:
                if rx.search(vod_id):
                    pans[name] = [vod_id]
            if not pans:
                # 非网盘直链：照 jar 的 Push 站，给 直连/嗅探/解析 三条线路
                return {"list": [{"vod_id": vod_id, "vod_name": vod_id, "vod_pic": "",
                                  "vod_play_from": "直连$$$嗅探$$$解析",
                                  "vod_play_url": f"播放${vod_id}$$$播放${vod_id}$$$播放${vod_id}"}]}
            return {"list": [self._build_vod(vod_id, vod_id, "", "", pans)]}
        sid, real_id = vod_id.split("@", 1)
        site = self.sites.get(sid)
        if not site:
            return {"list": []}
        _ensure_url(site)
        try:
            t = site["type"]
            if t in ("webshare", "wogg"):
                pans, raw_html = maccms_detail_pans(site, real_id)
                soup = BeautifulSoup(raw_html, "html.parser") if BeautifulSoup else None
                title = (soup.select_one("h1") or soup.select_one("title")).get_text(strip=True) if soup else ""
                pic = ""
                content = ""
                if soup:
                    img = soup.select_one(".module-item-pic img") or soup.select_one(".video-cover img")
                    if img:
                        pic = img.get("data-src") or img.get("src", "")
                    info = soup.select_one(".module-info-introduction-content") or soup.select_one(".vod_content")
                    content = info.get_text(strip=True) if info else ""
            elif t == "kkpan":
                pans, content = kkpan_detail(site, real_id)
                title, pic = content, ""
            elif t == "aipan":
                pans, content = aipan_detail(site, real_id)
                title, pic = "", ""
            elif t in ("jike", "qupan", "mipan", "pansou"):
                pans = {}
                for name, rx in PAN_RES:
                    if rx.search(real_id):
                        pans[name] = [real_id]
                title, pic, content = real_id, "", ""
            else:  # bbs / zhinan / shuangxing：详情页通用正则
                pans, raw_html = page_detail_pans(site, real_id)
                title, pic, content = "", "", ""
                if BeautifulSoup is not None:
                    soup = BeautifulSoup(raw_html, "html.parser")
                    h = soup.select_one("h4") or soup.select_one("h1") or soup.select_one("title")
                    title = h.get_text(strip=True) if h else ""
                    if "权限不足" in raw_html or "立即登录" in raw_html:
                        content = f"该站点需要登录账号，请在 ext 中配置 {sid}cookie"
            if not pans:
                return {"list": [{"vod_id": vod_id, "vod_name": title or sid,
                                  "vod_play_from": "提示",
                                  "vod_play_url": "未找到网盘链接$none"}]}
            return {"list": [self._build_vod(vod_id, title, pic, content, pans)]}
        except Exception:
            return {"list": []}

    # ---------- 选集显示名：跟随剧名 + 集数 + 清晰度 + 文件大小 ----------
    @staticmethod
    def _fmt_size(sz):
        try:
            sz = int(sz or 0)
        except Exception:
            sz = 0
        if sz >= 1073741824:
            return f"{sz / 1073741824:.1f}G"
        if sz > 0:
            return f"{sz / 1048576:.0f}M"
        return ""

    _EP_NUM_RES = [
        re.compile(r"[Ss]\d{1,2}[Ee](\d{1,3})"),      # S01E06
        re.compile(r"\b[Ee][Pp]?(\d{1,3})\b"),        # E06 / EP06
        re.compile(r"第\s*(\d{1,3})\s*[集期话回]"),     # 第6集
        re.compile(r"^(\d{1,3})[ ._\-]"),             # 01 4K / 06.xxx
        re.compile(r"\[(\d{1,3})\]"),                 # [06]
    ]

    def _ep_suffix(self, fname, size=0, name=""):
        """剧集显示名后缀：清晰度 + 体积（" 1080p · 1.2G"）；名字里已有清晰度就不重复加"""
        base = re.sub(r"\.[a-zA-Z0-9]{2,4}$", "", fname or "").strip() or ""
        mq = re.search(r"4320p|2160p|1080p|720p|[48][Kk]", base)
        q = ""
        if mq:
            q = {"2160P": "4K", "4320P": "8K"}.get(mq.group(0).upper(), mq.group(0))
        sfx = (" " + q) if (q and q not in (name or "")) else ""
        sz = self._fmt_size(size)
        if sz:
            sfx += f" · {sz}"
        me = re.search(r"\.([a-zA-Z0-9]{2,4})$", (fname or "").strip())
        if me:
            sfx += f" · {me.group(1).upper()}"     # 文件格式上屏（MKV/MP4…）
        return sfx

    def _ep_display(self, title, fname, idx, size=0, num=None):
        """选集上屏名 = 这一条线路里的序号（1..N，按文件列表顺序）。
        ★ 桌面壳会把名字【末尾的数字】当集数渲染，所以上屏名只给序号，
          不再拼体积/清晰度/扩展名：
          - 原来拼成"择日飞升 09 · 706M · MP4"，末尾是 MP4 → 12 集全显示成 4；
          - 用文件名里的真集号时（夸克分享叫 S01E87…）会显示 87..103，
            用户反馈"夸克的还是不对"，故统一用线路内序号。
        ★ num/size 参数保留（调用方仍传），上屏不再使用。"""
        try:
            return str(int(idx))
        except Exception:
            return str(idx)

    def _ep_num(self, fname, idx):
        """从文件名认集数；认不出按序号（统一"第NN集"）"""
        base = re.sub(r"\.[a-zA-Z0-9]{2,4}$", "", fname or "").strip() or ""
        for rx in self._EP_NUM_RES:
            m = rx.search(base)
            if m:
                return int(m.group(1))
        return idx

    def _build_vod(self, vod_id, title, pic, content, pans):
        uc_lines, quark_lines, p123_lines = [], [], []
        uc_ref = []          # 主 UC 线路的【集号】序列（夸克线路按它对齐显示）
        # UC 展开（全部链接，后面按集数排序，剧情更全的排最前）
        for link in pans.get("UC", []):
            try:
                items = self.uc.list_videos(link, limit=500)
            except Exception:
                items = []
            if items:
                eps = [f"{self._ep_display(title, it['file_name'], i + 1, it.get('size'))}$"
                       f"{it['file_name']}__{it['fid']}+{it['pwd_id']}+{it['share_fid_token']}"
                       for i, it in enumerate(items)]
                uc_lines.append((len(eps), "#".join(eps)))
                nums = [self._ep_num(it["file_name"], i + 1) for i, it in enumerate(items)]
                if len(nums) > len(uc_ref):
                    uc_ref = nums
        # 夸克展开（免登直链，与 UC 同构）
        # ★ 显示名跟 UC 主线路【逐集对齐】：集号用 UC 的（"第01集"这种），
        #   清晰度/体积用夸克自己文件的（两条线路在 App 里看起来一模一样，只差体积）
        for link in pans.get("夸克", []):
            try:
                items = self.quark.list_videos(link, limit=500)
            except Exception:
                items = []
            if items:
                eps = []
                for i, it in enumerate(items):
                    num = uc_ref[i] if i < len(uc_ref) else self._ep_num(it["file_name"], i + 1)
                    lb = self._ep_display(title, it["file_name"], i + 1, it.get("size"), num=num)
                    eps.append(f"{lb}$Q~{it['file_name']}__{it['fid']}+{it['pwd_id']}"
                               f"+{it['share_fid_token']}")
                quark_lines.append((len(eps), "#".join(eps)))
        # 123 展开（免登直链）
        for link in pans.get("123", []):
            try:
                items = self.pan123.list_videos(link)
            except Exception:
                items = []
            if items:
                eps = []
                for i, it in enumerate(items):
                    pid = (f"{it['file_name']}__{it['file_id']}+{it['etag']}+{it['s3key']}"
                           f"+{it['size']}+{quote(it['download_url'], safe='')}")
                    eps.append(f"{self._ep_display(title, it['file_name'], i + 1, it.get('size'))}${pid}")
                p123_lines.append((len(eps), "#".join(eps)))
        play_from, play_url = [], []
        # 集数多的线路排前面（剧情更全），线路名带集数
        for i, (cnt, urls) in enumerate(sorted(uc_lines, key=lambda x: -x[0])):
            play_from.append(f"UC无限{cnt}集#{i + 1}")
            play_url.append(urls)
        for i, (cnt, urls) in enumerate(sorted(quark_lines, key=lambda x: -x[0])):
            play_from.append(f"夸克无限{cnt}集#{i + 1}")
            play_url.append(urls)
        for i, (cnt, urls) in enumerate(sorted(p123_lines, key=lambda x: -x[0])):
            play_from.append(f"123云盘{cnt}集#{i + 1}")
            play_url.append(urls)
        # 百度/迅雷/天翼/阿里/移动 均需登录转存，不支持免登直链，直接不出线路
        if not play_from:
            play_from, play_url = ["提示"], ["UC/夸克/123分享已失效（或仅有百度等需登录网盘），请返回换一条$none"]
        return {"vod_id": vod_id, "vod_name": title, "vod_pic": pic, "vod_content": content,
                "vod_play_from": "$$$".join(play_from), "vod_play_url": "$$$".join(play_url)}

    # ---------- 播放：夸克（直链 + 单连接限速加速） ----------
    def _slow_link(self, url, headers, probe=98304, budget=0.35):
        """探这条直链是不是被限速：96KB 用时 > 0.35s 即视为慢（游客直链约 1s）
        ★ 判定结果缓存 30 分钟：否则 CDN 缓存命中会让第二次探测变快、误判成"不慢"，
          于是播放器又拿到裸直链（还是 0.1MB/s），等于加速时有时无。"""
        ent = self._slow_cache.get(url)
        if ent and time.time() - ent[1] < 1800:
            return ent[0]
        slow = True   # 默认按"慢"处理：探测失败/异常状态时走代理更稳，裸直链 0.1MB/s 必卡死
        try:
            h = dict(headers)
            h["Range"] = "bytes=0-%d" % (probe - 1)
            t0 = time.time()
            r = requests.get(url, headers=h, stream=True, timeout=(6, 10))
            if r.status_code not in (200, 206):
                # 403/412 等错误页会瞬间"下载"完；不判状态码会被误当成快链，把坏裸链给播放器
                try:
                    r.close()
                except Exception:
                    pass
            else:
                got = 0
                for c in r.iter_content(32768):
                    if not c:
                        continue
                    got += len(c)
                    if got >= probe:
                        break
                try:
                    r.close()
                except Exception:
                    pass
                slow = got > 0 and (time.time() - t0) > budget
        except Exception:
            pass
        self._slow_cache[url] = (slow, time.time())
        return slow

    def _proxy_alive(self, sid, timeout=5):
        """本地代理自检：走一遍 /probe/<sid>，不通就不把代理地址给播放器。
        代理是本机无状态服务，自检通过后 5 分钟内直接信任——否则每换一集都白等一次回源探测"""
        if time.time() - getattr(self, "_proxy_ok_at", 0) < 300:
            return True
        try:
            url = "%s/probe/%s" % (self.proxy.base_url(), sid)
            s = requests.Session()
            s.trust_env = False          # 别走系统代理
            r = s.get(url, timeout=timeout, stream=True)
            ok = r.status_code == 200
            try:
                r.close()
            except Exception:
                pass
            if ok:
                self._proxy_ok_at = time.time()
            return ok
        except Exception:
            return False

    def _quark_fresh_link(self, pwd_id, fid, fid_token=None):
        """拿一条【当前匿名会话有效】的夸克直链 + 对应请求头 => (url, headers, size)。
        不给 fid_token（或已失效）时自动重列分享换新 token——实测分享 token 与匿名会话绑定，
        会话轮换后旧 token 必 403(41020)，重列是唯一可靠的刷新方式"""
        info = self.quark.download_info(pwd_id, fid, fid_token) if fid_token else {}
        if not info:
            try:
                for it in self.quark.list_videos("https://pan.quark.cn/s/%s" % pwd_id, limit=300):
                    if it.get("fid") == fid:
                        info = self.quark.download_info(pwd_id, fid, it["share_fid_token"])
                        break
            except Exception:
                pass
        dl = (info or {}).get("url") or ""
        if not dl:
            return "", {}, 0
        h = {"User-Agent": PC_UA, "Accept-Encoding": "identity",
             "Referer": "https://pan.quark.cn"}
        ck = self.quark.cookie_header()
        if ck:
            h["Cookie"] = ck
        return dl, h, int((info or {}).get("size") or 0)

    def _quark_play(self, pwd_id, fid, fid_token):
        """夸克免登播放：拿直链 → 判是否被限速 → 慢则改走本地并发代理（多连接叠加限速）
        ★ 夸克游客直链实测单连接恒定 0.10MB/s，12 连接 ≈ 1.2MB/s（对齐 jar 的 thread/chunksize 方案）
        ★ share_fid_token 与匿名会话绑定：会话换了/过期了会 403(41020)，
           这里自动重新列一次分享拿新的 token 再试
        ★ 任何异常或代理自检不过都回退裸直链，保证至少能播"""
        dl, headers, size = self._quark_fresh_link(pwd_id, fid, fid_token)
        if not dl:
            return {"parse": 0, "msg": "夸克直链获取失败，请重试或换集"}
        direct = {"parse": 0, "url": dl, "header": headers}
        if not self.accel_on:
            return direct
        try:
            # 游客直链实测恒定 0.10MB/s：无 cookie 时不必每集再探（省 ~1s），直接走并发代理；
            # 配了 quark_cookie（会员）链接快慢不一，才需要探测决定走不走代理
            if self.quark.cookie and not self._slow_link(dl, headers):
                return direct              # 本来就快，别多绕一层
            # ★ 匿名会话 cookie 会过期（CDN 412）：给代理挂刷新回调，
            #   拉块 403/412 时自动重列分享换新直链+新 cookie 续播（否则播放器永远 1Kb/s 转圈）
            refresh = lambda: self._quark_fresh_link(pwd_id, fid)[:2]
            sid = self.proxy.register(dl, headers, size, refresh=refresh)
            if not sid:
                return direct
            if not self._proxy_alive(sid):
                return direct
            return {"parse": 0, "url": "%s/s/%s" % (self.proxy.base_url(), sid),
                    "header": {"User-Agent": PC_UA}}
        except Exception:
            return direct

    # ---------- 播放：UC 三级回退 + 123 直链 ----------
    def playerContent(self, flag, play_id, vipFlags):
        # 推送直链的三条线路（对齐 jar Push 站）
        if flag == "直连":
            return {"parse": 0, "url": play_id}
        if flag == "嗅探":
            return {"parse": 1, "url": play_id}
        if flag == "解析":
            return {"parse": 2, "jx": 1, "url": play_id}
        if play_id.startswith("http"):
            # 推送的裸分享链接：UC/123 自己展开直接播，其余提示需登录
            if re.search(r"https?://drive\.uc\.cn/s/", play_id):
                try:
                    items = self.uc.list_videos(play_id)
                except Exception:
                    items = []
                if items:
                    it = items[0]
                    return self.uc.play_anonymous(it["pwd_id"], it["fid"], it["share_fid_token"])
                return {"parse": 0, "msg": "UC分享解析失败，请重试"}
            if re.search(r"https?://pan\.quark\.cn/s/", play_id):
                try:
                    items = self.quark.list_videos(play_id)
                except Exception:
                    items = []
                if items:
                    it = items[0]
                    return self._quark_play(it["pwd_id"], it["fid"], it["share_fid_token"])
                return {"parse": 0, "msg": "夸克分享解析失败，请重试"}
            if Pan123.SHARE_RE.search(play_id):
                try:
                    items = self.pan123.list_videos(play_id)
                    if items and items[0].get("download_url"):
                        return self.pan123.play_direct(items[0]["download_url"])
                except Exception:
                    pass
                return {"parse": 0, "msg": "123分享解析失败，请重试"}
            return {"parse": 0, "msg": "该网盘需登录，暂不支持免登播放"}
        if play_id.endswith(".htm") or "分享$" in flag + play_id or play_id == "none":
            return {"parse": 0, "msg": "该分享解析失败或为需登录网盘，请重试或换线路"}
        if play_id.startswith("Q~"):
            # 夸克免登：Q~name__fid+pwd_id+fid_token（与 UC 同构，仅前缀区分）
            try:
                rest = play_id[2:]
                head, pwd_id, fid_token = rest.rsplit("+", 2)
                fid = head.split("__", 1)[-1] if "__" in head else head
                rst = self._quark_play(pwd_id, fid, fid_token)
                if rst.get("url"):
                    return rst
                return {"parse": 0, "msg": "夸克无限线路获取失败，请重试或换集"}
            except Exception as e:
                return {"parse": 0, "msg": f"夸克解析失败: {e}"}
        parts = play_id.rsplit("+", 4)
        try:
            if len(parts) == 5:  # 123 云盘：name__fileId+etag+s3key+size+download_url
                dl = unquote(parts[4])
                rst = self.pan123.play_direct(dl)
                if rst.get("url"):
                    return rst
                return {"parse": 0, "msg": "123直链获取失败"}
            if len(parts) >= 3:  # UC：name__fid+pwd_id+fid_token —— 无限免登裸直链（同 jar 的 q() 无限分支）
                head, pwd_id, fid_token = parts[0], parts[1], parts[2]
                fid = head.split("__", 1)[-1] if "__" in head else head
                rst = self.uc.play_anonymous(pwd_id, fid, fid_token)
                if rst.get("url"):
                    return rst
                return {"parse": 0, "msg": "UC无限线路获取失败，请重试或换集"}
        except Exception as e:
            return {"parse": 0, "msg": f"解析失败: {e}"}
        return {"parse": 0, "msg": "无法识别的播放地址"}


if __name__ == "__main__":
    sp = Spider()
    sp.init("{}")
    home = sp.homeContent(True)
    print("胶囊站点数:", len(home["class"]))
    for c in home["class"]:
        print(" ", c["type_id"], c["type_name"])

    print("\n--- 并发搜索：凡人修仙传 ---")
    rst = sp.searchContent("凡人修仙传", True, "1")
    by_site = {}
    for v in rst["list"]:
        by_site.setdefault(v["vod_id"].split("@")[0], 0)
        by_site[v["vod_id"].split("@")[0]] += 1
    print("结果数:", len(rst["list"]), "按站:", by_site)
    if rst["list"]:
        first = rst["list"][0]
        print("第一条:", first["vod_name"], "|", first["vod_remarks"], "|", first["vod_id"][:80])
