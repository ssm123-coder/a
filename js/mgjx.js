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
    url: '/rider/list/pcweb/v3?platform=pcweb&channelId=fyclass&pn=fypage&pc=80&hudong=1&_support=10000000&kind=a1&area=a1',
    filter_url: 'year={{fl.year or "all"}}&sort={{fl.sort or "all"}}&chargeInfo={{fl.chargeInfo or "all"}}',
    parse_url: [
        "http://106.12.191.132:520/Mg.php?url=",
        "https://test1.12321app.com/daoliansiquanjia.php?url=",
        "http://jiexi.fc8001.top/tJYtHAIRQdMaWdKF.php?url=",
        "https://niubi.69mini.com/api/?key=de8570d02b2e5181978a6c47a8eb4d91&url=",
        "https://jx.xmflv.com/?url="
            ],
    blocked_urls: [
        '播放失败，换其他源！'
    ],
    headers: {
        'User-Agent': 'PC_UA'
    },
    timeout: 5000,
    class_name: '\u7535\u89c6\u5267\u0026\u7535\u5f71\u0026\u7efc\u827a\u0026\u5c11\u513f\u0026\u7eaa\u5f55\u7247',
    class_url: '\u0032\u0026\u0033\u0026\u0031\u0026\u0031\u0030\u0026\u0035\u0031',
    filter: {
        "2": getCommonFilter(),
        "3": getCommonFilter(),
        "1": getCommonFilter(),
        "10": getCommonFilter(),
        "51": getCommonFilter()
    },
    limit: 20,
    play_parse: true,
    lazy: $js.toString(() => {
        let apiList = rule.parse_url;
        let targetSrc = input.split("?")[0];
        let finalUrl = null;
        function isBad(u) {
            if(!u) return true;
            return rule.blocked_urls.some(b => u.includes(b));
        }
        for(let i=0;i<apiList.length;i++){
            try{
                let fullApi = apiList[i] + encodeURIComponent(targetSrc);
                let resText = fetch(fullApi,{
                    method:"GET",
                    headers:{
                        "User-Agent":"Mozilla/5.0",
                        "Referer":"https://www.mgtv.com/"
                    },
                    timeout:6000
                });
                let ret = JSON.parse(resText);
                let playUrl = ret.url || ret.data || ret.result;
                if(playUrl && playUrl.startsWith("http") && !isBad(playUrl)){
                    finalUrl = playUrl;
                    break;
                }
            }catch(err){
                continue;
            }
        }
        if(finalUrl){
            input = {
                header:{"User-Agent":""},
                parse:0,
                url:finalUrl,
                jx:0,
                danmaku:'http://127.0.0.1:9978/proxy?do=danmu&site=js&url=' + targetSrc
            };
        }else{
            input = {
                header:{"User-Agent":""},
                parse:0,
                url:targetSrc,
                jx:1,
                danmaku:'http://127.0.0.1:9978/proxy?do=danmu&site=js&url=' + targetSrc
            };
        }
    }),
    一级: 'json:data.hitDocs;title;img;updateInfo||rightCorner.text;playPartId',
    二级: $js.toString(() => {
        fetch_params.headers.Referer = "https://www.mgtv.com";
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        let videoId = input.split('video_id=')[1].split('&')[0];
        let infoUrl = `https://pcweb.api.mgtv.com/video/info?allowedRC=1&vid=${videoId}&type=b&_support=10000000`;
        let infoData = JSON.parse(request(infoUrl));
        if (infoData && infoData.data && infoData.data.info) {
            let detail = infoData.data.info.detail || {};
            VOD = {
                vod_name: infoData.data.info.title || "",
                type_name: detail.kind || "",
                vod_year: detail.releaseTime || "",
                vod_area: detail.area || "",
                vod_actor: detail.leader || "",
                vod_director: detail.director || "",
                vod_content: detail.story || "",
                vod_remarks: detail.updateInfo || ""
            };
            if (detail.img) VOD.vod_pic = detail.img;
        }
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let host = "https://www.mgtv.com";
        let ourl = json.data.list.length > 0 ? json.data.list[0].url : json.data.series[0].url;
        if (!/^http/.test(ourl)) ourl = host + ourl;
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        html = request(ourl);
        if (html.includes("window.location =")) {
            ourl = pdfh(html, "meta[http-equiv=refresh]&&content").split("url=")[1];
            html = request(ourl);
        }
        try {
            let details = pdfh(html, ".m-details&&Html").replace(/h1>/, "h6>").replace(/div/g, "br");
            let actor = "",
                director = "",
                time = "";
            if (/播出时间/.test(details)) {
                actor = pdfh(html, "p:eq(5)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(4)&&Text");
                time = pdfh(html, "p:eq(3)&&Text");
            } else {
                actor = pdfh(html, "p:eq(4)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(3)&&Text");
                time = "已完结";
            }
            let _img = pd(html, ".video-img&&img&&src");
            let JJ = pdfh(html, ".desc&&Text").split("简介：")[1];
            VOD.vod_name = VOD.vod_name || pdfh(html, ".vt-txt&&Text");
            VOD.type_name = VOD.type_name || pdfh(html, "p:eq(0)&&Text").substr(0, 6);
            VOD.vod_area = VOD.vod_area || pdfh(html, "p:eq(1)&&Text");
            VOD.vod_actor = VOD.vod_actor || actor;
            VOD.vod_director = VOD.vod_director || director;
            VOD.vod_remarks = VOD.vod_remarks || time;
            VOD.vod_pic = VOD.vod_pic || _img;
            VOD.vod_content = VOD.vod_content || JJ;
            if (!VOD.vod_name) VOD.vod_name = VOD.type_name;
        } catch (e) {
            log("获取影片信息发生错误:" + e.message);
        }
        function getRjpg(imgUrl, xs) {
            xs = xs || 3;
            let picSize = /jpg_/.test(imgUrl) ? imgUrl.split("jpg_")[1].split(".")[0] : false;
            let rjpg = false;
            if (picSize) {
                let a = parseInt(picSize.split("x")[0]) * xs;
                let b = parseInt(picSize.split("x")[1]) * xs;
                rjpg = a + "x" + b + ".jpg";
            }
            return /jpg_/.test(imgUrl) && rjpg ? imgUrl.replace(imgUrl.split("jpg_")[1], rjpg) : imgUrl;
        }
        if (json.data.total === 1 && json.data.list.length === 1) {
            let data = json.data.list[0];
            d.push({
                title: data.t4,
                desc: data.t2,
                pic_url: getRjpg(data.img),
                url: "https://www.mgtv.com" + data.url
            });
        } else if (json.data.list.length > 1) {
            for (let i = 1; i <= json.data.total_page; i++) {
                if (i > 1) json = JSON.parse(fetch(input.replace("page=1", "page=" + i), {}));
                json.data.list.forEach(function(data) {
                    if (data.isIntact == "1") {
                        d.push({
                            title: data.t4,
                            desc: data.t2,
                            pic_url: getRjpg(data.img),
                            url: "https://www.mgtv.com" + data.url
                        });
                    }
                });
            }
        } else {
            print(input + "暂无片源");
        }
        VOD.vod_play_from = "\u6052\u8f69";
        VOD.vod_play_url = d.map(function(it) {
            return it.title + "$" + it.url;
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
    })
};
function getCommonFilter() {
    return [{
        "key": "chargeInfo",
        "name": "付费类型",
        "value": [{
                "n": "全部",
                "v": "all"
            },
            {
                "n": "免费",
                "v": "b1"
            },
            {
                "n": "vip",
                "v": "b2"
            }
        ]
    }, {
        "key": "sort",
        "name": "排序",
        "value": [{
                "n": "最新",
                "v": "c1"
            },
            {
                "n": "最热",
                "v": "c2"
            },
            {
                "n": "知乎高分",
                "v": "c4"
            }
        ]
    }, {
        "key": "year",
        "name": "年代",
        "value": [{
                "n": "全部",
                "v": "all"
            },
            {
                "n": "2026",
                "v": "2026"
            },
            {
                "n": "2025",
                "v": "2025"
            },
            {
                "n": "2024",
                "v": "2024"
            },
            {
                "n": "2023",
                "v": "2023"
            },
            {
                "n": "2022",
                "v": "2022"
            },
            {
                "n": "2021",
                "v": "2021"
            },
            {
                "n": "2020",
                "v": "2020"
            },
            {
                "n": "2019",
                "v": "2019"
            },
            {
                "n": "2018",
                "v": "2018"
            },
            {
                "n": "2017",
                "v": "2017"
            },
            {
                "n": "2016",
                "v": "2016"
            },
            {
                "n": "2015",
                "v": "2015"
            },
            {
                "n": "2014",
                "v": "2014"
            },
            {
                "n": "2013",
                "v": "2013"
            },
            {
                "n": "2012",
                "v": "2012"
            },
            {
                "n": "2011",
                "v": "2011"
            },
            {
                "n": "2010",
                "v": "2010"
            },
            {
                "n": "2009",
                "v": "2009"
            },
            {
                "n": "2008",
                "v": "2008"
            },
            {
                "n": "2007",
                "v": "2007"
            },
            {
                "n": "2006",
                "v": "2006"
            },
            {
                "n": "2005",
                "v": "2005"
            },
            {
                "n": "2004",
                "v": "2004"
            }
        ]
    }];
}
