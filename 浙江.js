// 引入 geetest.0.0.0.js
const geet = require('./geetest.0.0.0.js'); // 确保路径正确
let timestamp = new Date().getTime();

function main (c, d, e) {
        // var f = a.b("x_pos", timestamp);
        var f = func_a_b("x_pos", timestamp);
        return c >= f - 3 && c <= f + 3 ? {
            success: !0,
            message: "success",
            // validate: b.A(c,e.d.challenge) + "_" + b.A(a.b("rand0", timestamp), e.d.challenge) + "_" + b.A(a.b("rand1", timestamp), e.d.challenge),
            validate: func_b_A(c,e.d.challenge) + "_" + func_b_A(func_a_b("rand0", timestamp), e.d.challenge) + "_" + func_b_A(func_a_b("rand1", timestamp), e.d.challenge),
            score: Math.round(d / 200)
        } : {
            success: 0,
            message: "fail"
        }
    }
main(145, 953, {
    "c": timestamp,
    "d": {
        "challenge": "d9d4f495e875a2e075a1a4a6e1b9770f37",
        "type": "slide",
        "fullbg": "pictures/gt/cfcd20849/cfcd20849.jpg",
        "bg": "pictures/gt/cfcd20849/bg/8e5646ef5.jpg",
        "slice": "pictures/gt/cfcd20849/slice/8e5646ef5.png",
        "xpos": 0,
        "ypos": 14,
        "height": 116,
        "link": "javascript:;",
        "https": true,
        "logo": true,
        "product": "popup",
        "id": "",
        "version": "6.0.0",
        "theme": "golden",
        "theme_version": "3.2.0",
        "show_delay": 250,
        "hide_delay": 800,
        "lang": "zh-cn",
        "clean": false,
        "protocol": "https://",
        "api_server": "api.geetest.com",
        "static_servers": [
            "static.geetest.com",
            "dn-staticdown.qbox.me"
        ],
        "retry": 0,
        "debugConfig": {},
        "gt": "55f458c56d1671abd7ba7402ab845a9c",
        "offline": true,
        "slide": "/static/js/geetest.0.0.0.js"
    },
    "B": "https://gl.jtyst.zj.gov.cn/zjyz/gzcx/yyclcx/service.html",
    "dom": {
        "c": "geetest_1744599379566"
    }
})
