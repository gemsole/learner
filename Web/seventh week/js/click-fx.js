/* 随机点击特效：在页面任意位置点击后，随机弹出一颗爱心 / 星星 / 小动物 / 有趣表情，
   向上飘散、摇摆并渐隐。每次点击随机选择类别、样式（可上色的文本字符 / 多彩表情）、
   颜色、大小、旋转角度、上升高度、左右摇摆幅度、缩放节奏、时长与缓动，
   偶尔一次弹出两颗，保证每次都不重样。 */
(function () {
    "use strict";

    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

    /* 特效类别池：每类是一组字符，colorable 为 true 的可用 color 上色，false 的为自带多彩的表情 */
    var CATEGORIES = [
        /* 爱心 */
        [
            { ch: "\u2665", colorable: true },              // ♥  实心，可染色
            { ch: "\u2661", colorable: true },              // ♡  空心，可染色
            { ch: "\u2764\uFE0F", colorable: false },       // ❤️
            { ch: "\uD83D\uDC96", colorable: false },       // 💖
            { ch: "\uD83D\uDC95", colorable: false },       // 💕
            { ch: "\uD83D\uDC97", colorable: false },       // 💗
            { ch: "\uD83D\uDC98", colorable: false },       // 💘
            { ch: "\uD83D\uDC9D", colorable: false },       // 💝
            { ch: "\uD83E\uDE77", colorable: false }        // 🩷
        ],
        /* 星星 */
        [
            { ch: "\u2605", colorable: true },              // ★  实心，可染色
            { ch: "\u2606", colorable: true },              // ☆  空心，可染色
            { ch: "\u2B50", colorable: false },             // ⭐
            { ch: "\uD83C\uDF1F", colorable: false },       // 🌟
            { ch: "\u2728", colorable: false },             // ✨
            { ch: "\uD83D\uDCAB", colorable: false }        // 💫
        ],
        /* 小动物 */
        [
            { ch: "\uD83D\uDC31", colorable: false },       // 🐱
            { ch: "\uD83D\uDC36", colorable: false },       // 🐶
            { ch: "\uD83D\uDC30", colorable: false },       // 🐰
            { ch: "\uD83D\uDC3B", colorable: false },       // 🐻
            { ch: "\uD83D\uDC3C", colorable: false },       // 🐼
            { ch: "\uD83E\uDD8A", colorable: false },       // 🦊
            { ch: "\uD83D\uDC38", colorable: false },       // 🐸
            { ch: "\uD83D\uDC25", colorable: false },       // 🐥
            { ch: "\uD83E\uDD84", colorable: false },       // 🦄
            { ch: "\uD83D\uDC28", colorable: false },       // 🐨
            { ch: "\uD83D\uDC37", colorable: false },       // 🐷
            { ch: "\uD83D\uDC39", colorable: false }        // 🐹
        ],
        /* 随机表情 */
        [
            { ch: "\uD83C\uDF88", colorable: false },       // 🎈
            { ch: "\uD83C\uDF89", colorable: false },       // 🎉
            { ch: "\uD83C\uDF40", colorable: false },       // 🍀
            { ch: "\uD83C\uDF08", colorable: false },       // 🌈
            { ch: "\u2618\uFE0F", colorable: false },       // ☘️
            { ch: "\uD83C\uDF38", colorable: false },       // 🌸
            { ch: "\uD83C\uDF3B", colorable: false },       // 🌻
            { ch: "\uD83C\uDF6D", colorable: false },       // 🍭
            { ch: "\uD83D\uDC4D", colorable: false },       // 👍
            { ch: "\uD83D\uDC4F", colorable: false },       // 👏
            { ch: "\uD83C\uDFB5", colorable: false },       // 🎵
            { ch: "\uD83C\uDF81", colorable: false },       // 🎁
            { ch: "\uD83E\uDD29", colorable: false },       // 🤩
            { ch: "\uD83D\uDE0E", colorable: false },       // 😎
            { ch: "\uD83E\uDD73", colorable: false }        // 🥳
        ]
    ];

    /* 可染色字符的配色：爱心用红粉系，星星用金黄系 */
    var HEART_COLORS = ["#ff4d6d", "#ff2e63", "#fb6f92", "#ff758f", "#ff9eb5", "#ffb3c1", "#e63946", "#f72585"];
    var STAR_COLORS = ["#ffd166", "#ffb703", "#fb8500", "#ffd60a", "#fca311", "#ffe066", "#f4a261"];
    var EASINGS = ["ease-out", "cubic-bezier(0.22, 1, 0.36, 1)", "cubic-bezier(0.16, 1, 0.3, 1)", "cubic-bezier(0.34, 1.56, 0.64, 1)"];

    function rand(min, max) { return min + Math.random() * (max - min); }
    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
    function pct(n) { return Math.round(n * 100) / 100; }

    function spawn(event) {
        /* 占位链接（href="#"）：拦截默认跳转，避免点击「更多」等按钮时滚回页顶 */
        var link = event.target.closest && event.target.closest('a[href="#"]');
        if (link) event.preventDefault();

        if (reduced.matches) return;

        /* 大多数一次一颗，偶尔一次两颗在落点附近错开，更有层次 */
        var count = Math.random() < 0.22 ? 2 : 1;
        for (var i = 0; i < count; i++) {
            make(event.clientX + rand(-14, 14), event.clientY + rand(-8, 8));
        }
    }

    function make(x, y) {
        var pool = pick(CATEGORIES);
        var g = pick(pool);

        var el = document.createElement("span");
        el.textContent = g.ch;
        var s = el.style;
        s.position = "fixed";
        s.left = x + "px";
        s.top = y + "px";
        s.pointerEvents = "none";
        s.zIndex = "9999";
        s.lineHeight = "1";
        s.fontFamily = '"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif';
        if (g.colorable) {
            /* 文本字符按所属类别染色：含心形的用红粉系，星星用金黄系 */
            s.color = pick(g.ch === "\u2665" || g.ch === "\u2661" ? HEART_COLORS : STAR_COLORS);
        }
        s.willChange = "transform, opacity";
        document.body.appendChild(el);

        var size = rand(16, 44);
        s.fontSize = size + "px";

        /* 随机运动参数：方向、高度、旋转、缩放节奏、时长、缓动 */
        var rise = rand(90, 250);
        var sway = rand(26, 96) * (Math.random() < 0.5 ? -1 : 1);
        var rot0 = rand(-24, 24);
        var rot1 = rot0 + rand(-36, 36);
        var scale0 = rand(0.5, 0.8);
        var scale1 = rand(1.05, 1.35);   // 升起途中放大「弹一下」
        var duration = rand(900, 1600);
        var easing = pick(EASINGS);

        var anim = el.animate([
            {
                transform: "translate(-50%, -50%) rotate(" + pct(rot0) + "deg) scale(" + pct(scale0) + ")",
                opacity: 0
            },
            {
                transform: "translate(calc(-50% + " + pct(sway * 0.4) + "px), calc(-50% - " + pct(rise * 0.25) + "px)) rotate(" + pct(rot0 + (rot1 - rot0) * 0.35) + "deg) scale(" + pct(scale1) + ")",
                opacity: 1,
                offset: 0.28
            },
            {
                transform: "translate(calc(-50% - " + pct(sway * 0.5) + "px), calc(-50% - " + pct(rise * 0.7) + "px)) rotate(" + pct(rot0 + (rot1 - rot0) * 0.75) + "deg) scale(" + pct(scale1 * 0.92) + ")",
                opacity: 0.9,
                offset: 0.7
            },
            {
                transform: "translate(calc(-50% + " + pct(sway) + "px), calc(-50% - " + pct(rise) + "px)) rotate(" + pct(rot1) + "deg) scale(" + pct(scale0 * 0.9) + ")",
                opacity: 0
            }
        ], {
            duration: duration,
            easing: easing,
            fill: "forwards"
        });

        anim.onfinish = anim.oncancel = function () { el.remove(); };
    }

    document.addEventListener("click", spawn);
})();
