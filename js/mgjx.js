var rule = {
    title: '百忙无果[官]',
    host: 'https://pianku.api.mgtv.com',
    homeUrl: '',
    searchUrl: 'https://mobileso.bz.mgtv.com/applet/search/v1?channelCode=mobile-wxap&q=**&pn=fypage&pc=10&_support=10000000',
    detailUrl: 'https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=fyid',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    multi: 1,
    url: '/rider/list/pcweb/v3?platform=pcweb&channelId=fyclass&pn=fypage&pc=80&hudong=1&_support=10000000&{{fl.kind}}&{{fl.area}}',
    filter_url: 'year={{fl.year or "all"}}&sort={{fl.sort or "all"}}&chargeInfo={{fl.chargeInfo or "all"}}',
    headers: {
        'User-Agent': 'PC_UA'
    },
    timeout: 5000,
    class_name: '电视剧&电影&综艺&动漫&纪录片&教育&少儿',
    class_url: '2&3&1&50&51&115&10',
    filter: {
        "3": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ],
        "2": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ],
        "1": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ],
        "5": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ],
        "11": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ],
        "115": [
            {
                "key": "chargeInfo",
                "name": "付费类型",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "免费", "v": "b1"},
                    {"n": "VIP", "v": "b2"},
                    {"n": "VIP用券", "v": "b3"},
                    {"n": "付费点播", "v": "b4"}
                ]
            },
            {
                "key": "sort",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "c1"},
                    {"n": "最热", "v": "c2"},
                    {"n": "知乎高分", "v": "c4"}
                ]
            },
            {
                "key": "year",
                "name": "年代",
                "value": [
                    {"n": "全部", "v": "all"},
                    {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"},
                    {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"},
                    {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"},
                    {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"},
                    {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"},
                    {"n": "2010", "v": "2010"}
                ]
            }
        ]
    },
    limit: 20,
    play_parse: true,
lazy: $js.toString(() => {
    
    let apiList = [
        'http://106.12.191.132:520/Mg.php?url=',
        'https://test1.12321app.com/daoliansiquanjia.php?url=',
        'https://v.gimy.bot/jx/api.php?url='
    ];
    
    let videoUrl = input.split("?")[0];
    let success = false;
    let result = null;
    
    let danmakuUrl = 'http://127.0.0.1:9997/proxy?do=' + input.split("?")[0];
    
    for (let i = 0; i < apiList.length; i++) {
        try {
            let api = apiList[i] + videoUrl;
            console.log("尝试解析接口 " + (i + 1) + ": " + api);
            
            let response = fetch(api, {
                method: 'get',
                headers: {
                    'User-Agent': 'okhttp/3.14.9',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            
            let bata = JSON.parse(response);
            log(bata);
            
            // 判断是否解析成功
            if (bata.url && bata.url.length > 0) {
                result = bata;
                success = true;
                console.log("接口 " + (i + 1) + " 解析成功");
                break;
            }
        } catch (e) {
            console.log("接口 " + (i + 1) + " 解析失败: " + e.message);
            continue;
        }
    }
    
    // 如果所有接口都失败
    if (!success || !result) {
        input = {
            header: {
                'User-Agent': ''
            },
            parse: 0,
            url: videoUrl,
            jx: 1,
            danmaku: danmakuUrl
        };
    } else {
        // 解析成功
        if (result.url.includes("http")) {
            input = {
                header: {
                    'User-Agent': ''
                },
                parse: 0,
                url: result.url,
                jx: 0,
                danmaku: danmakuUrl
            };
        } else {
            input = {
                header: {
                    'User-Agent': ''
                },
                parse: 0,
                url: videoUrl,
                jx: 1,
                danmaku: danmakuUrl
            };
        }
    }
}),
    推荐: '.list_item;img&&alt;img&&src;a&&Text;a&&data-float',
    一级: 'json:data.hitDocs;title;img;updateInfo||rightCorner.text;playPartId',
    二级: $js.toString(() => {
        fetch_params.headers.Referer = "https://www.mgtv.com";
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        VOD = {};
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let host = "https://www.mgtv.com";
        let ourl = json.data.list.length > 0 ? json.data.list[0].url : json.data.series[0].url;
        if (!/^http/.test(ourl)) {
            ourl = host + ourl
        }
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        html = request(ourl);
        if (html.includes("window.location =")) {
            print("开始获取ourl");
            ourl = pdfh(html, "meta[http-equiv=refresh]&&content").split("url=")[1];
            print("获取到ourl:" + ourl);
            html = request(ourl)
        }
        try {
            let details = pdfh(html, ".m-details&&Html").replace(/h1>/, "h6>").replace(/div/g, "br");
            print(details);
            let actor = "",
                director = "",
                time = "";
            if (/播出时间/.test(details)) {
                actor = pdfh(html, "p:eq(5)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(4)&&Text");
                time = pdfh(html, "p:eq(3)&&Text")
            } else {
                actor = pdfh(html, "p:eq(4)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(3)&&Text");
                time = "已完结"
            }
            let _img = pd(html, ".video-img&&img&&src");
            let JJ = pdfh(html, ".desc&&Text").split("简介：")[1];
            let _desc = time;
            VOD.vod_name = pdfh(html, ".vt-txt&&Text");
            VOD.type_name = pdfh(html, "p:eq(0)&&Text").substr(0, 6);
            VOD.vod_area = pdfh(html, "p:eq(1)&&Text");
            VOD.vod_actor = actor;
            VOD.vod_director = director;
            VOD.vod_remarks = _desc;
            VOD.vod_pic = _img;
            VOD.vod_content = JJ;
            if (!VOD.vod_name) {
                VOD.vod_name = VOD.type_name;
            }
        } catch (e) {
            log("获取影片信息发生错误:" + e.message)
        }
        function getRjpg(imgUrl, xs) {
            xs = xs || 3;
            let picSize = /jpg_/.test(imgUrl) ? imgUrl.split("jpg_")[1].split(".")[0] : false;
            let rjpg = false;
            if (picSize) {
                let a = parseInt(picSize.split("x")[0]) * xs;
                let b = parseInt(picSize.split("x")[1]) * xs;
                rjpg = a + "x" + b + ".jpg"
            }
            let img = /jpg_/.test(imgUrl) && rjpg ? imgUrl.replace(imgUrl.split("jpg_")[1], rjpg) : imgUrl;
            return img
        }
        if (json.data.total === 1 && json.data.list.length === 1) {
            let data = json.data.list[0];
            let url = "https://www.mgtv.com" + data.url;
            d.push({
                title: data.t4,
                desc: data.t2,
                pic_url: getRjpg(data.img),
                url: url
            })
        } else if (json.data.list.length > 1) {
            for (let i = 1; i <= json.data.total_page; i++) {
                if (i > 1) {
                    json = JSON.parse(fetch(input.replace("page=1", "page=" + i), {}))
                }
                json.data.list.forEach(function(data) {
                    let url = "https://www.mgtv.com" + data.url;
                    if (data.isIntact == "1") {
                        d.push({
                            title: data.t4,
                            desc: data.t2,
                            pic_url: getRjpg(data.img),
                            url: url
                        })
                    }
                })
            }
        } else {
            print(input + "暂无片源")
        }
        VOD.vod_play_from = "芒果TV";
        VOD.vod_play_url = d.map(function(it) {
            return it.title + "$" + it.url
        }).join("#");
        setResult(d);
    }),
    搜索: $js.toString(() => {
        fetch_params.headers.Referer = "https://www.mgtv.com";
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let contents = json?.data?.contents || [];
        for(let i of contents){
            if(!i.data || !i.data.length) continue;
            let item = i.data[0];
            if(!item.vid || !item.img) continue;
            let desc = Array.isArray(i.desc) ? i.desc.join(',') : '';
            d.push({
                title: item.title.replace(/<B>|<\/B>/g, ''),
                img: item.img,
                content: '',
                desc: desc,
                url: item.vid
            })
        }
        setResult(d);
    }),
}
