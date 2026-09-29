var rule = {
    title: 'ATMB',
    host: '',
    homeUrl: '',
    searchUrl: '**',
    detailUrl: 'fyid',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    multi: 1,
    class_name: '电影&剧集&综艺&动漫&记录&少儿&短剧&漫剧&体育&中视频&宠物',
    class_url: 'movie&tv&variety&cartoon&doco&child&short&manju&sports&midvideo&pettv',
    limit: 20,
    play_parse: true,
    headers: {
        'User-Agent': 'PC_UA'
    },
    timeout: 10000,
    filter: {
        "movie":[
            {key:"itype",name:"类型",value:[{n:"全部",v:"-1"},{n:"动作",v:"4"},{n:"喜剧",v:"3"},{n:"爱情",v:"5"},{n:"科幻",v:"12"},{n:"犯罪",v:"6"},{n:"冒险",v:"7"},{n:"恐怖",v:"11"},{n:"动画",v:"15"},{n:"战争",v:"8"},{n:"悬疑",v:"10"},{n:"灾难",v:"25"},{n:"青春",v:"26"}]},
            {key:"iarea",name:"地区",value:[{n:"全部",v:"-1"},{n:"内地",v:"100024"},{n:"中国香港",v:"100025"},{n:"中国台湾",v:"100026"},{n:"美国",v:"100029"},{n:"日本",v:"100027"},{n:"韩国",v:"100028"},{n:"泰国",v:"100031"},{n:"印度",v:"100030"},{n:"英国",v:"15"},{n:"法国",v:"16"},{n:"德国",v:"17"},{n:"加拿大",v:"18"},{n:"西班牙",v:"19"},{n:"意大利",v:"20"},{n:"澳大利亚",v:"21"},{n:"其他",v:"100033"}]},
            {key:"iyear",name:"年份",value:[{n:"全部",v:"-1"},{n:"即将上线",v:"999"},{n:"2026",v:"2026"},{n:"2025",v:"2025"},{n:"2024",v:"2024"},{n:"2023",v:"2023"},{n:"2022",v:"2022"},{n:"2021",v:"2021"},{n:"2020",v:"2020"},{n:"2019",v:"20"},{n:"2018",v:"2018"},{n:"2017",v:"1"},{n:"2016",v:"2"},{n:"2015",v:"3"},{n:"2014",v:"4"},{n:"2013-2011",v:"5"},{n:"2010-2006",v:"6"},{n:"2005-2000",v:"7"},{n:"90年代",v:"8"},{n:"80年代",v:"9"},{n:"其他",v:"10"}]}
        ],
        "tv":[
            {key:"itype",name:"类型",value:[{n:"全部",v:"-1"},{n:"爱情",v:"1"},{n:"都市",v:"2"},{n:"青春",v:"3"},{n:"奇幻",v:"4"},{n:"武侠",v:"5"},{n:"古装",v:"6"},{n:"科幻",v:"7"},{n:"猎奇",v:"8"},{n:"竞技",v:"9"},{n:"传奇",v:"10"},{n:"逆袭",v:"19"},{n:"军旅",v:"11"},{n:"家庭",v:"12"},{n:"喜剧",v:"13"},{n:"悬疑",v:"14"},{n:"权谋",v:"15"},{n:"革命",v:"16"},{n:"现实",v:"17"},{n:"刑侦",v:"18"},{n:"民国",v:"20"},{n:"IP改编",v:"21"}]},
            {key:"iarea",name:"地区",value:[{n:"全部",v:"-1"},{n:"内地",v:"0"},{n:"中国香港",v:"14"},{n:"中国台湾",v:"4"},{n:"美国",v:"8"},{n:"泰国",v:"9"},{n:"英国",v:"1"},{n:"韩国",v:"5"},{n:"日本",v:"10"},{n:"其他",v:"9999"}]},
            {key:"iyear",name:"年份",value:[{n:"全部",v:"-1"},{n:"即将上线",v:"1"},{n:"2026",v:"2026"},{n:"2025",v:"2025"},{n:"2024",v:"2"},{n:"2023",v:"3"},{n:"2022",v:"4"},{n:"2021",v:"5"},{n:"2020-2016",v:"6"},{n:"2015-2011",v:"7"},{n:"2010-2000",v:"8"},{n:"更早",v:"9"}]}
        ],
        "variety":[
            {key:"itype",name:"类型",value:[{n:"全部",v:"-1"},{n:"游戏",v:"10"},{n:"脱口秀",v:"2"},{n:"音乐舞台",v:"11"},{n:"情感",v:"12"},{n:"生活",v:"22"},{n:"职场",v:"20"},{n:"喜剧",v:"14"},{n:"美食",v:"19"},{n:"潮流运动",v:"21"},{n:"竞技",v:"24"},{n:"影视",v:"16"},{n:"电竞",v:"15"},{n:"推理",v:"25"},{n:"访谈",v:"3"},{n:"亲子",v:"17"},{n:"文化",v:"26"},{n:"互动",v:"23"},{n:"晚会",v:"6"},{n:"资讯",v:"7"}]},
            {key:"iarea",name:"地区",value:[{n:"全部",v:"-1"},{n:"国内",v:"1"},{n:"海外",v:"2"}]},
            {key:"iyear",name:"年份",value:[{n:"全部",v:"-1"},{n:"2026",v:"2026"},{n:"2025",v:"2025"},{n:"2024",v:"2024"},{n:"2023",v:"2023"},{n:"2022",v:"2022"},{n:"2021",v:"2021"},{n:"2020",v:"50"},{n:"2019",v:"7"},{n:"2018",v:"1"},{n:"2017",v:"2"},{n:"2016",v:"3"},{n:"2015",v:"4"},{n:"2014",v:"5"},{n:"2013",v:"6"},{n:"2012",v:"2012"},{n:"2011",v:"2011"},{n:"2010",v:"2010"},{n:"更早",v:"99"}]}
        ],
        "cartoon":[
            {key:"itype",name:"类型",value:[{n:"全部",v:"-1"},{n:"玄幻",v:"9"},{n:"科幻",v:"4"},{n:"奇幻",v:"21"},{n:"武侠",v:"13"},{n:"仙侠",v:"23"},{n:"都市",v:"24"},{n:"恋爱",v:"7"},{n:"搞笑",v:"1"},{n:"冒险",v:"2"},{n:"悬疑",v:"17"},{n:"竞技",v:"20"},{n:"日常",v:"15"},{n:"真人",v:"18"},{n:"治愈",v:"25"},{n:"游戏",v:"26"},{n:"异能",v:"27"},{n:"历史",v:"19"},{n:"古风",v:"28"},{n:"智斗",v:"29"},{n:"恐怖",v:"30"},{n:"美食",v:"31"},{n:"音乐",v:"32"},{n:"其他",v:"12"}]},
            {key:"iarea",name:"地区",value:[{n:"全部",v:"-1"},{n:"内地",v:"1"},{n:"日本",v:"2"},{n:"欧美",v:"3"},{n:"其他",v:"4"}]},
            {key:"iyear",name:"年份",value:[{n:"全部",v:"-1"},{n:"2026",v:"2026"},{n:"2025",v:"2025"},{n:"2024",v:"2024"},{n:"2023",v:"2023"},{n:"2022",v:"2022"},{n:"2021",v:"2021"},{n:"2020",v:"50"},{n:"2019",v:"11"},{n:"2018",v:"2018"},{n:"2017",v:"2017"},{n:"2016",v:"1"},{n:"2015",v:"2"},{n:"2014",v:"3"},{n:"2013",v:"4"},{n:"2012",v:"5"},{n:"2011",v:"6"},{n:"00年代",v:"7"},{n:"90年代",v:"8"},{n:"80年代",v:"9"},{n:"更早",v:"10"}]}
        ]
    },

    lazy: $js.toString(() => {
        let playUrl = input;
        if (playUrl.indexOf("$") > -1) {
            playUrl = playUrl.split("$")[1];
        }
        input = {
            parse: 1,
            url: playUrl,
            jx: 1
        };
    }),

    一级: $js.toString(() => {
        let tid = MY_CATE || 'movie';
        let CATE_MAP = {
            'movie': [['qq', 'movie'], ['mgtv', '3'], ['iqiyi', '1'], ['iqiyi', '16'], ['bili', '2']],
            'tv': [['qq', 'tv'], ['mgtv', '2'], ['iqiyi', '2'], ['bili', '5']],
            'variety': [['qq', 'variety'], ['mgtv', '1'], ['iqiyi', '6'], ['bili', '7']],
            'cartoon': [['qq', 'cartoon'], ['mgtv', '50'], ['iqiyi', '4'], ['bili', '1'], ['bili', '4']],
            'doco': [['qq', 'doco'], ['mgtv', '51'], ['iqiyi', '3'], ['bili', '3']],
            'child': [['qq', 'child'], ['mgtv', '10'], ['mgtv', '115'], ['iqiyi', '15']],
            'short': [['qq', 'short'], ['iqiyi', '35']],
            'manju': [['iqiyi', '37']],
            'sports': [['qq', 'sports']],
            'midvideo': [['qq', 'midvideo']],
            'pettv': [['qq', 'pettv']],
        };
        let PRIORITY = { 'mgtv': 0, 'bili': 1, 'qq': 2, 'iqiyi': 3 };

        function normTitle(t) {
            if (!t) return '';
            return t.replace(/<[^>]+>/g, '').replace(/[\s\p{P}]/gu, '').toLowerCase();
        }
        function mergeResults(results) {
            let map = {};
            let order = [];
            results.forEach(function (item) {
                let key = normTitle(item.title);
                if (!key) return;
                if (!map[key]) {
                    map[key] = item;
                    order.push(key);
                } else {
                    let oldP = map[key].url.split('__')[0];
                    let newP = item.url.split('__')[0];
                    let oldRank = PRIORITY[oldP] !== undefined ? PRIORITY[oldP] : 99;
                    let newRank = PRIORITY[newP] !== undefined ? PRIORITY[newP] : 99;
                    if (newRank < oldRank) map[key] = item;
                }
            });
            return order.map(function (k) { return map[k]; });
        }

        let platforms = CATE_MAP[tid] || [];
        let all = [];
        var fl = MY_FL || {};
        var pg = MY_PAGE || 1;

        var qqFp = 'sort=75';
        if (fl.itype && fl.itype !== '-1') qqFp += '&itype=' + fl.itype;
        if (fl.iarea && fl.iarea !== '-1') qqFp += '&iarea=' + fl.iarea;
        if (fl.iyear && fl.iyear !== '-1') qqFp += '&iyear=' + fl.iyear;

        let categoryUa = (typeof PC_UA !== 'undefined' && PC_UA) ? PC_UA : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';
        let categoryTasks = platforms.map(function (pf) {
            let platform = pf[0];
            let chanId = pf[1];
            if (platform === 'qq') {
                let QQ_CHAN = { 'movie': 100173, 'tv': 100113, 'variety': 100109, 'cartoon': 100119, 'child': 100150, 'doco': 100105, 'short': 120188, 'sports': 100103, 'midvideo': 110852, 'pettv': 100302 };
                let cid = QQ_CHAN[chanId] || 100173;
                let headers = {
                    'User-Agent': categoryUa, 'Content-Type': 'application/json',
                    'origin': 'https://v.qq.com', 'referer': 'https://v.qq.com/'
                };

                if (chanId === 'sports' || chanId === 'midvideo' || chanId === 'pettv') {
                    let gp = {
                        page_params: { page_type: 'channel', page_id: String(cid), scene: 'channel', new_mark_label_enabled: '1' },
                        page_bypass_params: { params: { platform_id: '2', caller_id: '3000010', data_mode: 'default', user_mode: 'default', page_type: 'channel', page_id: String(cid), scene: 'channel', new_mark_label_enabled: '1' }, scene: 'channel' },
                        page_context: null
                    };
                    return {
                        platform: platform, chanId: chanId,
                        url: 'https://pbaccess.video.qq.com/trpc.vector_layout.page_view.PageService/getPage?video_appid=3000010&vversion_platform=2',
                        options: { method: 'POST', headers: headers, data: gp },
                        fallbackOptions: { method: 'POST', headers: headers, body: gp }, jsonBody: true, relay: 'getpage', cid: String(cid)
                    };
                }
                let body = { page_params: { channel_id: String(cid), filter_params: qqFp, page_type: 'operation', page_id: 'channel_list' } };
                if (pg > 1) {
                    let m = pg - 1;
                    body.page_context = {
                        "_ctrl_page_index": String(m), "_ctrl_showed_module_num": String(m),
                        "_ds_cli_6970df954e7a9803_poster_offset": String(m * 12),
                        "_ds_cli_6970df954e7a9803_poster_size": "12", "_merger_mod_cnt": String(m),
                        "page_index": String(m),
                        "sdk_page_ctx": '{"page_offset":' + m + ',"page_size":5,"used_module_num":' + m + '}',
                        "video_un_page_index": String(m)
                    };
                }
                return {
                    platform: platform, chanId: chanId,
                    url: 'https://pbaccess.video.qq.com/trpc.multi_vector_layout.mvl_controller.MVLPageHTTPService/getMVLPage?&vversion_platform=2',
                    options: { method: 'POST', headers: headers, data: body },
                    fallbackOptions: { method: 'POST', headers: headers, body: body }, jsonBody: true
                };
            }
            if (platform === 'mgtv') {
                let url = 'https://pianku.api.mgtv.com/rider/list/pcweb/v3?platform=pcweb&channelId=' + chanId + '&pn=' + pg + '&pc=20&hudong=1&_support=10000000&kind=a1&area=a1';
                if (fl.iyear && fl.iyear !== '-1') url += '&year=' + fl.iyear;
                return { platform: platform, chanId: chanId, url: url, options: { headers: { 'User-Agent': categoryUa, 'Referer': 'https://www.mgtv.com' } } };
            }
            if (platform === 'iqiyi') {
                return {
                    platform: platform, chanId: chanId,
                    url: 'https://pcw-api.iqiyi.com/search/recommend/list?channel_id=' + chanId + '&data_type=1&page_id=' + pg + '&ret_num=20',
                    options: { headers: { 'User-Agent': categoryUa } }
                };
            }
            return {
                platform: platform, chanId: chanId,
                url: 'https://api.bilibili.com/pgc/season/index/result?order=2&pagesize=20&type=1&season_type=' + chanId + '&page=' + pg + '&season_status=-1',
                options: { headers: { 'User-Agent': categoryUa, 'Referer': 'https://www.bilibili.com' } }
            };
        });

        function fetchGetPage(task){
            try {
                var cid = task.cid;
                var gHeaders = {
                    'User-Agent': categoryUa, 'Content-Type': 'application/json',
                    'origin': 'https://v.qq.com', 'referer': 'https://v.qq.com/'
                };
                var ctx = null, html = '';
                for (var kk = 1; kk <= pg; kk++) {
                    var gp = {
                        page_params: { page_type: 'channel', page_id: cid, scene: 'channel', new_mark_label_enabled: '1' },
                        page_bypass_params: { params: { platform_id: '2', caller_id: '3000010', data_mode: 'default', user_mode: 'default', page_type: 'channel', page_id: cid, scene: 'channel', new_mark_label_enabled: '1' }, scene: 'channel' },
                        page_context: ctx
                    };
                    html = request(task.url, { method: 'POST', headers: gHeaders, body: gp }, true);
                    var pj = JSON.parse(html);
                    ctx = (pj.data && pj.data.page_context) ? pj.data.page_context : null;
                    if (!ctx) break;
                }
                return html;
            } catch (e) { log('getPage翻页错误: ' + e.message); return ''; }
        }
        let categoryHtml = categoryTasks.map(function(){ return ''; });
        let normalIdx = [];
        categoryTasks.forEach(function(t,i){ if(t.relay!=='getpage') normalIdx.push(i); });
        if (normalIdx.length > 1 && typeof batchFetch === 'function') {
            try {
                let bres = batchFetch(normalIdx.map(function(i){ let t=categoryTasks[i]; return { url:t.url, options:t.options||{} }; }));
                if(Array.isArray(bres) && bres.length===normalIdx.length){ normalIdx.forEach(function(i,n){ categoryHtml[i]=bres[n]; }); }
            } catch (e) { log('分类并发不可用，切换串行: ' + e.message); }
        }
        normalIdx.forEach(function(i){
            if(categoryHtml[i]===''){
                let t=categoryTasks[i];
                try { categoryHtml[i]=request(t.url,t.fallbackOptions||t.options||{},t.jsonBody===true); }
                catch(e){ log(t.platform+'分类请求错误: '+e.message); categoryHtml[i]=''; }
            }
        });
        categoryTasks.forEach(function(t,i){ if(t.relay==='getpage') categoryHtml[i]=fetchGetPage(t); });

        categoryTasks.forEach(function (task, taskIndex) {
            let platform = task.platform;
            let chanId = task.chanId;
            try {
                let html = categoryHtml[taskIndex] || '';
                if (!html) return;
                let json = JSON.parse(html);
                if (platform === 'qq') {
                    let qqSeen = {};
                    function collectQqCards(node) {
                        if (!node) return;
                        if (Array.isArray(node)) { node.forEach(function (child) { collectQqCards(child); }); return; }
                        if (typeof node !== 'object') return;
                        let p = node.params;
                        if (p && p.cid && !qqSeen[p.cid]) {
                            let title = p.title || p.mz_title || '';
                            if (title) {
                                qqSeen[p.cid] = 1;
                                let remark = p.third_title || p.update_desc || p.second_title || p.sub_title || p.episode_updated || p.mark_label || p.year || '';
                                let pic = p.image_url_vertical || p.new_pic_vt || p.new_pic_hz || p.pic_276x386 || p.image_url || p.ready_image_url || '';
                                all.push({ title: title, img: pic, pic_url: pic, url: 'qq__' + p.cid, desc: '腾讯' });
                            }
                        }
                        Object.keys(node).forEach(function (key) {
                            if (key === 'params') return;
                            let child = node[key];
                            if (child && typeof child === 'object') collectQqCards(child);
                        });
                    }
                    collectQqCards(json.data || json);
                } else if (platform === 'mgtv') {
                    let items = json.data ? json.data.hitDocs || [] : [];
                    items.forEach(function (item) {
                        if (item.title && (item.playPartId || item.clipId)) {
                            let mgtvId = item.playPartId || item.clipId;
                            let remark = item.updateInfo || (item.rightCorner && item.rightCorner.text) || item.update_info || item.subtitle || '';
                            let pic = item.img || '';
                            all.push({ title: item.title, img: pic, pic_url: pic, url: 'mgtv__' + mgtvId, desc: '芒果' });
                        }
                    });
                } else if (platform === 'iqiyi') {
                    let items = json.data ? json.data.list || [] : [];
                    items.forEach(function (item) {
                        if (item.name && item.albumId) {
                            let pic = item.imageUrl || '';
                            if (pic.startsWith('//')) pic = 'https:' + pic;
                            let remark = '';
                            let latest = item.latestOrder || 0;
                            let total = item.videoCount || 0;
                            let channel = Number(item.channelId || chanId || 0);
                            if (channel === 1) remark = item.score ? item.score + '分' : '';
                            else if (channel === 6) remark = item.period ? item.period + (String(item.period).indexOf('期') > -1 ? '' : '期') : '';
                            else if (channel === 5) remark = item.focus || '';
                            else if (latest && total) remark = Number(latest) === Number(total) ? latest + '集全' : latest + '/' + total + '集';
                            else if (latest) remark = '更新至 ' + latest + '集';
                            else if (total) remark = '共' + total + '集';
                            else remark = item.focus || item.period || item.subtitle || '';
                            if (item.score && channel !== 1) remark = item.score + '分\t' + remark;
                            all.push({ title: item.name, img: pic, pic_url: pic, url: 'iqiyi__' + item.albumId, desc: '爱奇艺' });
                        }
                    });
                } else if (platform === 'bili') {
                    let items = (json.data && json.data.list) ? json.data.list : [];
                    items.forEach(function (vod) {
                        if (vod.season_id && vod.title) {
                            let remark = (vod.new_ep && vod.new_ep.index_show) || vod.index_show || vod.badge || '';
                            let pic = vod.cover || '';
                            all.push({ title: vod.title, img: pic, pic_url: pic, url: 'bili__' + vod.season_id, desc: '哔哩哔哩' });
                        }
                    });
                }
            } catch (e) { log(platform + '分类解析错误: ' + e.message); }
        });

        let merged = mergeResults(all);
        setResult(merged);
    }),

    二级: $js.toString(() => {

        if (typeof log === 'undefined') log = function () {};
        if (typeof fetch_params === 'undefined') fetch_params = { headers: {} };
        if (!fetch_params.headers) fetch_params.headers = {};
        var PC_UA = (typeof PC_UA !== 'undefined' && PC_UA) ? PC_UA : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
        var MOBILE_UA = (typeof MOBILE_UA !== 'undefined' && MOBILE_UA) ? MOBILE_UA : 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1';
        let parts = input.split('__');
        let platform = parts[0];
        let vid = parts[1];
        let d = [];
        VOD = {};

        try {
            if (platform === 'mgtv') {
                fetch_params.headers.Referer = 'https://www.mgtv.com';
                fetch_params.headers['User-Agent'] = MOBILE_UA;

                var epUrl = 'https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=' + vid;
                var epHtml = request(epUrl);
                var epJson = null;
                try { epJson = JSON.parse(epHtml); } catch (e) { log('芒果episode解析错误: ' + e.message); }
                var epList = (epJson && epJson.data) ? epJson.data.list || [] : [];
                var totalPage = (epJson && epJson.data) ? epJson.data.total_page || 1 : 1;

                if (!epList.length) {
                    fetch_params.headers['User-Agent'] = PC_UA;
                    var albumHtml = request('https://www.mgtv.com/b/' + vid + '/');
                    var videoId = '';
                    var m1 = albumHtml.match(/\/b\/\d+\/(\d+)\.html/);
                    if (m1) videoId = m1[1];
                    if (!videoId) {
                        var m2 = albumHtml.match(/url=([^"'\s>]+)/i);
                        if (m2) {
                            var redir = m2[1];
                            if (redir.indexOf('http') !== 0) redir = 'https://www.mgtv.com' + redir;
                            var html2 = request(redir);
                            var m3 = html2.match(/\/b\/\d+\/(\d+)\.html/);
                            if (m3) videoId = m3[1];
                        }
                    }
                    log('芒果专辑ID=' + vid + ' 视频ID=' + videoId);
                    if (videoId) {
                        fetch_params.headers['User-Agent'] = MOBILE_UA;
                        epHtml = request('https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=' + videoId);
                        try { epJson = JSON.parse(epHtml); } catch (e) {}
                        epList = (epJson && epJson.data) ? epJson.data.list || [] : [];
                        totalPage = (epJson && epJson.data) ? epJson.data.total_page || 1 : 1;
                    }
                }

                if (totalPage > 1) {
                    for (var pi = 2; pi <= totalPage; pi++) {
                        try {
                            var pHtml = request('https://pcweb.api.mgtv.com/episode/list?page=' + pi + '&size=50&video_id=' + vid);
                            var pJson = JSON.parse(pHtml);
                            if (pJson && pJson.data && pJson.data.list) epList = epList.concat(pJson.data.list);
                        } catch (e) { break; }
                    }
                }

                if (epList.length) {
                    fetch_params.headers['User-Agent'] = MOBILE_UA;
                    var ourl = epList[0].url;
                    if (ourl && ourl.indexOf('http') !== 0) ourl = 'https://www.mgtv.com' + ourl;
                    if (ourl) {
                        var detailHtml = request(ourl);
                        if (detailHtml.indexOf('302') > -1 || detailHtml.indexOf('window.location') > -1) {
                            var rm = detailHtml.match(/url=([^"'\s>]+)/i) || detailHtml.match(/href=["']([^"']+)/i);
                            if (rm) {
                                ourl = rm[1];
                                if (ourl.indexOf('http') !== 0) ourl = 'https://www.mgtv.com' + ourl;
                                detailHtml = request(ourl);
                            }
                        }
                        var tm = detailHtml.match(/<title>([^<]+)<\/title>/);
                        if (tm) {
                            var t = tm[1];
                            if (t && t.indexOf('302') < 0 && t.indexOf('Found') < 0 && t.indexOf('芒果TV') < 0 && t.indexOf('首页') < 0) {
                                t = t.replace(/\s*第\d+集.*$/i, '').replace(/\s*[-_]\s*芒果TV.*$/i, '').replace(/\s*[-_]\s*湖南卫视.*$/i, '').trim();
                                if (t) VOD.vod_name = t;
                            }
                        }
                        var pm = detailHtml.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)/i);
                        if (pm) VOD.vod_pic = pm[1];
                    }
                }

                for (var ei = 0; ei < epList.length; ei++) {
                    var ep = epList[ei];
                    if (ep.isIntact == '1' && ep.url) {
                        var playUrl = ep.url;
                        if (playUrl.indexOf('http') !== 0) playUrl = 'https://www.mgtv.com' + playUrl;
                        d.push({ title: ep.t4 || ep.t2 || '正片', url: playUrl });
                    }
                }

                if (!VOD.vod_name && epList[0]) {
                    var rawName = epList[0].t3 || '';
                    VOD.vod_name = rawName.replace(/\s*第\d+集.*$/, '').trim();
                }
                if (!VOD.vod_pic && epList[0]) VOD.vod_pic = epList[0].img || '';

            } else if (platform === 'bili') {
                fetch_params.headers['User-Agent'] = PC_UA;
                fetch_params.headers.Referer = 'https://www.bilibili.com';
                let detailUrl = 'https://api.bilibili.com/pgc/view/web/season?season_id=' + vid;
                let html = request(detailUrl);
                let json = JSON.parse(html);
                let result = json.result || {};
                let episodes = result.episodes || [];

                episodes.forEach(function (ep) {
                    let badge = ep.badge || '';
                    if (ep.section_type === 1 || ep.badge_type === 1 || badge.indexOf('预告') > -1) return;
                    let title = (ep.title || '') + ' ' + (ep.long_title || '');
                    if (ep.link) d.push({ title: title.trim(), url: ep.link });
                });
                VOD.vod_name = result.title || '';
                VOD.vod_pic = result.cover || '';

            } else if (platform === 'qq') {
                // 参考腾讯.js：用fetch请求float_vinfo2
                let QZOutputJson;
                fetch_params.headers['User-Agent'] = PC_UA;
                let detailUrl = 'https://node.video.qq.com/x/api/float_vinfo2?cid=' + vid;
                let html = fetch(detailUrl, fetch_params);
                let json = JSON.parse(html);
                let videoIds = (json.c && json.c.video_ids) || [];
                VOD.vod_name = (json.c && json.c.title) || '';
                VOD.vod_pic = (json.c && json.c.pic) || '';

                if (videoIds.length === 1) {
                    d.push({ title: '在线播放', url: 'https://v.qq.com/x/cover/' + vid + '/' + videoIds[0] + '.html' });
                } else if (videoIds.length > 1) {
                    for (let i = 0; i < videoIds.length; i += 30) {
                        let batch = videoIds.slice(i, i + 30);
                        try {
                            let oUrl = 'https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238&appkey=6c03bbe9658448a4&union_platform=1&idlist=' + batch.join(',');
                            let oHtml = fetch(oUrl, fetch_params);
                            eval(oHtml);
                            if (QZOutputJson && QZOutputJson.results) {
                                QZOutputJson.results.forEach(function (it1) {
                                    it1 = it1.fields;
                                    let catStr = JSON.stringify(it1.category_map || []);
                                    if (catStr.indexOf('预告') < 0 && catStr.indexOf('花絮') < 0) {
                                        let url = 'https://v.qq.com/x/cover/' + vid + '/' + it1.vid + '.html';
                                        d.push({ title: it1.c_title_output || it1.title, url: url });
                                    }
                                });
                            }
                        } catch (e) { log('腾讯批量获取错误: ' + e.message); }
                    }
                }

            } else if (platform === 'iqiyi') {
                fetch_params.headers['User-Agent'] = PC_UA;
                let detailUrl = 'https://pcw-api.iqiyi.com/video/video/videoinfowithuser/' + vid + '?agent_type=1&authcookie=&subkey=' + vid + '&subscribe=1';
                let html = request(detailUrl);
                let json = JSON.parse(html).data || {};
                VOD.vod_name = json.name || '';
                VOD.vod_pic = json.imageUrl || '';
                let channelId = json.channelId || 0;
                let albumId = json.albumId || vid;

                let playlists = [];
                if (channelId === 1 || channelId === 5) {
                    playlists = [{ playUrl: json.playUrl, shortTitle: json.shortTitle || '正片' }];
                } else if (channelId === 6) {
                    try {
                        let qs = (json.period || '').split('-')[0];
                        let listUrl = 'https://pcw-api.iqiyi.com/album/source/svlistinfo?cid=6&sourceid=' + albumId + '&timelist=' + qs;
                        let playData = JSON.parse(request(listUrl)).data || {};
                        if (playData[qs]) {
                            playData[qs].forEach(function (it) {
                                playlists.push({ playUrl: it.playUrl, shortTitle: it.shortTitle });
                            });
                        }
                    } catch (e) { log('爱奇艺综艺错误: ' + e.message); }
                } else {
                    try {
                        let listUrl = 'https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid=' + albumId + '&size=200&page=1';
                        let listData = JSON.parse(request(listUrl)).data || {};
                        let epsodelist = listData.epsodelist || [];
                        let total = listData.total || 0;
                        if (total > 200) {
                            let totalPages = Math.ceil(total / 200);
                            for (let page = 2; page <= totalPages; page++) {
                                try {
                                    let pageUrl = 'https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid=' + albumId + '&size=200&page=' + page;
                                    epsodelist = epsodelist.concat((JSON.parse(request(pageUrl)).data || {}).epsodelist || []);
                                } catch (e) { break; }
                            }
                        }
                        playlists = epsodelist;
                    } catch (e) { log('爱奇艺剧集错误: ' + e.message); }
                }

                playlists.forEach(function (ep) {
                    let epUrl = ep.playUrl || '';
                    if (epUrl.startsWith('//')) epUrl = 'https:' + epUrl;
                    let title = ep.shortTitle || ('第' + (ep.order || '') + '集');
                    if (epUrl) d.push({ title: title, url: epUrl });
                });
            }
        } catch (e) { log('二级错误: ' + e.message); }

        VOD.vod_play_from = 'ATMB';
        VOD.vod_play_url = d.map(function (it) { return it.title + '$' + it.url; }).join('#');
        setResult(d);
    }),

    搜索: $js.toString(() => {
        let keyword = KEY;
        let PRIORITY = { 'mgtv': 0, 'bili': 1, 'qq': 2, 'iqiyi': 3 };
        if (typeof PC_UA === 'undefined') var PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

        function md5(s) {
            function rh(n, j) { var s32 = (n & 0xFFFF) + (j & 0xFFFF); var hi16 = (n >> 16) + (j >> 16) + (s32 >> 16); return (hi16 << 16) | (s32 & 0xFFFF); }
            function rol(n, c) { return (n << c) | (n >>> (32 - c)); }
            function cmn(q, a, b, x, s, t) { return rh(rol(rh(rh(a, q), rh(x, t)), s), b); }
            function ff(a, b, c, d, x, s, t) { return cmn((b & c) | ((~b) & d), a, b, x, s, t); }
            function gg(a, b, c, d, x, s, t) { return cmn((b & d) | (c & (~d)), a, b, x, s, t); }
            function hh(a, b, c, d, x, s, t) { return cmn(b ^ c ^ d, a, b, x, s, t); }
            function ii(a, b, c, d, x, s, t) { return cmn(c ^ (b | (~d)), a, b, x, s, t); }
            function coreMd5(x, len) {
                x[len >> 5] |= 0x80 << (len % 32);
                x[(((len + 64) >>> 9) << 4) + 14] = len;
                var a = 1732584193, b = -271733879, c = -1732584194, d = 271733878;
                for (var i = 0; i < x.length; i += 16) {
                    var oa = a, ob = b, oc = c, od = d;
                    a = ff(a, b, c, d, x[i], 7, -680876936); d = ff(d, a, b, c, x[i + 1], 12, -389564586); c = ff(c, d, a, b, x[i + 2], 17, 606105819); b = ff(b, c, d, a, x[i + 3], 22, -1044525330);
                    a = ff(a, b, c, d, x[i + 4], 7, -176418897); d = ff(d, a, b, c, x[i + 5], 12, 1200080426); c = ff(c, d, a, b, x[i + 6], 17, -1473231341); b = ff(b, c, d, a, x[i + 7], 22, -45705983);
                    a = ff(a, b, c, d, x[i + 8], 7, 1770035416); d = ff(d, a, b, c, x[i + 9], 12, -1958414417); c = ff(c, d, a, b, x[i + 10], 17, -42063); b = ff(b, c, d, a, x[i + 11], 22, -1990404162);
                    a = ff(a, b, c, d, x[i + 12], 7, 1804603682); d = ff(d, a, b, c, x[i + 13], 12, -40341101); c = ff(c, d, a, b, x[i + 14], 17, -1502002290); b = ff(b, c, d, a, x[i + 15], 22, 1236535329);
                    a = gg(a, b, c, d, x[i + 1], 5, -165796510); d = gg(d, a, b, c, x[i + 6], 9, -1069501632); c = gg(c, d, a, b, x[i + 11], 14, 643717713); b = gg(b, c, d, a, x[i], 20, -373897302);
                    a = gg(a, b, c, d, x[i + 5], 5, -701558691); d = gg(d, a, b, c, x[i + 10], 9, 38016083); c = gg(c, d, a, b, x[i + 15], 14, -660478335); b = gg(b, c, d, a, x[i + 4], 20, -405537848);
                    a = gg(a, b, c, d, x[i + 9], 5, 568446438); d = gg(d, a, b, c, x[i + 14], 9, -1019803690); c = gg(c, d, a, b, x[i + 3], 14, -187363961); b = gg(b, c, d, a, x[i + 8], 20, 1163531501);
                    a = gg(a, b, c, d, x[i + 13], 5, -1444681467); d = gg(d, a, b, c, x[i + 2], 9, -51403784); c = gg(c, d, a, b, x[i + 7], 14, 1735328473); b = gg(b, c, d, a, x[i + 12], 20, -1926607734);
                    a = hh(a, b, c, d, x[i + 5], 4, -378558); d = hh(d, a, b, c, x[i + 8], 11, -2022574463); c = hh(c, d, a, b, x[i + 11], 16, 1839030562); b = hh(b, c, d, a, x[i + 14], 23, -35309556);
                    a = hh(a, b, c, d, x[i + 1], 4, -1530992060); d = hh(d, a, b, c, x[i + 4], 11, 1272893353); c = hh(c, d, a, b, x[i + 7], 16, -155497632); b = hh(b, c, d, a, x[i + 10], 23, -1094730640);
                    a = hh(a, b, c, d, x[i + 13], 4, 681279174); d = hh(d, a, b, c, x[i], 11, -358537222); c = hh(c, d, a, b, x[i + 3], 16, -722521979); b = hh(b, c, d, a, x[i + 6], 23, 76029189);
                    a = hh(a, b, c, d, x[i + 9], 4, -640364487); d = hh(d, a, b, c, x[i + 12], 11, -421815835); c = hh(c, d, a, b, x[i + 15], 16, 530742520); b = hh(b, c, d, a, x[i + 2], 23, -995338651);
                    a = ii(a, b, c, d, x[i], 6, -198630844); d = ii(d, a, b, c, x[i + 7], 10, 1126891415); c = ii(c, d, a, b, x[i + 14], 15, -1416354905); b = ii(b, c, d, a, x[i + 5], 21, -57434055);
                    a = ii(a, b, c, d, x[i + 12], 6, 1700485571); d = ii(d, a, b, c, x[i + 3], 10, -1894986606); c = ii(c, d, a, b, x[i + 10], 15, -1051523); b = ii(b, c, d, a, x[i + 1], 21, -2054922799);
                    a = ii(a, b, c, d, x[i + 8], 6, 1873313359); d = ii(d, a, b, c, x[i + 15], 10, -30611744); c = ii(c, d, a, b, x[i + 6], 15, -1560198380); b = ii(b, c, d, a, x[i + 13], 21, 1309151649);
                    a = ii(a, b, c, d, x[i + 4], 6, -145523070); d = ii(d, a, b, c, x[i + 11], 10, -1120210379); c = ii(c, d, a, b, x[i + 2], 15, 718787259); b = ii(b, c, d, a, x[i + 9], 21, -343485551);
                    a = rh(a, oa); b = rh(b, ob); c = rh(c, oc); d = rh(d, od);
                }
                return [a, b, c, d];
            }
            function rawToHex(raw) {
                var hex = '0123456789abcdef', str = '';
                for (var i = 0; i < raw.length * 4; i++) {
                    str += hex.charAt((raw[i >> 2] >> ((i % 4) * 8 + 4)) & 0x0F) + hex.charAt((raw[i >> 2] >> ((i % 4) * 8)) & 0x0F);
                }
                return str;
            }
            function rawToStr(raw) {
                var str = '';
                for (var i = 0; i < raw.length * 4; i++) {
                    str += String.fromCharCode((raw[i >> 2] >> ((i % 4) * 8)) & 0xFF);
                }
                return str;
            }
            function strToRaw(str) {
                var raw = [];
                for (var i = 0; i < str.length * 8; i += 8) {
                    raw[i >> 5] |= (str.charCodeAt(i / 8) & 0xFF) << (i % 32);
                }
                return raw;
            }
            function utf8Encode(str) {
                var utftext = '', start = 0, end = 0;
                for (var n = 0; n < str.length; n++) {
                    var c = str.charCodeAt(n);
                    if (c < 128) end++;
                    else if (c > 127 && c < 2048) end += 2;
                    else end += 3;
                }
                utftext = new Array(end);
                for (n = 0; n < str.length; n++) {
                    c = str.charCodeAt(n);
                    if (c < 128) utftext[start++] = String.fromCharCode(c);
                    else if (c > 127 && c < 2048) {
                        utftext[start++] = String.fromCharCode((c >> 6) | 192);
                        utftext[start++] = String.fromCharCode((c & 63) | 128);
                    } else {
                        utftext[start++] = String.fromCharCode((c >> 12) | 224);
                        utftext[start++] = String.fromCharCode(((c >> 6) & 63) | 128);
                        utftext[start++] = String.fromCharCode((c & 63) | 128);
                    }
                }
                return utftext.join('');
            }
            return rawToHex(coreMd5(strToRaw(utf8Encode(s)), s.length * 8));
        }

        function normTitle(t) {
            if (!t) return '';
            return t.replace(/<[^>]+>/g, '').replace(/[\s\p{P}]/gu, '').toLowerCase();
        }
        function cleanTitle(t) {
            if (!t) return '';
            return t.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
        }
        function mergeResults(results, kw) {
            let normKw = normTitle(kw);
            function matchScore(title) {
                let t = normTitle(title);
                if (!t) return 0;
                if (t === normKw) return 100;
                if (t.indexOf(normKw) === 0) return 80;
                if (t.indexOf(normKw) > -1) return 60;
                return 0;
            }
            let filtered = results.filter(function (item) {
                let t = cleanTitle(item.title);
                if (!t || t.length < 2) return false;
                if (t.indexOf('<') > -1 || t.indexOf('>') > -1) return false;
                let desc = item.desc || '';
                if (desc.indexOf('全网搜') > -1 || desc.indexOf('外站') > -1) return false;
                let pf = item.url.split('__')[0];
                if (pf === 'qq' || pf === 'mgtv') {
                    if (/[《》]/.test(t)) return false;
                }
                item.title = t;
                return matchScore(t) > 0;
            });
            filtered.sort(function (a, b) {
                let sa = matchScore(a.title);
                let sb = matchScore(b.title);
                if (sb !== sa) return sb - sa;
                let ak = a.url.split('__')[0], bk = b.url.split('__')[0];
                let pa = PRIORITY[ak] !== undefined ? PRIORITY[ak] : 99;
                let pb = PRIORITY[bk] !== undefined ? PRIORITY[bk] : 99;
                return pa - pb;
            });
            return filtered;
        }

        let all = [];

        let FILTER_KW = ['预告', '花絮', '片花', '剪辑', '片段', '解说', '速看', '速通', '合集', '精彩', '集锦', '盘点', '回顾', 'MV', '主题曲', '插曲', '彩蛋', '特辑', '独家', '专访', '纯享', '制作', '幕后', '宣传', '反应', 'reaction', '名场面', '抢先看', '评测', 'cut', 'CUT', '音频', '原创', '深度', '解读', '看完', '分钟', '路透', '曝光', '造型', '片场', '背台词', '告别', '长文', '新剧', '公子', '呆萌', '仪态', '清冷', '温润', '仙气', '白衣', '古装', '高马尾', '蓝衣', '素衣', '青色'];
        function isMainContent(title) {
            if (!title) return false;
            // 只过滤《》括号（新闻/路透标题），不过滤其他括号（多季剧名可能带括号）
            if (/[《》]/.test(title)) return false;
            return !FILTER_KW.some(function (kw) { return title.indexOf(kw) > -1; });
        }

        let searchUa = (typeof PC_UA !== 'undefined' && PC_UA) ? PC_UA : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';
        let MGTV_SALT = 'xHAa3YZflWLogZUOzl';
        function searchUuid() {
            return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                let r = Math.random() * 16 | 0;
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
        }
        function buildMgtvSearchUrl() {
            let params = {
                allowedRC: '1', src: 'mgtv', did: 'cf03b95969454cb6bcb388762459354d',
                timestamp: new Date().toISOString().replace(/\.\d{3}Z/, 'Z'),
                signVersion: '1', signNonce: searchUuid(),
                q: keyword, pn: '1', pc: '10', corr: '1', _support: '10000000'
            };
            let keys = Object.keys(params).sort();
            let qs = keys.map(function (k) { return k + '=' + encodeURI(String(params[k])); }).join('&');
            return 'https://mobileso.bz.mgtv.com/pc/search/v2?' + qs + '&signature=' + md5(MGTV_SALT + qs + MGTV_SALT);
        }
        var BAK = '1d8b6e7d45233436';
        var BSC = '560c52ccd288fed045859ed18bffd973';
        function buildBiliSearchUrl(t) {
            let p = { appkey: BAK, build: '7000300', keyword: keyword, mobi_app: 'android', pagesize: 20, pn: 1, ts: Math.round(Date.now() / 1000), type: t };
            let ks = Object.keys(p).sort();
            let raw = ks.map(function (k) { return k + '=' + p[k]; }).join('&');
            let sg = md5(raw + BSC);
            let enc = ks.map(function (k) { return k + '=' + encodeURIComponent(p[k]); }).join('&');
            return 'https://app.bilibili.com/x/v2/search/type?' + enc + '&sign=' + sg;
        }
        let qqSearchUrl = 'https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2';
        let qqSearchBody = {
            "version": "25042201", "clientType": 1, "filterValue": "",
            "uuid": "B1E50847-D25F-4C4B-BBA0-36F0093487F6", "retry": 0,
            "query": keyword, "pagenum": 0, "isPrefetch": true, "pagesize": 30, "queryFrom": 0,
            "searchDatakey": "", "transInfo": "", "isneedQc": true, "preQid": "", "adClientInfo": "",
            "extraInfo": {"isNewMarkLabel": "1", "multi_terminal_pc": "1", "themeType": "1", "sugRelatedIds": "{}", "appVersion": ""}
        };
        let qqSearchHeaders = {
            'User-Agent': searchUa, 'Content-Type': 'application/json',
            'origin': 'https://v.qq.com', 'referer': 'https://v.qq.com/'
        };
        let iqiyiSearchUrl = 'https://search.video.iqiyi.com/o?if=html5&key=' + encodeURIComponent(keyword) + '&pageNum=1&pos=1&pageSize=30&site=iqiyi';
        let searchTasks = [
            { key: 'mgtv', url: buildMgtvSearchUrl(), options: { headers: { 'User-Agent': searchUa, 'Referer': 'https://www.mgtv.com' } } },
            { key: 'bili7', url: buildBiliSearchUrl(7), options: { headers: { 'User-Agent': searchUa, 'Referer': 'https://www.bilibili.com' } } }
        ];
        if (typeof batchFetch === 'function') {
            searchTasks.push({ key: 'bili8', url: buildBiliSearchUrl(8), options: { headers: { 'User-Agent': searchUa, 'Referer': 'https://www.bilibili.com' } } });
        }
        searchTasks.push(
            { key: 'qq', url: qqSearchUrl, options: { method: 'POST', headers: qqSearchHeaders, data: qqSearchBody }, fallbackOptions: { method: 'POST', headers: qqSearchHeaders, body: qqSearchBody }, jsonBody: true },
            { key: 'iqiyi', url: iqiyiSearchUrl, options: { headers: { 'User-Agent': searchUa } } }
        );
        let searchResponses = [];
        let searchBatched = false;
        if (typeof batchFetch === 'function') {
            try {
                searchResponses = batchFetch(searchTasks.map(function (task) { return { url: task.url, options: task.options || {} }; }));
                searchBatched = Array.isArray(searchResponses) && searchResponses.length === searchTasks.length;
            } catch (e) { log('搜索并发请求不可用，切换串行: ' + e.message); }
        }
        if (!searchBatched) {
            searchResponses = searchTasks.map(function (task) {
                try { return request(task.url, task.fallbackOptions || task.options || {}, task.jsonBody === true); }
                catch (e) { log(task.key + '搜索请求错误: ' + e.message); return ''; }
            });
        }
        let searchHtml = {};
        searchTasks.forEach(function (task, index) { searchHtml[task.key] = searchResponses[index] || ''; });

        try {
            let html = searchHtml.mgtv;
            let json = JSON.parse(html);

            if (json.data && json.data.contents) {
                json.data.contents.forEach(function (data) {
                    let d0 = data.data;
                    if (!d0 || typeof d0 !== 'object' || Array.isArray(d0)) return;
                    let cards = (d0.yearList && d0.yearList.length) ? d0.yearList : [d0];
                    cards.forEach(function (item) {
                        let title = cleanTitle(item.hitTitle || item.title || '');
                        let img = item.pic || '';
                        let vid = '';
                        let src = (item.sourceList && item.sourceList.length) ? item.sourceList[0] : null;
                        let pageUrl = (src && src.url) || item.url || '';
                        if (pageUrl.indexOf('/s/') > -1) return;
                        if (src) {
                            if (src.source !== 'imgo') return;
                            vid = src.vid ? String(src.vid) : '';
                            if (!vid) {
                                let m = String(pageUrl).match(/\/b\/\d+\/(\d+)\.html/);
                                if (m) vid = m[1];
                            }
                        } else if (item.vid) {
                            vid = String(item.vid);
                        }
                        if (!vid) {
                            let m = String(pageUrl).match(/\/b\/\d+\/(\d+)\.html/);
                            if (m) vid = m[1];
                        }
                        if (!vid || !title) return;
                        if (!isMainContent(title)) return;
                        let descParts = [];
                        if (Array.isArray(item.desc)) {
                            item.desc.forEach(function (x) {
                                if (x && (x.text || x.label)) descParts.push((x.label ? x.label + ':' : '') + (x.text || ''));
                            });
                        }
                        if (item.playTime) descParts.push(item.playTime);
                        let remark = item.updateInfo || descParts.join(',') || item.subtitle || '';
                        all.push({ title: title, img: img, pic_url: img, url: 'mgtv__' + vid, desc: '芒果' });
                    });
                });
            }
        } catch (e) { log('芒果搜索错误: ' + e.message); }

        try {
            function biliAppSearch(t, firstHtml) {
                let text = firstHtml;
                if (!text) text = request(buildBiliSearchUrl(t), { headers: { 'User-Agent': searchUa, 'Referer': 'https://www.bilibili.com' } });
                var jo = JSON.parse(text);
                if (jo && jo.code === 0 && jo.data && jo.data.items) return jo.data.items;
                return [];
            }
            var seen = {};
            function biliPush(items) {
                items.forEach(function (vod) {
                    var aid = vod.season_id;
                    if (aid === undefined || aid === null || aid === 0) return;
                    aid = (aid + '').trim();
                    if (seen[aid]) return;
                    seen[aid] = 1;
                    var title = (vod.title || '').replace(/<[^>]+>/g, '').trim();
                    var img = (vod.cover || '').trim();
                    var remark = (vod.new_ep && vod.new_ep.index_show) || vod.index_show || vod.styles || vod.badge || vod.season_type_name || '';
                    all.push({ title: title, img: img, pic_url: img, url: 'bili__' + aid, desc: '哔哩哔哩' });
                });
            }
            var biliItems7 = biliAppSearch(7, searchHtml.bili7);
            biliPush(biliItems7);
            var biliNormKeyword = normTitle(keyword);
            var biliHasExact = biliItems7.some(function (vod) {
                return normTitle((vod.title || '').replace(/<[^>]+>/g, '').trim()) === biliNormKeyword;
            });
            if (!biliHasExact) biliPush(biliAppSearch(8, searchHtml.bili8));
        } catch (e) { log('哔哩搜索错误: ' + e.message); }

        try {
            let html = searchHtml.qq;
            let json = JSON.parse(html);
            let itemList = [];
            if (json.data && json.data.normalList && json.data.normalList.itemList) {
                itemList = itemList.concat(json.data.normalList.itemList);
            }
            if (json.data && json.data.areaBoxList) {
                json.data.areaBoxList.forEach(function (box) {
                    if (box.itemList) itemList = itemList.concat(box.itemList);
                });
            }

            itemList.forEach(function (it) {
                if (it && it.videoInfo) {
                    let cid = (it.doc && it.doc.id) || it.videoInfo.cid || it.videoInfo.coverId || '';
                    if (!cid) return;
                    cid = String(cid);
                    let title = cleanTitle(it.videoInfo.title || '');
                    if (!title || title.indexOf('<') > -1 || title.indexOf('>') > -1) return;
                    if (!isMainContent(title)) return;
                    let viewType = it.videoInfo.viewType;
                    if (viewType !== 1 && viewType !== 25) return; 
                    let desc = it.videoInfo.secondLine || it.videoInfo.updateInfo || it.videoInfo.episodeUpdated || it.videoInfo.secondTitle || it.videoInfo.subTitle || '';
                    all.push({ title: title, img: it.videoInfo.imgUrl || it.videoInfo.pic || '', pic_url: it.videoInfo.imgUrl || it.videoInfo.pic || '', url: 'qq__' + cid, desc: '腾讯视频-4K' });
                }
            });
        } catch (e) { log('腾讯搜索错误: ' + e.message); }

        try {
            let html = searchHtml.iqiyi;
            let json = JSON.parse(html);
            let docinfos = json.data ? json.data.docinfos : [];
            let validCh = ['电影', '电视剧', '综艺', '动漫', '纪录片', '少儿', '短剧', '漫剧'];
            docinfos.forEach(function (doc) {
                let album = doc.albumDocInfo || {};
                let title = cleanTitle(album.albumTitle || '');
                let albumId = album.albumId || '';
                let pic = album.albumVImage || '';
                let channel = album.channel || '';
                if (!title || !albumId) return;
                if (!isMainContent(title)) return;
                if (!validCh.some(function (ch) { return channel.indexOf(ch) > -1; })) return;
                if (pic.startsWith('//')) pic = 'https:' + pic;
                let remark = '';
                let latest = album.latestOrder || 0;
                let total = album.videoCount || album.itemTotalNumber || 0;
                if (latest && total) {
                    remark = Number(latest) === Number(total) ? latest + '集全' : latest + '/' + total + '集';
                } else if (latest) {
                    remark = '更新至 ' + latest + '集';
                } else if (total) {
                    remark = '共' + total + '集';
                } else {
                    remark = album.period || album.focus || album.albumSubtitle || album.subTitle || '';
                }
                if (album.score) remark = album.score + '分\t' + remark;
                all.push({ title: title, img: pic, pic_url: pic, url: 'iqiyi__' + albumId, desc: '爱奇艺' });
            });
        } catch (e) { log('爱奇艺搜索错误: ' + e.message); }

        let merged = mergeResults(all, keyword);
        setResult(merged);
    }),
}
