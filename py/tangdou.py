# coding = utf-8
#!/usr/bin/python
import re
import sys
import json
import time
import urllib.parse
from base.spider import Spider

sys.path.append('..')

class Spider(Spider):
    def __init__(self):
        self.name = "糖豆广场舞"
        self.host = 'https://api-h5.tangdou.com'
        self.img_host = 'https://bimg.tangdou.com' 
        self.header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh,zh-CN;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'api-h5.tangdou.com',
            'Referer': 'https://www.tangdou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.cache = {}
        self.cache_timeout = 300  # 5分钟缓存
        self.uuid = f"{int(time.time() * 1000)}_{int(time.time() % 100000)}"
        
    def getName(self):
        return self.name

    def init(self, extend=''):
        pass

    def homeContent(self, filter):
        result = {}
        classes = [
            
            {"type_name": "广场舞", "type_id": "1"},
            {"type_name": "民族舞", "type_id": "2"},
            {"type_name": "jazz/现代舞", "type_id": "3"},
            {"type_name": "健身", "type_id": "4"},
            {"type_name": "双人舞", "type_id": "5"},
            {"type_name": "步法", "type_id": "6"},
            {"type_name": "气球", "type_id": "7"},
            {"type_name": "瑜伽", "type_id": "8"},
            {"type_name": "二人转", "type_id": "9"}
        ]
        
        result['class'] = classes
        
        filters = {}
        for cate in classes:
            tid = cate['type_id']
            filters[tid] = [
                {"key": "year", "name": "年份", "value": [
                    {"n": "全部", "v": "0"},
                    {"n": "2026", "v": "2026"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017及以前", "v": "2017"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"n": "最新", "v": "new"},
                    {"n": "最热", "v": "hot"},
                    {"n": "推荐", "v": "rec"}
                ]}
            ]
        
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        videos = []
        try:
            cache_key = "home_feed"
            data = self.get_cached_data(cache_key, 1, 20)
            
            if data and 'data' in data:
                for item in data['data']:
                    video = self._parse_video_item(item)
                    if video:
                        videos.append(video)
        except Exception as e:
            print(f"获取首页推荐失败: {e}")
        
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        videos = []
        try:
            page_size = 30
            api_url = f"{self.host}/mtangdou/home/feed?page={pg}&num={page_size}&uuid={self.uuid}"
            
            if tid != "0":
                api_url += f"&type={tid}"
            
            sort = extend.get('sort', 'new')
            if sort == 'hot':
                api_url += "&sort=hot"
            elif sort == 'rec':
                api_url += "&sort=rec"
            
            cache_key = f"category_{tid}_{pg}_{sort}"
            data = self.fetchData(api_url, cache_key)
            
            if data and 'data' in data:
                for item in data['data']:
                    video = self._parse_video_item(item)
                    if video:
                        videos.append(video)
        except Exception as e:
            print(f"获取分类内容失败: {e}")
        
        return {
            'list': videos,
            'page': int(pg),
            'pagecount': 9999,
            'limit': 30,
            'total': 999999
        }

    def detailContent(self, ids):
        try:
            vid = ids[0].split('||')[0] if '||' in ids[0] else ids[0]
            
            play_url_api = f"{self.host}/mtangdou/video/play?vid={vid}&uuid={self.uuid}"
            share_api = f"{self.host}/sample/share/main?vid={vid}"
            
            play_data = self.fetchData(play_url_api, f"play_{vid}", use_cache=False)
            
            share_data = self.fetchData(share_api, f"share_{vid}", use_cache=False)
            
            if not share_data or 'data' not in share_data:
                return {'list': []}
            
            data_info = share_data['data']
            
            content = data_info.get('desc', data_info.get('description', '')).strip()
            if not content:
                content = '祝您身体健康'
            
            cover_path = data_info.get('cover', data_info.get('img', ''))
            if cover_path and not cover_path.startswith('http'):
                cover_url = self.img_host + cover_path
            else:
                cover_url = cover_path

            video_detail = {
                "vod_id": vid,
                "vod_name": data_info.get('title', '').strip(),
                "vod_pic": cover_url,
                "vod_year": str(data_info.get('year', '')),
                "vod_area": data_info.get('area', '大陆'),
                "vod_actor": data_info.get('teacher', data_info.get('author', '')),
                "vod_director": "",
                "vod_content": content,
                "vod_play_from": "在线播放",
                "vod_remarks": f"时长: {data_info.get('duration_str', '未知')}" if 'duration_str' in data_info else ""
            }
            
            play_url = ""
            if play_data and 'data' in play_data:
                play_url = play_data['data'].get('play_url', '')
              
            if not play_url and 'video_url' in data_info:
                play_url = data_info['video_url']
            
            if play_url:
                video_detail["vod_play_url"] = f"{video_detail['vod_name']}${vid}||{play_url}"
            else:
                video_detail["vod_play_url"] = ""
            
            return {'list': [video_detail]}
            
        except Exception as e:
            print(f"获取详情失败: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg=1):
        videos = []
        try:
            search_api = f"{self.host}/mtangdou/search?word={urllib.parse.quote(key)}&page={pg}&num=30&uuid={self.uuid}"
            
            data = self.fetchData(search_api, use_cache=False)
            
            if data and 'data' in data:
                for item in data['data']:
                    video = self._parse_video_item(item)
                    if video:
                        videos.append(video)
            else:
                if pg == 1:
                    feed_data = self.get_cached_data("search_feed", 1, 100)
                    if feed_data and 'data' in feed_data:
                        key_lower = key.lower()
                        for item in feed_data['data']:
                            title = item.get('title', '').lower()
                            if key_lower in title:
                                video = self._parse_video_item(item)
                                if video:
                                    videos.append(video)
        except Exception as e:
            print(f"搜索失败: {e}")
        
        return {
            'list': videos,
            'page': int(pg),
            'pagecount': 9999,
            'limit': 30,
            'total': 999999
        }

    def playerContent(self, flag, id, vipFlags):
        try:
            if '||' in id:
                parts = id.split('||')
                vid = parts[0]
                play_url = parts[1] if len(parts) > 1 else ""
            else:
                vid = id
                play_url = ""
            
            if not play_url:
                play_api = f"{self.host}/mtangdou/video/play?vid={vid}&uuid={self.uuid}"
                data = self.fetchData(play_api, use_cache=False)
                if data and 'data' in data:
                    play_url = data['data'].get('play_url', '')
            
            if play_url:
                headers = {
                    "Referer": "https://www.tangdou.com/",
                    "User-Agent": self.header['User-Agent']
                }
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": play_url,
                    "header": json.dumps(headers)
                }
            else:
                return {"parse": 0, "playUrl": "", "url": ""}
                
        except Exception as e:
            print(f"播放解析失败: {e}")
            return {"parse": 0, "playUrl": "", "url": ""}

    def isVideoFormat(self, url):
        video_formats = ['.m3u8', '.mp4', '.avi', '.mkv', '.flv', '.ts', '.mov']
        return any(url.lower().endswith(fmt) for fmt in video_formats)

    def manualVideoCheck(self):
        pass

    def localProxy(self, params):
        return None

    def _parse_video_item(self, item):
        try:
            vid = str(item.get('vid', ''))
            if not vid:
                return None
            
            title = item.get('title', '').strip()
            cover_path = item.get('cover', item.get('img', item.get('video_img', '')))
            if cover_path and not cover_path.startswith('http'):
                img = self.img_host + cover_path
            else:
                img = cover_path
            
            duration = item.get('duration_str', '')
            teacher = item.get('teacher', item.get('author', ''))
            
            remarks = duration if duration else teacher
            
            return {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": remarks
            }
        except Exception as e:
            print(f"解析视频项失败: {e}")
            return None

    def get_cached_data(self, cache_key, page=1, num=30):
        current_time = time.time()
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_timeout:
                return cached_data

        api_url = f"{self.host}/mtangdou/home/feed?page={page}&num={num}&uuid={self.uuid}"
        result = self.fetchData(api_url, cache_key)
        if result:
            self.cache[cache_key] = (result, current_time)
        return result

    def fetchData(self, url, cache_key=None, use_cache=True):
        try:
            current_time = time.time()
            if use_cache and cache_key and cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return cached_data
            
            start_time = time.time()
            response = self.fetch(url, headers=self.header)
            end_time = time.time()
            
            print(f"请求耗时: {end_time - start_time:.2f}秒, URL: {url[:60]}...")
            
            if response.status_code != 200:
                print(f"API请求失败: {response.status_code}")
                return None
            
            data = json.loads(response.text)
            
            if use_cache and cache_key:
                self.cache[cache_key] = (data, current_time)
                
            return data
            
        except Exception as e:
            print(f"获取数据失败: {e}, URL: {url}")
            return None

    def fetch(self, url, headers=None):
        import requests
        try:
            if headers is None:
                headers = self.header
            response = requests.get(url, headers=headers, timeout=10)
            return response
        except Exception as e:
            print(f"请求异常: {e}")
            class FakeResponse:
                status_code = 0
                text = ""
            return FakeResponse()

if __name__ == '__main__':
    pass
