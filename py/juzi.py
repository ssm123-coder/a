# -*- coding: utf-8 -*-
"""
橘汁（4K追剧接口，juziappcc.hzhcbkj.cn）默影视 / TVBox Python 源

  {"name": "橘汁", "type": 3, "api": "./py/橘汁.py",
   "searchable": 1, "quickSearch": 0, "filterable": 0, "ext": ""}
"""

import base64
import json
import os
import random
import ssl
import string
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_HOST = "https://juziappcc.hzhcbkj.cn"

HOST_FALLBACKS = [
    "https://juziappcc.hzhcbkj.cn",
    "http://juziappcc.hzhcbkj.cn",
    "http://juziapp.hzhcbkj.cn",
    "https://juzhi777.app",
]

SAFE_CODE = "ZU1DSFFWNENKMDYXVUQRN0ZJDUC4PQ=="
SAFE_SECRET = "OC1A06E197EF10CF3F6058CA7A803B5E"
RSA_N = ("a9f44938c0895002dc059ee05196c162a30dadafee1439c88678d29b63b9cbef"
         "87ad52a51be9fbe939238784511f69695fc14a4e075ef1dc910bdcda35f677e3"
         "09e558ad83e3949720a2a5161ffb5f21f140416bedc4120194a6b3921c3c7770"
         "a1cac5a679646290aaa406c551638a2a34fba3e2c8e6e99ba5b74538238a6b45")
RSA_E = 65537
VAPP = "3070"

ALNUM = string.ascii_letters + string.digits

CATEGORIES = [
    ("home", "推荐"),
    ("21", "电视剧"),
    ("20", "电影"),
    ("22", "综艺"),
    ("23", "动漫"),
    ("24", "短剧"),
    ("25", "直播"),
    ("26", "漫剧"),
]

SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d]


def _t(value, default=""):
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _token(length):
    return "".join(random.choice(ALNUM) for _ in range(length - 1)) + "="

def _xtime(value):
    value <<= 1
    if value & 0x100:
        value = (value ^ 0x11b) & 0xff
    return value & 0xff


def _gmul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a = _xtime(a)
        b >>= 1
    return result


def _expand_key(key):
    nk = len(key) // 4
    nr = nk + 6
    words = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    for i in range(nk, 4 * (nr + 1)):
        temp = list(words[i - 1])
        if i % nk == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[one] for one in temp]
            temp[0] ^= RCON[i // nk - 1]
        elif nk > 6 and i % nk == 4:
            temp = [SBOX[one] for one in temp]
        words.append([words[i - nk][j] ^ temp[j] for j in range(4)])
    return [sum(words[4 * r:4 * r + 4], []) for r in range(nr + 1)], nr


def _encrypt_block(block, round_keys, nr):
    state = [block[i] ^ round_keys[0][i] for i in range(16)]
    for rnd in range(1, nr + 1):
        state = [SBOX[one] for one in state]
        state = [state[(i + 4 * (i % 4)) % 16] for i in range(16)]
        if rnd != nr:
            mixed = [0] * 16
            for col in range(4):
                a = state[4 * col:4 * col + 4]
                mixed[4 * col + 0] = _gmul(a[0], 2) ^ _gmul(a[1], 3) ^ a[2] ^ a[3]
                mixed[4 * col + 1] = a[0] ^ _gmul(a[1], 2) ^ _gmul(a[2], 3) ^ a[3]
                mixed[4 * col + 2] = a[0] ^ a[1] ^ _gmul(a[2], 2) ^ _gmul(a[3], 3)
                mixed[4 * col + 3] = _gmul(a[0], 3) ^ a[1] ^ a[2] ^ _gmul(a[3], 2)
            state = mixed
        state = [state[i] ^ round_keys[rnd][i] for i in range(16)]
    return bytes(state)


def aes_ecb(key, data):
    """AES-256-ECB + PKCS7，对应 host.aesEcbEncrypt(keyFmt=utf8, outFmt=base64)。"""
    raw = key.encode("utf-8")
    pad = 16 - len(data) % 16
    data = data + bytes([pad]) * pad
    round_keys, nr = _expand_key(raw)
    out = bytearray()
    for start in range(0, len(data), 16):
        out += _encrypt_block(data[start:start + 16], round_keys, nr)
    return bytes(out)


def aes_b64(key, plain):
    return base64.b64encode(aes_ecb(key, plain.encode("utf-8"))).decode("ascii")


def rsa_b64(data):
    n = int(RSA_N, 16)
    k = (n.bit_length() + 7) // 8
    msg = data.encode("utf-8")
    padding = bytearray()
    while len(padding) < k - 3 - len(msg):
        byte = os.urandom(1)[0]
        if byte:
            padding.append(byte)
    block = b"\x00\x02" + bytes(padding) + b"\x00" + msg
    cipher = pow(int.from_bytes(block, "big"), RSA_E, n)
    return base64.b64encode(cipher.to_bytes(k, "big")).decode("ascii")

def _varint(value):
    out = bytearray()
    value = int(value)
    while True:
        byte = value & 0x7f
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _f_str(no, value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return _varint(no * 8 + 2) + _varint(len(raw)) + raw


def _f_int(no, value):
    return _varint(no * 8) + _varint(value)


def pb_fields(data):
    out = {}
    pos = 0
    total = len(data)

    def read_var():
        nonlocal pos
        result = 0
        shift = 0
        while pos < total and shift < 70:
            byte = data[pos]
            pos += 1
            result += (byte & 127) << shift
            if not byte & 128:
                return result
            shift += 7
        return result

    while pos < total:
        tag = read_var()
        no = tag >> 3
        wire = tag & 7
        if no == 0:
            break
        if wire == 0:
            out.setdefault(no, []).append(read_var())
        elif wire == 2:
            length = read_var()
            if length < 0 or pos + length > total:
                break
            out.setdefault(no, []).append(data[pos:pos + length])
            pos += length
        elif wire == 5:
            pos += 4
        elif wire == 1:
            pos += 8
        else:
            break
    return out


def _first(fields, no):
    values = fields.get(no)
    return values[0] if values else None


def _text(value):
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return value.decode("utf-8", "replace")


def _str(fields, no):
    return _text(_first(fields, no))


def _int(fields, no, default=0):
    value = _first(fields, no)
    return default if value is None else int(value)


def _cover(seg):
    if not seg:
        return ""
    fields = pb_fields(seg)
    url = _str(fields, 2)
    return url or _str(fields, 1)


def _strip(text):
    import re
    out = str(text or "").replace("<br/>", "\n").replace("<br>", "\n")
    out = re.sub(r"<[^>]*>", "", out)
    out = (out.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
              .replace("&nbsp;", " ").replace("&amp;", "&"))
    return out.strip()

def _build_body(params, ts):
    kv = "&".join("%s=%s" % (key, params[key]) for key in params)
    r8 = _token(8)
    fake = _token(20)
    encrypted = aes_b64(SAFE_CODE, kv + str(ts))
    merged = r8 + encrypted
    return (_f_str(1, merged[:20]) + _f_str(2, merged[20:]) + _f_str(3, fake)
            + _f_int(4, ts) + _f_str(5, r8))


def _public_params(ts, r16):
    params = {
        "country": "CN", "vName": "3.0.7.0",
        "cpuId": "Qualcomm%20Technologies%2C%20Inc%20MSM8998",
        "young": 0, "facturer": "samsung", "pkg": "com.asjdhjhd.mgd.p3",
        "uuid": "3342CF6E5B34747029419DBA6B159A35", "resolution": "720x1280",
        "mac": "00%3Adb%3A1e%3A1b%3Aa8%3Ae8", "abid": "4365", "model": "SM-N9700",
        "plat": "android", "udid": "3342CF6E5B34747029419DBA6B159A35", "dpi": "320",
        "net": "1", "lang": "zh", "brand": "samsung", "density": "2.0",
        "appName": "%E6%A9%98%E6%B1%81", "cpu": "x86_64", "chid": "10000",
        "carrier": "%E7%A7%BB%E5%8A%A8", "v": "1", "tenantId": "",
        "_vOsCode": "28", "vOs": "9", "vApp": VAPP, "device": "0",
        "androidID": "f00b0e69983f85a9", "timestamp": ts, "random_str": r16,
    }
    params["sig"] = rsa_b64(str(ts) + r16 + VAPP)
    sig_aes = aes_b64(SAFE_SECRET, str(ts) + r16)
    params["sig2"] = sig_aes[:8]
    params["sig3"] = sig_aes[8:]
    return json.dumps(params, ensure_ascii=False, separators=(",", ":"))


class Spider(object):
    def __init__(self):
        self.host = DEFAULT_HOST
        self._ssl_ctx = None

    def init(self, extend=""):
        ext = _t(extend)
        if ext.startswith("http"):
            self.host = ext.rstrip("/")
        elif ext.startswith("{"):
            try:
                cfg = json.loads(ext)
                if isinstance(cfg, dict) and _t(cfg.get("host")):
                    self.host = _t(cfg.get("host")).rstrip("/")
            except Exception:
                pass
        return None

    def _ctx(self):
        if self._ssl_ctx is None:
            try:
                self._ssl_ctx = ssl.create_default_context()
            except Exception:
                self._ssl_ctx = ssl._create_unverified_context()
        return self._ssl_ctx

    def _post(self, base, path, params, body):
        ts = int(time.time() * 1000)
        r16 = _token(16)
        query = urllib.parse.urlencode(params)
        headers = {
            "publicParams": _public_params(ts, r16),
            "Content-Type": "application/x-protobuf",
            "Accept": "application/x-protobuf",
            "User-Agent": "okhttp/3.12.1",
        }
        req = urllib.request.Request(base + path + "?" + query, data=body,
                                     headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25, context=self._ctx()) as resp:
                return resp.getcode(), resp.read()
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, exc.read()
            except Exception:
                return exc.code, b""
        except Exception:
            try:
                ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                    return resp.getcode(), resp.read()
            except urllib.error.HTTPError as exc:
                return exc.code, b""
            except Exception:
                return 0, b""

    def _call(self, path, params, raw_params=None):
        ts = int(time.time() * 1000)
        body = _build_body(params, ts)
        query_params = raw_params if raw_params is not None else params
        hosts = [self.host] + [one for one in HOST_FALLBACKS if one != self.host]
        for base in hosts:
            code, payload = self._post(base, path, query_params, body)
            if code == 200 and payload:
                self.host = base
                return payload
        return b""

    @staticmethod
    def _unwrap(body):
        if not body:
            return {"error": "接口没有返回内容"}
        if body.lstrip()[:1] == b"{":
            try:
                data = json.loads(body.decode("utf-8", "replace"))
            except Exception:
                return {"error": "接口返回的数据无法解析"}
            return {"error": _t(data.get("message") or data.get("msg") or "接口报错")}
        fields = pb_fields(body)
        code = _int(fields, 1, -1)
        if code != 200:
            return {"error": _str(fields, 2) or ("请求失败(%s)" % code)}
        return {"data": _first(fields, 3) or b""}

    def _api(self, path, params, kind):
        payload = self._call(path, params)
        result = self._unwrap(payload)
        if "error" in result:
            return result
        data = result.get("data") or b""
        if not data:
            return {"error": "接口没有返回数据"}
        if kind == "list":
            fields = pb_fields(data)
            return {"items": [pb_fields(seg) for seg in fields.get(1, [])]}
        return {"fields": pb_fields(data)}

    @staticmethod
    def _video(fields):
        vid = _int(fields, 3)
        name = _str(fields, 5)
        if not vid or not name:
            return None
        return {
            "vod_id": str(vid),
            "vod_name": name,
            "vod_pic": _cover(_first(fields, 2)),
            "vod_remarks": _str(fields, 13),
            "vod_year": _str(fields, 14),
            "vod_area": _str(fields, 1),
            "vod_actor": _str(fields, 12),
            "vod_director": _str(fields, 7),
            "vod_content": _strip(_str(fields, 4)),
        }

    def _video_list(self, raw):
        out = []
        for fields in raw:
            item = self._video(fields)
            if item:
                out.append(item)
        return out

    def homeContent(self, filter=False):
        return {"class": [{"type_id": tid, "type_name": name} for tid, name in CATEGORIES]}

    def homeVideoContent(self):
        result = self._api("/api/proto/v5/drama/search",
                           {"page": "1", "pagesize": "20"}, "list")
        return {"list": self._video_list(result.get("items") or [])}

    def categoryContent(self, tid, pg, filter=False, extend=None):
        page = int(pg) if str(pg).isdigit() else 1
        if not tid or tid == "home":
            items = self.homeVideoContent().get("list") or []
            return {"list": items, "page": page, "pagecount": 1,
                    "limit": len(items), "total": len(items)}
        result = self._api("/api/proto/v5/drama/category",
                           {"typeId1": tid, "page": str(page), "pagesize": "20"}, "list")
        items = self._video_list(result.get("items") or [])
        more = len(items) >= 20
        return {
            "list": items,
            "page": page,
            "pagecount": page + 1 if more else page,
            "limit": len(items),
            "total": page * 20 if more else (page - 1) * 20 + len(items),
        }

    def searchContent(self, key, quick=False, pg="1"):
        page = int(pg) if str(pg).isdigit() else 1
        result = self._api("/api/proto/v5/drama/search",
                           {"page": str(page), "pagesize": "20", "searchKeys": _t(key)}, "list")
        items = self._video_list(result.get("items") or [])
        more = len(items) >= 20
        return {"list": items, "page": page,
                "pagecount": page + 1 if more else page,
                "limit": len(items), "total": page * 20 if more else (page - 1) * 20 + len(items)}


    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) else ids
        vid = _t(vid)
        if not vid:
            return {"list": []}
        result = self._api("/api/proto/v5/drama/getDetail", {"id": vid}, "detail")
        fields = result.get("fields") or {}
        videos = fields.get(29) or []
        if not videos:
            return {"list": []}

        groups = {}
        order = []
        for seg in videos:
            vf = pb_fields(seg)
            source = _str(vf, 9) or _str(vf, 11) or "default"
            path = _str(vf, 4)
            if not path:
                continue
            if source not in groups:
                groups[source] = {"name": _str(vf, 10) or source, "eps": []}
                order.append(source)
            ep = _int(vf, 13)
            name = _str(vf, 2)
            if not name or name.isdigit():
                name = ("第%d集" % ep) if ep > 0 else "正片"
            groups[source]["eps"].append({
                "name": name,
                "s": source,
                "p": path,
            })

        play_from = []
        play_url = []
        for source in order:
            group = groups[source]
            if not group["eps"]:
                continue
            label = group["name"] or source
            if label in play_from:
                label = "%s-%d" % (label, len(play_from))
            entries = []
            for ep in group["eps"]:
                entries.append("%s$%s" % (ep["name"], _b64e({"s": source, "p": ep["p"]})))
            play_from.append(label)
            play_url.append("#".join(entries))

        if not play_from:
            return {"list": []}

        item = {
            "vod_id": vid,
            "vod_name": _str(fields, 9),
            "vod_pic": _cover(_first(fields, 2)),
            "vod_remarks": _str(fields, 26),
            "vod_year": _str(fields, 18),
            "vod_area": _str(fields, 1),
            "vod_actor": _str(fields, 25),
            "vod_director": _str(fields, 12),
            "vod_content": _strip(_str(fields, 6)),
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url),
        }
        return {"list": [item]}

    def playerContent(self, flag, id, vipFlags=None):
        header = {"User-Agent": "okhttp/3.12.1"}
        try:
            payload = _b64d(_t(id))
        except Exception:
            return {"parse": 0, "url": "", "header": header}
        source = _t(payload.get("s"))
        path = _t(payload.get("p"))
        if not source or not path:
            return {"parse": 0, "url": "", "header": header}

        params = {"vodPlayFrom": source, "playUrl": urllib.parse.quote(path, safe="")}
        raw = {"vodPlayFrom": source, "playUrl": path}
        result = self._api("/api/proto/v5/videoUsableUrl", params, "url")
        if "error" in result:
            return {"parse": 0, "url": "", "header": header}
        fields = result.get("fields") or {}
        url = _str(fields, 1)
        if not url.startswith("http"):
            return {"parse": 0, "url": "", "header": header}
        return {"parse": 0, "url": url, "header": header}


def _b64e(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "zj:" + base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64d(text):
    raw = text[3:] if text.startswith("zj:") else text
    raw += "=" * (-len(raw) % 4)
    return json.loads(base64.urlsafe_b64decode(raw.encode("utf-8")).decode("utf-8"))
