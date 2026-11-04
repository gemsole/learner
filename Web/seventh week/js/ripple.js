/* Material Design 涟漪：点击可交互表面时，从落点向外扩散一圈半透明波纹 */
(function () {
    "use strict";

    /* 参与涟漪的元素：按钮、服务卡、车型卡、轮播控制 */
    var HOSTS = "a.btn, .hud-cta, .service-card, .car-card, .carousel-btn, .booking-submit, button";
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

    function spawn(event) {
        if (reduced.matches) return;

        var host = event.target && event.target.closest ? event.target.closest(HOSTS) : null;
        if (!host || host.disabled) return;

        var rect = host.getBoundingClientRect();
        if (!rect.width || !rect.height) return;

        /* 宿主需要能裁掉溢出的波纹 */
        var cs = window.getComputedStyle(host);
        if (cs.position === "static") host.style.position = "relative";
        if (cs.overflow === "visible") host.style.overflow = "hidden";

        /* 鼠标点击取落点；键盘触发（detail 为 0）取元素中心 */
        var x = rect.width / 2;
        var y = rect.height / 2;
        if (event.detail > 0) {
            x = event.clientX - rect.left;
            y = event.clientY - rect.top;
        }

        /* 半径取到最远角，波纹刚好铺满整个表面 */
        var radius = Math.hypot(Math.max(x, rect.width - x), Math.max(y, rect.height - y));
        var size = radius * 2;

        var wave = document.createElement("span");
        wave.className = "ripple-wave";
        var s = wave.style;
        s.position = "absolute";
        s.top = (y - radius) + "px";
        s.left = (x - radius) + "px";
        s.width = size + "px";
        s.height = size + "px";
        s.borderRadius = "50%";
        /* 深色控件上用浅色波纹，其余跟随文字色，自动适配明暗表面 */
        s.background = host.classList.contains("carousel-btn") ? "#ffffff" : "currentColor";
        s.opacity = "0";
        s.pointerEvents = "none";
        s.willChange = "transform, opacity";
        host.appendChild(wave);

        var anim = wave.animate([
            { transform: "scale(0.18)", opacity: 0 },
            { transform: "scale(1)", opacity: 0.3, offset: 0.38 },
            { transform: "scale(1)", opacity: 0 }
        ], {
            duration: 640,
            easing: "cubic-bezier(0.16, 1, 0.3, 1)",
            fill: "forwards"
        });

        anim.onfinish = anim.oncancel = function () {
            wave.remove();
        };
    }

    document.addEventListener("click", spawn);
})();
