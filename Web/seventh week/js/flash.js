/* ==================================================================
   闪租页渲染
   1) 活动横幅：角标、标题、说明、两步路径、按钮与倒计时（配置驱动）
   2) 车型展示区：左列主视觉卡 + 右侧车辆卡（车辆信息取自 CARS_DATA）
   ================================================================== */
(function () {
    "use strict";

    if (!window.APP_CONFIG || !window.CARS_DATA) return;

    var PROMO = window.APP_CONFIG.get("flashPromo");
    var SHOWCASE = window.APP_CONFIG.get("flashShowcase");

    function setText(id, text) {
        var el = document.getElementById(id);
        if (el && text) el.textContent = text;
    }

    /* ---------- 活动横幅 ---------- */

    function renderPromo() {
        if (!PROMO) return;

        setText("flash-tag", PROMO.tag);
        setText("flash-title-lead", PROMO.titleLead);
        setText("flash-title-hl", PROMO.titleHighlight);
        setText("flash-desc", PROMO.desc);
        setText("flash-countdown-label", PROMO.countdownLabel);
        setText("flash-visual-tag", PROMO.visualTag);

        var cta = document.getElementById("flash-cta");
        if (cta) {
            cta.textContent = PROMO.ctaText;
            cta.href = PROMO.ctaHref;
        }

        var rules = document.getElementById("flash-rules");
        if (rules) {
            rules.textContent = PROMO.rulesText;
            rules.href = PROMO.rulesHref;
        }

        var box = document.getElementById("flash-steps");
        if (box && PROMO.steps) {
            box.innerHTML = PROMO.steps.map(function (step, index) {
                var arrow = index < PROMO.steps.length - 1
                    ? '<span class="flash-step-arrow" aria-hidden="true">›</span>'
                    : "";
                return '<span class="flash-step">' +
                    '<span class="flash-step-no">STEP ' + step.no + '</span>' +
                    '<span>' + step.text + '</span>' +
                    "</span>" + arrow;
            }).join("");
        }

        startCountdown(PROMO.countdownHours);
    }

    /* 倒计时：从页面加载时刻起算，每秒刷新，归零后停止定时器 */
    var countdownTimer = null;

    function startCountdown(hours) {
        if (countdownTimer) {
            clearInterval(countdownTimer);
            countdownTimer = null;
        }

        var el = document.getElementById("flash-countdown");
        if (!el || !hours) return;

        var deadline = Date.now() + hours * 3600 * 1000;

        function pad(n) {
            return n < 10 ? "0" + n : "" + n;
        }

        function tick() {
            var diff = Math.max(0, deadline - Date.now());
            var h = Math.floor(diff / 3600000);
            var m = Math.floor((diff % 3600000) / 60000);
            var s = Math.floor((diff % 60000) / 1000);
            el.textContent = pad(h) + ":" + pad(m) + ":" + pad(s);
            if (diff <= 0) {
                clearInterval(countdownTimer);
                countdownTimer = null;
            }
        }

        tick();
        countdownTimer = setInterval(tick, 1000);
    }

    /* ---------- 车型展示区 ---------- */

    function featureHTML(feature) {
        return '<div class="flash-feature flash-feature--' + feature.variant + '">' +
            '<img class="flash-feature-img" src="' + feature.img + '" alt="" loading="lazy">' +
            '<div class="flash-feature-body">' +
            '<span class="flash-feature-tag">' + feature.tag + "</span>" +
            '<span class="flash-feature-big">' + feature.big + "</span>" +
            '<span class="flash-feature-sub">' + feature.sub + "</span>" +
            "</div>" +
            "</div>";
    }

    function carHTML(car) {
        var copy = '<p class="flash-car-name">' + car.category + "<em>|</em>" + car.name +
            "</p>" +
            '<span class="flash-price">' + car.price +
            "<span>" + SHOWCASE.priceUnit + "</span></span>";
        return '<a class="flash-car" href="./order.html?car=' + car.id + '">' +
            '<div class="flash-car-copy">' + copy + "</div>" +
            '<div class="flash-car-copy flash-car-copy--alt" aria-hidden="true">' + copy +
            "</div>" +
            '<div class="flash-car-media"><img src="' + car.img + '" alt="' + car.name +
            '" loading="lazy"></div>' +
            "</a>";
    }

    function renderShowcase() {
        if (!SHOWCASE) return;

        setText("flash-section-title", SHOWCASE.title);
        setText("flash-section-desc", SHOWCASE.description);
        setText("flash-section-tag", SHOWCASE.tag);

        var byId = {};
        window.CARS_DATA.forEach(function (car) {
            byId[car.id] = car;
        });

        var cars = (SHOWCASE.carIds || []).map(function (id) {
            return byId[id];
        }).filter(Boolean);

        var mosaic = document.getElementById("flash-mosaic");
        if (mosaic) {
            mosaic.innerHTML = (SHOWCASE.features || []).map(featureHTML).join("") +
                cars.map(carHTML).join("");
        }
    }

    renderPromo();
    renderShowcase();
})();
