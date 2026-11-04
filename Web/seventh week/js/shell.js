/* ==================================================================
   共享壳层：头部导航 + 页脚（含跑马灯）
   三页重复的 .head / .foot 区块由此脚本在原占位处同步渲染：
   - 同步执行（非 defer），DOM 解析到占位脚本时立即插入，
     保证与原先静态书写时相同的渲染结果，无首屏闪烁/布局跳动；
   - 导航高亮按当前页面路径自动判定，无需每页手工切 active；
   - 客服电话等取值一律来自 js/config.js（APP_CONFIG.get）。
   ================================================================== */
(function () {
    "use strict";

    var slotEl = document.currentScript;
    var slot = slotEl && slotEl.getAttribute("data-shell");
    if (!slot || !window.APP_CONFIG) return;

    var PHONE = window.APP_CONFIG.get("phone");

    /* 头部导航项：match 为对应页面关键字（order 页与列表页同样高亮「国际租车」） */
    var NAV_ITEMS = [
        { href: "./index.html", label: "首页", match: "index" },
        { href: "./international.html", label: "国际租车", match: "international" },
        { href: "#", label: "闪租", match: "" },
        { href: "#", label: "服务项目", match: "" },
        { href: "#", label: "关于我们", match: "" }
    ];

    /* 跑马灯文案：无缝滚动由两组相同内容拼接 */
    var TICKER_LINES = [
        "京A·23F86 已于 2 分钟前在首都机场 T3 交付",
        "沪C·80K12 预计 14:00 抵达虹桥火车站店",
        "粤B·31P66 完成保养，重新上架待租",
        "川A·9Q208 由成都天府店调往双流机场店",
        "今日车队出租率 87% · 中文客服在线 6 人"
    ];

    /* 页脚栏目 */
    var FOOT_COLS = [
        { title: "关于悦行网", links: ["关于我们", "联系我们", "加入我们", "品牌故事"] },
        { title: "条款", links: ["隐私条款", "用户协议", "租车须知"] },
        { title: "帮助", links: ["客服中心", "互问互答", "常见问题"] },
        { title: "关于服务", links: ["服务时间", "短租及可选服务"] }
    ];

    /* 当前页对应的导航高亮项：首页 → index；订单页/国际页 → international */
    function activeMatch() {
        var path = location.pathname.toLowerCase();
        if (path.indexOf("order") !== -1 || path.indexOf("international") !== -1) return "international";
        return "index";
    }

    function renderHeader() {
        var match = activeMatch();
        var lis = NAV_ITEMS.map(function (item) {
            var cls = item.match && item.match === match ? ' class="active"' : "";
            return '                <li' + cls + '><a href="' + item.href + '">' + item.label + "</a></li>";
        }).join("\n");

        var html = "\n" +
            '    <div class="head">\n' +
            '        <div class="logo">\n' +
            '            <span class="logo-en">CARECAR</span>\n' +
            '            <span class="logo-cn">悦行网</span>\n' +
            "        </div>\n" +
            '        <div class="nav">\n' +
            "            <ul>\n" +
            lis + "\n" +
            "            </ul>\n" +
            "        </div>\n" +
            '        <div class="login">\n' +
            '            <a href="#" class="btn">登录 / 注册</a>\n' +
            '            <span class="phone">' + PHONE + "</span>\n" +
            "        </div>\n" +
            "    </div>\n";

        slotEl.insertAdjacentHTML("afterend", html);
    }

    function tickerGroupHTML(indent) {
        return TICKER_LINES.map(function (line) {
            return indent + "<span>" + line + "</span>";
        }).join("\n");
    }

    function footColHTML(col) {
        return "                <div class=\"foot-col\">\n" +
            "                    <h3 class=\"foot-title\">" + col.title + "</h3>\n" +
            "                    <ul class=\"foot-links\">\n" +
            col.links.map(function (link) {
                return "                        <li><a href=\"#\">" + link + "</a></li>";
            }).join("\n") + "\n" +
            "                    </ul>\n" +
            "                </div>";
    }

    function renderFooter() {
        var group =
            "                    <div class=\"ticker-group\">\n" +
            tickerGroupHTML("                        ") + "\n" +
            "                    </div>";

        var cols = FOOT_COLS.map(footColHTML).join("\n");

        var html = "\n" +
            "        <div class=\"foot\">\n" +
            "            <div class=\"ticker\" aria-hidden=\"true\">\n" +
            "                <div class=\"ticker-track\">\n" +
            group + "\n" +
            group + "\n" +
            "                </div>\n" +
            "            </div>\n" +
            "            <div class=\"foot-inner\">\n" +
            cols + "\n" +
            "                <div class=\"foot-col foot-qr\">\n" +
            "                    <h3 class=\"foot-title\">微信公众号</h3>\n" +
            "                    <img src=\"./images/wechrt.png\" alt=\"微信公众号二维码\" loading=\"lazy\">\n" +
            "                </div>\n" +
            "            </div>\n" +
            "            <div class=\"foot-bottom\">\n" +
            "                <p>© 2026 悦行网 CARECAR · 本页面为学习演示用途</p>\n" +
            "                <span class=\"foot-sys\">FLEET CONSOLE · 24H ROADSIDE ASSISTANCE " + PHONE + "</span>\n" +
            "            </div>\n" +
            "        </div>\n";

        slotEl.insertAdjacentHTML("afterend", html);
    }

    if (slot === "header") {
        renderHeader();
    } else if (slot === "footer") {
        renderFooter();
    }

    /* 占位脚本完成使命后移除，保持 DOM 与原先静态书写一致 */
    if (slotEl.parentNode) slotEl.parentNode.removeChild(slotEl);
})();
