# -*- coding: utf-8 -*-
"""
抖音直播爬虫 V3 - 修复版
修复问题：
1. 移除无法生效的性别筛选（抖音API不返回性别字段）
2. 优化在线人数显示
3. 改进筛选逻辑
"""
import re
import sys
import json
import time
import random
import string
from typing import List, Dict, Optional, Any

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.extend = extend
        self.cookie_cache = ""
        self._init_categories()

    def _init_categories(self):
        """初始化抖音直播完整分类体系"""
        self.sub_categories = [
            # 娱乐子类
            {"type_id": "102$4", "type_name": "音乐", "partition": "102"},
            {"type_id": "103$4", "type_name": "游戏", "partition": "103"},
            {"type_id": "105$4", "type_name": "舞蹈", "partition": "105"},
            {"type_id": "101$4", "type_name": "聊天", "partition": "101"},
            {"type_id": "104$4", "type_name": "二次元", "partition": "104"},
            {"type_id": "109$4", "type_name": "颜值", "partition": "109"},
            # 科技文化子类
            {"type_id": "106$4", "type_name": "文化", "partition": "106"},
            {"type_id": "108$4", "type_name": "运动", "partition": "108"},
            {"type_id": "107$4", "type_name": "生活", "partition": "107"},
            {"type_id": "112$4", "type_name": "教育", "partition": "112"},
        ]

    def getName(self):
        return "抖音直播"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, param):
        return None

    host = "https://live.douyin.com"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 分类配置
    classes_config = [
       ## 主分类
        ##{"type_id": "main_entertainment", "type_name": "娱乐天地", "subtype": "main"},
        ##{"type_id": "main_tech", "type_name": "科技文化", "subtype": "main"},
        # 娱乐子类
        {"type_id": "102$4", "type_name": "音乐"},
        {"type_id": "103$4", "type_name": "游戏"},
        {"type_id": "105$4", "type_name": "舞蹈"},
        {"type_id": "101$4", "type_name": "聊天"},
        {"type_id": "104$4", "type_name": "二次元"},
        {"type_id": "109$4", "type_name": " 颜值"},
        # 科技文化子类
        {"type_id": "106$4", "type_name": "文化"},
        {"type_id": "108$4", "type_name": "运动"},
        {"type_id": "107$4", "type_name": "生活"},
        {"type_id": "112$4", "type_name": "教育"},
    ]

    # ==================== 工具函数 ====================
    def _generate_device_id(self):
        timestamp = self._base36_encode(int(time.time() * 1000))
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=13))
        return f"{timestamp}{random_part}"

    @staticmethod
    def _base36_encode(num):
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        if num == 0:
            return '0'
        res = []
        while num > 0:
            num, rem = divmod(num, 36)
            res.append(alphabet[rem])
        return ''.join(reversed(res))

    def _get_cookie(self):
        if self.cookie_cache:
            return self.cookie_cache
        try:
            resp = self.fetch(self.host, headers=self.headers, verify=False)
            cookies = resp.headers.get('set-cookie', '')
            if cookies:
                match = re.search(r'ttwid=([^;]+)', cookies)
                if match:
                    self.cookie_cache = f"ttwid={match.group(1)}"
        except Exception:
            pass
        return self.cookie_cache

    def _get_headers(self):
        cookie = self._get_cookie()
        hd = self.headers.copy()
        hd["Referer"] = self.host
        if cookie:
            hd["Cookie"] = cookie
        return hd

    def _first_non_empty(self, *values):
        for v in values:
            if v is not None and v != '' and v != 0:
                return v
        return None

    def _format_online_count(self, user_count):
        """格式化在线人数显示"""
        if user_count is None or user_count == '':
            return ""
        try:
            count = int(user_count)
            if count >= 100000000:  # 亿
                return f"{count / 100000000:.1f}亿"
            elif count >= 10000:  # 万
                return f"{count / 10000:.1f}万"
            elif count > 0:
                return str(count)
            else:
                return ""
        except (ValueError, TypeError):
            return str(user_count) if user_count else ""

    def _parse_raw_live_data(self, item):
        if not isinstance(item, dict):
            return None
        candidates = [
            item.get('lives', {}).get('rawdata'),
            item.get('lives', {}).get('raw_data'),
            item.get('live', {}).get('rawdata'),
            item.get('live_info', {}).get('rawdata'),
            item.get('aweme_info', {}).get('live_info', {}).get('rawdata'),
            item.get('data', {}).get('rawdata'),
            item.get('rawdata'),
            item.get('lives'),
            item.get('live'),
            item.get('live_info'),
            item.get('aweme_info', {}).get('live_info'),
            item.get('aweme_info'),
            item.get('data'),
            item
        ]
        for c in candidates:
            if isinstance(c, str):
                try:
                    parsed = json.loads(c)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    continue
            elif isinstance(c, dict):
                return c
        return None

    def _normalize_search_item(self, raw, fallback=None):
        if not isinstance(raw, dict):
            return None
        fallback = fallback or {}

        room_id = self._first_non_empty(
            raw.get('id_str'),
            raw.get('room_id_str'),
            raw.get('room', {}).get('id_str'),
            raw.get('room', {}).get('id'),
            raw.get('room_id'),
            raw.get('roomId')
        )
        if not room_id:
            return None

        web_rid = self._first_non_empty(
            raw.get('owner', {}).get('web_rid'),
            raw.get('web_rid'),
            raw.get('room', {}).get('owner', {}).get('web_rid')
        ) or self._generate_device_id()

        nickname = self._first_non_empty(
            raw.get('owner', {}).get('nickname'),
            raw.get('nickname'),
            raw.get('room', {}).get('owner', {}).get('nickname'),
            fallback.get('nickname')
        ) or '抖音直播'

        title = self._first_non_empty(
            raw.get('title'),
            raw.get('room', {}).get('title'),
            fallback.get('title'),
            nickname
        )

        pic = self._first_non_empty(
            raw.get('owner', {}).get('avatar_large', {}).get('url_list', [None])[0],
            raw.get('room', {}).get('cover', {}).get('url_list', [None])[0],
            raw.get('cover', {}).get('url_list', [None])[0],
            raw.get('cover_url')
        ) or ''

        online_text = self._first_non_empty(
            raw.get('room', {}).get('stats', {}).get('user_count_str'),
            raw.get('room', {}).get('stats', {}).get('user_count'),
            raw.get('user_count_str'),
            raw.get('user_count'),
        )
        tag_text = self._first_non_empty(
            raw.get('video_feed_tag'),
            raw.get('room', {}).get('partition_road_map', [{}])[0].get('title'),
            raw.get('partition', {}).get('title'),
            fallback.get('tag')
        )
        remark = ' '.join(filter(None, [tag_text, online_text]))

        return {
            "vod_id": f"{web_rid}@@{room_id}",
            "vod_name": nickname,
            "vod_pic": pic,
            "vod_remarks": remark,
            "vod_content": title
        }

    def _extract_search_videos(self, payload):
        if not isinstance(payload, list):
            return []
        results = []
        seen = set()
        for item in payload:
            raw = self._parse_raw_live_data(item)
            norm = self._normalize_search_item(raw, {
                "nickname": item.get('nickname'),
                "title": item.get('title') or item.get('desc'),
                "tag": item.get('search_keyword')
            })
            if not norm:
                continue
            if norm['vod_id'] in seen:
                continue
            seen.add(norm['vod_id'])
            results.append(norm)
        return results

    def _get_category_name(self, category_id):
        for cat in self.classes_config:
            if cat.get('type_id') == category_id:
                return cat.get('type_name', '')
        return ''

    # ==================== 筛选配置 ====================
    def _get_filter_config(self, category_id):
        """获取分类的筛选配置 - 优化版"""
        return [
            {"key": "order", "name": "排序", "value": [
                {"n": "综合推荐", "v": "hot"},
                {"n": "在线人数", "v": "online"},
                {"n": "最新开播", "v": "time"},
            ]},
            {"key": "status", "name": "直播状态", "value": [
                {"n": "全部", "v": "all"},
                {"n": "正在直播", "v": "live"},
            ]},
            {"key": "online", "name": "在线人数", "value": [
                {"n": "不限", "v": "0"},
                {"n": "1万+", "v": "10000"},
                {"n": "5万+", "v": "50000"},
                {"n": "10万+", "v": "100000"},
            ]},
        ]

    # ==================== 框架标准方法 ====================
    def homeContent(self, filter):
        """首页内容"""
        classes = self.classes_config

        # 构建筛选配置
        filters = {}
        for cat in self.classes_config:
            filters[cat["type_id"]] = self._get_filter_config(cat["type_id"])

        # 获取热门推荐
        featured = self._get_featured_streams()

        return {
            "class": classes,
            "list": featured,
            "filters": filters
        }

    def _get_featured_streams(self):
        """获取首页推荐直播"""
        list_ = []
        headers = self._get_headers()

        urls_to_try = [
            "https://live.douyin.com/webcast/web/feed/",
            "https://webcast.amemv.com/webcast/web/feed/",
        ]

        for url in urls_to_try:
            try:
                params = {
                    "aid": "6383",
                    "app_name": "douyin_web",
                    "live_id": "1",
                    "device_platform": "web",
                    "count": "12",
                    "web_rid": self._generate_device_id(),
                }
                resp = self.fetch(url, headers=headers, params=params, verify=False)
                data = resp.json()

                items = data.get('data', []) or data.get('data', {}).get('data', [])
                if not isinstance(items, list):
                    items = []

                for it in items:
                    if 'room' not in it:
                        continue
                    room = it['room']
                    web_rid = it.get('web_rid') or self._generate_device_id()
                    room_id = room.get('id_str')
                    if not room_id:
                        continue

                    title = room.get('title', '抖音直播')
                    cover_url = room.get('cover', {}).get('url_list', [None])[0] if isinstance(room.get('cover'), dict) else ''
                    nickname = room.get('owner', {}).get('nickname', '主播')

                    # 获取在线人数 - 尝试多个字段
                    user_count = room.get('stats', {}).get('user_count', 0) or room.get('stats', {}).get('user_count_str', 0)
                    user_count_str = self._format_online_count(user_count)

                    list_.append({
                        "vod_id": f"{web_rid}@@{room_id}",
                        "vod_name": title,
                        "vod_pic": cover_url,
                        "vod_remarks": f"🔥{user_count_str}" if user_count_str else "🔥热门"
                    })

                if list_:
                    break
            except Exception:
                continue

        ##if not list_:
            ##list_ = [
                ##{"vod_id": "main_entertainment@@1", "vod_name": "娱乐天地", "vod_pic": "", "vod_remarks": "点击进入"},
                ##{"vod_id": "main_tech@@2", "vod_name": "科技文化", "vod_pic": "", "vod_remarks": "点击进入"},
            ##]

        return list_

    def homeVideoContent(self):
        """首页视频内容"""
        return {"list": self._get_featured_streams()}

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 - 支持完整筛选"""
        category_id = str(tid)
        page = int(pg or 1)
        offset = 15 * (page - 1)

        # 解析筛选参数
        order_by = 'hot'
        status_filter = 'all'
        online_threshold = 0

        if extend and isinstance(extend, dict):
            order_by = str(extend.get('order', 'hot'))
            status_filter = str(extend.get('status', 'all'))
            online_str = str(extend.get('online', '0'))
            try:
                online_threshold = int(online_str) if online_str and online_str != '0' else 0
            except (ValueError, TypeError):
                online_threshold = 0

        list_ = []

        # 主分类处理
        if category_id.startswith('main_'):
            return self._get_main_category_content(category_id, page, order_by, status_filter, online_threshold, offset)

        # 子分类处理
        return self._get_sub_category_content(category_id, page, order_by, status_filter, online_threshold, offset)

    def _filter_by_online(self, user_count, threshold):
        """根据在线人数筛选"""
        if threshold <= 0:
            return True
        try:
            count = int(user_count) if user_count else 0
            return count >= threshold
        except (ValueError, TypeError):
            return True

    def _get_main_category_content(self, category_id, page, order_by, status_filter, online_threshold, offset):
        """获取主分类内容 - 聚合子分类"""
        list_ = []
        headers = self._get_headers()

        # 确定主分类包含哪些子分类
        if category_id == 'main_entertainment':
            subcats = [c for c in self.sub_categories if c["type_id"] in ["102$4", "103$4", "105$4", "101$4", "104$4", "109$4"]]
        else:
            subcats = [c for c in self.sub_categories if c["type_id"] in ["106$4", "108$4", "107$4", "112$4"]]

        # 从每个子分类获取数据
        for subcat in subcats[:6]:
            subcat_id = subcat['type_id']
            params = self._build_category_params(subcat_id, offset, order_by)

            urls = [
                "https://live.douyin.com/webcast/web/partition/detail/room/v2/",
                "https://webcast.amemv.com/webcast/web/partition/detail/room/v2/",
            ]

            for url in urls:
                try:
                    resp = self.fetch(url, headers=headers, params=params, verify=False)
                    data = resp.json()

                    if data.get('status_code') != 0:
                        continue

                    items = data.get('data', {}).get('data', [])
                    if not items:
                        break

                    for it in items:
                        web_rid = it.get('web_rid') or self._generate_device_id()
                        room = it.get('room')
                        if not room:
                            continue
                        room_id = room.get('id_str')
                        if not room_id:
                            continue

                        title = room.get('title', subcat['type_name'])
                        cover = room.get('cover', {})
                        cover_url = cover.get('url_list', [None])[0] if isinstance(cover, dict) else ''
                        nickname = room.get('owner', {}).get('nickname', '主播')

                        # 获取在线人数
                        user_count = room.get('stats', {}).get('user_count', 0) or room.get('stats', {}).get('user_count_str', 0)
                        user_count_str = self._format_online_count(user_count)

                        # 在线人数筛选
                        if not self._filter_by_online(user_count, online_threshold):
                            continue

                        list_.append({
                            "vod_id": f"{web_rid}@@{room_id}",
                            "vod_name": title,
                            "vod_pic": cover_url,
                            "vod_remarks": f"{subcat['type_name']} | 🔥{user_count_str}" if user_count_str else subcat['type_name']
                        })
                    break
                except Exception:
                    continue

        # 根据在线人数排序
        if order_by == 'online':
            def get_user_count(item):
                remark = item.get('vod_remarks', '')
                match = re.search(r'([\d.]+)(万|亿)?', remark)
                if match:
                    num = float(match.group(1))
                    unit = match.group(2)
                    if unit == '亿':
                        return num * 100000000
                    elif unit == '万':
                        return num * 10000
                    return num
                return 0
            list_.sort(key=get_user_count, reverse=True)

        return {
            "list": list_[:20],
            "page": page,
            "pagecount": 9999,
            "limit": 15,
            "total": 999999
        }

    def _get_sub_category_content(self, category_id, page, order_by, status_filter, online_threshold, offset):
        """获取子分类内容"""
        parts = category_id.split('$')
        if len(parts) < 2:
            return {"list": [], "page": page, "pagecount": 0, "limit": 15, "total": 9999}
        partition, ptype = parts[0], parts[1]

        category_name = self._get_category_name(category_id)

        params = self._build_category_params(category_id, offset, order_by)
        headers = self._get_headers()

        urls = [
            "https://live.douyin.com/webcast/web/partition/detail/room/v2/",
            "https://webcast.amemv.com/webcast/web/partition/detail/room/v2/",
        ]
        list_ = []

        for url in urls:
            try:
                resp = self.fetch(url, headers=headers, params=params, verify=False)
                data = resp.json()
                if data.get('status_code') != 0:
                    continue
                if not data.get('data', {}).get('data'):
                    break
                items = data['data']['data']
                for it in items:
                    web_rid = it.get('web_rid') or self._generate_device_id()
                    room = it['room']

                    # 获取在线人数
                    user_count = room.get('stats', {}).get('user_count', 0) or room.get('stats', {}).get('user_count_str', 0)
                    user_count_str = self._format_online_count(user_count)

                    # 在线人数筛选
                    if not self._filter_by_online(user_count, online_threshold):
                        continue

                    title = room.get('title', category_name)
                    cover_url = room.get('cover', {}).get('url_list', [None])[0] if isinstance(room.get('cover'), dict) else ''
                    nickname = room.get('owner', {}).get('nickname', '主播')

                    list_.append({
                        "vod_id": f"{web_rid}@@{room['id_str']}",
                        "vod_name": title,
                        "vod_pic": cover_url,
                        "vod_remarks": f"🔥{user_count_str}" if user_count_str else category_name
                    })
                break
            except Exception:
                continue

        # 排序
        if order_by == 'online':
            def get_user_count(item):
                remark = item.get('vod_remarks', '')
                match = re.search(r'([\d.]+)(万|亿)?', remark)
                if match:
                    num = float(match.group(1))
                    unit = match.group(2)
                    if unit == '亿':
                        return num * 100000000
                    elif unit == '万':
                        return num * 10000
                    return num
                return 0
            list_.sort(key=get_user_count, reverse=True)

        return {
            "list": list_,
            "page": page,
            "pagecount": 9999,
            "limit": 15,
            "total": 999999
        }

    def _build_category_params(self, category_id, offset, order_by):
        """构建分类请求参数"""
        parts = category_id.split('$')
        partition = parts[0] if parts else category_id
        ptype = parts[1] if len(parts) > 1 else '4'

        return {
            "aid": "6383",
            "app_name": "douyin_web",
            "live_id": "1",
            "device_platform": "web",
            "language": "zh-CN",
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Chrome",
            "browser_version": "120.0.0.0",
            "partition": partition,
            "partition_type": ptype,
            "count": "15",
            "offset": str(offset),
            "web_rid": self._generate_device_id(),
            "cookie_enabled": "true",
            "screen_width": "1920",
            "screen_height": "1080"
        }

    def searchContent(self, key, quick, pg="1"):
        """搜索内容"""
        kw = key.strip()
        if not kw:
            return {"list": [], "page": 1}
        page = 1
        offset = 0

        headers = self._get_headers()

        # 策略1 专用直播搜索
        try:
            params1 = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "search_channel": "aweme_live",
                "search_source": "switch_tab",
                "query_correct_type": "1",
                "need_filter_settings": "1",
                "list_type": "single",
                "keyword": kw,
                "offset": str(offset),
                "count": "20",
                "os_version": "10"
            }
            r = self.fetch("https://www.douyin.com/aweme/v1/web/live/search/",
                           params=params1, headers=headers, verify=False)
            data = r.json()
            list_ = self._extract_search_videos(data.get('data'))
            if list_:
                return {"list": list_, "page": 1}
        except Exception:
            pass

        # 策略2 通用搜索
        try:
            params2 = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "search_channel": "aweme_live",
                "keyword": kw,
                "offset": str(offset),
                "count": "20",
                "os_version": "10"
            }
            r = self.fetch("https://www.douyin.com/aweme/v1/web/general/search/stream/",
                           params=params2, headers=headers, verify=False)
            data = r.json()
            list_ = self._extract_search_videos(data.get('data'))
            if list_:
                return {"list": list_, "page": 1}
        except Exception:
            pass

        # 降级分区搜索
        try:
            part_url = f"https://live.douyin.com/webcast/web/partition/search/?keyword={kw}&aid=6383"
            r = self.fetch(part_url, headers=self._get_headers(), verify=False)
            data = r.json()
            partitions = data.get('data', {}).get('SearchResult', [])
            if not partitions:
                return {"list": [], "page": 1}

            merged = []
            seen = set()
            for i in range(min(3, len(partitions))):
                part = partitions[i].get('partition', {})
                p_id = part.get('id_str')
                p_type = part.get('type')
                if not p_id or p_type is None:
                    continue
                cate_ret = self.categoryContent(f"{p_id}${p_type}", 1, None, None)
                for item in cate_ret.get('list', []):
                    if item['vod_id'] in seen:
                        continue
                    seen.add(item['vod_id'])
                    item['vod_remarks'] = item['vod_remarks'] or part.get('title', kw)
                    merged.append(item)
                    if len(merged) >= 20:
                        break
                if len(merged) >= 20:
                    break
            return {"list": merged, "page": 1}
        except Exception:
            pass

        return {"list": [], "page": 1}

    def detailContent(self, ids):
        """详情内容"""
        if not ids:
            return {"list": []}
        raw_id = ids[0]

        # 检查是否是主分类入口
        if raw_id.startswith('main_'):
            return {"list": []}

        parts = raw_id.split('@@')
        if len(parts) != 2:
            return {"list": []}
        web_rid, room_id = parts[0], parts[1]

        url = "https://live.douyin.com/webcast/room/web/enter/"
        params = {
            "aid": "6383",
            "app_name": "douyin_web",
            "live_id": "1",
            "device_platform": "web",
            "enter_from": "web_live",
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Chrome",
            "browser_version": "120.0.0.0",
            "web_rid": web_rid,
            "room_id_str": room_id,
            "enter_source": "",
            "is_need_double_stream": "false"
        }
        headers = self._get_headers()
        try:
            r = self.fetch(url, params=params, headers=headers, verify=False)
            data = r.json()
            if not data.get('data', {}).get('data'):
                return {"list": []}
            info = data['data']['data'][0]

            resolution_map = {
                "FULL_HD1": "蓝光",
                "HD1": "超清",
                "ORIGION": "原画",
                "SD1": "标清",
                "SD2": "高清"
            }

            flv_pull = info.get('stream_url', {}).get('flv_pull_url', {})
            flv_episodes = []
            for k, v in flv_pull.items():
                name = resolution_map.get(k, k)
                flv_episodes.append(f"{name}${v}")

            hls_pull = info.get('stream_url', {}).get('hls_pull_url_map', {})
            hls_episodes = []
            for k, v in hls_pull.items():
                name = resolution_map.get(k, k)
                hls_episodes.append(f"{name}${v}")

            vod_play_from = ""
            vod_play_url = ""
            if flv_episodes:
                vod_play_from += "FLV$$$"
                vod_play_url += "#".join(flv_episodes) + "$$$"
            if hls_episodes:
                vod_play_from += "HLS"
                vod_play_url += "#".join(hls_episodes)

            vod_play_from = vod_play_from.rstrip("$$$")
            vod_play_url = vod_play_url.rstrip("$$$")

            # 获取在线人数
            user_count = info.get('stats', {}).get('user_count', 0) or info.get('stats', {}).get('user_count_str', 0)
            user_count_str = self._format_online_count(user_count)

            vod = {
                "vod_id": raw_id,
                "vod_name": info.get('title', '抖音直播'),
                "vod_pic": info.get('cover', {}).get('url_list', [None])[0] if isinstance(info.get('cover'), dict) else '',
                "vod_actor": info.get('owner', {}).get('nickname', '主播') + (f" 🔥{user_count_str}" if user_count_str else ""),
                "vod_content": info.get('title', ''),
                "vod_play_from": vod_play_from,
                "vod_play_url": vod_play_url
            }
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        """播放器内容"""
        if not id:
            return {"parse": 0, "url": "", "header": self.headers}
        return {
            "parse": 0,
            "url": id,
            "header": {
                "User-Agent": self.ua,
                "Referer": self.host
            }
        }