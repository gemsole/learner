// 订单详情页：根据 ?car= 参数渲染对应车辆的订单信息（每辆车各自的取还车安排互不相同），
// 保价套餐卡片点击切换选中态。纯前端演示逻辑：车辆档案统一来自 js/cars-data.js（唯一数据源），
// 套餐文案 / 费率 / 时段 / 门店等可配置项统一来自 js/config.js，本文件不另行声明。
(function () {
    "use strict";

    /* 车辆档案唯一数据源：js/cars-data.js 的 CARS_DATA，按 id 建映射供本页查询 */
    var CARS = {};
    CARS_DATA.forEach(function (car) { CARS[car.id] = car; });

    /* 套餐文案与计价费率统一来自配置层（js/config.js） */
    var PACKAGES = APP_CONFIG.get("packages");
    var RATES = APP_CONFIG.get("rates");

    /* 其余可选项同样来自配置层：时段 / 最短租期 / 同城门店 */
    var TIME_SLOTS = APP_CONFIG.get("timeSlots");
    var MIN_RENTAL_DAYS = APP_CONFIG.get("minRentalDays");
    var STORES_BY_PLACE = APP_CONFIG.get("storesByPlace");

    /* 「套餐包含」页签内容 / 限时活动 / 免费取消说明，同样出自配置层 */
    var INCLUDE = APP_CONFIG.get("orderInclude");
    var PROMO = APP_CONFIG.get("orderPromo");
    var FREE_CANCEL = APP_CONFIG.get("freeCancel");

    /* 租车流程 / 订单条款 / 注意事项页签内容，亦出自配置层 */
    var FLOW = APP_CONFIG.get("orderFlow");
    var TERMS = APP_CONFIG.get("orderTerms");
    var NOTICES = APP_CONFIG.get("orderNotices");

    /* 从 "YYYY-MM-DD" 算出「周几」标签 */
    function weekdayOf(dateStr) {
        var p = dateStr.split("-");
        var d = new Date(+p[0], +p[1] - 1, +p[2]);
        return "周" + "日一二三四五六".charAt(d.getDay());
    }

    /* "2026-11-02" + "09:00" → "11-02 09:00"，供步骤条时间戳使用 */
    function shortWhen(dateStr, time) {
        return dateStr.slice(5) + " " + time;
    }

    function fmt(n) {
        return "¥" + n.toLocaleString("en-US");
    }

    function setText(id, text) {
        var el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    function setMoney(id, n) {
        setText(id, fmt(n));
    }

    /* 页面静态文案的配置化填充：套餐卡片 / 驾驶人芯片 / 费用行名称。
       填充值与原静态标记一致，仅改为由配置层提供；只改文本不动节点，
       因此不影响后续对同一批元素的事件绑定 */
    function fillConfigText() {
        Array.prototype.forEach.call(document.querySelectorAll(".order-pkg"), function (card, i) {
            var pkg = PACKAGES[i];
            if (!pkg) return;
            var title = card.querySelector("h3");
            var lines = card.querySelectorAll(".order-pkg-desc p");
            if (title) title.textContent = pkg.title;
            if (lines[0]) lines[0].textContent = pkg.cover;
            if (lines[1]) lines[1].textContent = pkg.desc;
        });

        var addChip = document.querySelector('.order-chips[data-group="driver"] .order-chip[data-value="add"]');
        if (addChip) addChip.textContent = "增加 1 名（¥" + RATES.extraDriverDay + "/天）";

        var driverDt = document.querySelector("#fee-driver-row dt");
        if (driverDt) driverDt.textContent = "额外驾驶人 · ¥" + RATES.extraDriverDay + "/天";

        var saleDt = document.querySelector("#fee-sale-row dt");
        if (saleDt) saleDt.textContent = "在线全额支付优惠 · " + Math.round((1 - RATES.saleRate) * 100) + "折";
    }

    fillConfigText();

    /* 「套餐包含」页签：结构静态在 HTML，文字与条目统一由配置层渲染 */
    function renderInclude() {
        if (!INCLUDE) return;

        setText("inc-fee-badge", INCLUDE.feeBadge);
        setText("inc-fee-title", INCLUDE.feeTitle);
        setText("inc-ins-badge", INCLUDE.insBadge);
        setText("inc-ins-title", INCLUDE.insTitle);
        setText("inc-extra", INCLUDE.extra);

        /* 费用勾选清单 */
        var feeList = document.getElementById("inc-fee-list");
        if (feeList) {
            feeList.innerHTML = "";
            INCLUDE.feeItems.forEach(function (item) {
                var li = document.createElement("li");
                li.textContent = item;
                feeList.appendChild(li);
            });
        }

        /* 保险分组：组标题 + 若干「名称 + 说明」卡片 */
        var groupsBox = document.getElementById("inc-groups");
        if (groupsBox) {
            groupsBox.innerHTML = "";
            INCLUDE.groups.forEach(function (group) {
                var block = document.createElement("section");
                block.className = "inc-group";

                var head = document.createElement("h4");
                head.className = "inc-group-title";
                head.textContent = group.title;
                block.appendChild(head);

                var cards = document.createElement("div");
                cards.className = "inc-cards";
                group.items.forEach(function (item) {
                    var card = document.createElement("div");
                    card.className = "inc-card";
                    var name = document.createElement("h5");
                    name.textContent = item.name;
                    var desc = document.createElement("p");
                    desc.textContent = item.desc;
                    card.appendChild(name);
                    card.appendChild(desc);
                    cards.appendChild(card);
                });
                block.appendChild(cards);
                groupsBox.appendChild(block);
            });
        }
    }

    renderInclude();

    /* 限时活动与免费取消静态文案：同样由配置层填充（时限部分随取车安排联动） */
    function renderPromo() {
        if (PROMO) {
            setText("promo-tag", PROMO.tag);
            setText("promo-text", PROMO.text);
            /* 倒计时标签来自配置 */
            setText("promo-countdown-label", PROMO.countdownLabel || "距活动结束");
            startCountdown(PROMO.countdownHours || 0);
        }
        if (FREE_CANCEL) {
            setText("cancel-title", FREE_CANCEL.title);
            setText("cancel-late", FREE_CANCEL.lateNote);
        }
    }

    /* 限时倒计时：根据配置的小时数算出截止时间，每秒刷新一次展示 */
    var countdownTimer = null;
    function startCountdown(hours) {
        if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; }
        var el = document.getElementById("promo-countdown");
        if (!el || !hours) return;

        var deadline = Date.now() + hours * 3600 * 1000;

        function pad(n) { return n < 10 ? "0" + n : "" + n; }

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

    renderPromo();

    /* 租车流程：按配置渲染为竖向步骤时间轴（序号由 CSS 计数器生成） */
    function renderFlow() {
        var box = document.getElementById("flow-list");
        if (!box || !FLOW) return;
        box.innerHTML = "";
        FLOW.forEach(function (step) {
            var li = document.createElement("li");
            li.className = "flow-step";
            var title = document.createElement("h3");
            title.className = "flow-title";
            title.textContent = step.title;
            var desc = document.createElement("p");
            desc.className = "flow-desc";
            desc.textContent = step.desc;
            li.appendChild(title);
            li.appendChild(desc);
            box.appendChild(li);
        });
    }

    renderFlow();

    /* 订单条款：按配置渲染为编号条款卡（编号由 CSS 计数器生成） */
    function renderTerms() {
        var box = document.getElementById("terms-list");
        if (!box || !TERMS) return;
        box.innerHTML = "";
        TERMS.forEach(function (term) {
            var card = document.createElement("section");
            card.className = "terms-card";
            var title = document.createElement("h3");
            title.className = "terms-title";
            title.textContent = term.title;
            var desc = document.createElement("p");
            desc.className = "terms-desc";
            desc.textContent = term.desc;
            card.appendChild(title);
            card.appendChild(desc);
            box.appendChild(card);
        });
    }

    renderTerms();

    /* 注意事项：按配置渲染为警示条目 */
    function renderNotices() {
        var box = document.getElementById("notice-list");
        if (!box || !NOTICES) return;
        box.innerHTML = "";
        NOTICES.forEach(function (text) {
            var li = document.createElement("li");
            li.textContent = text;
            box.appendChild(li);
        });
    }

    renderNotices();

    /* 把一辆车的档案填进页面各个锚点 */
    var current = null;             // 当前展示的车辆档案，费用联动时复用

    /* 当前生效的取还车安排：初值来自车辆档案，「修改」弹层保存后覆盖 */
    var schedule = { pick: null, ret: null };

    function copyWhen(w) {
        return { date: w.date, time: w.time, place: w.place, store: w.store, hours: w.hours };
    }

    /* 把当前取还车安排渲染到页面锚点：两栏时间轴 + 步骤条时间 */
    function renderSchedule() {
        setText("pick-date", schedule.pick.date);
        setText("pick-week", weekdayOf(schedule.pick.date));
        setText("pick-time", schedule.pick.time);
        setText("pick-place", schedule.pick.place);
        setText("pick-store", schedule.pick.store);
        setText("pick-hours", schedule.pick.hours);

        setText("ret-date", schedule.ret.date);
        setText("ret-week", weekdayOf(schedule.ret.date));
        setText("ret-time", schedule.ret.time);
        setText("ret-place", schedule.ret.place);
        setText("ret-store", schedule.ret.store);
        setText("ret-hours", schedule.ret.hours);

        setText("step-3-time", shortWhen(schedule.pick.date, schedule.pick.time));
        setText("step-4-time", shortWhen(schedule.ret.date, schedule.ret.time));

        /* 免费取消时限随取车安排联动：取车时间（当地时间）前可取消 */
        if (FREE_CANCEL) {
            setText("cancel-deadline", FREE_CANCEL.deadlinePrefix +
                schedule.pick.date + " " + schedule.pick.time + FREE_CANCEL.deadlineSuffix);
        }
    }

    function fill(car) {
        current = car;
        schedule.pick = copyWhen(car.pickup);
        schedule.ret = copyWhen(car.ret);
        document.title = "订单详情 | " + car.name + " - 悦行网";

        var img = document.getElementById("order-img");
        if (img) { img.src = car.img; img.alt = car.name; }

        setText("order-category", car.category);
        setText("order-name", car.name);
        setText("order-plate", car.plate);

        var specEls = document.querySelectorAll("#order-specs .order-spec-text");
        specEls.forEach(function (el, i) { el.textContent = car.specs[i]; });

        setText("order-space", car.space);
        setText("order-suggest", car.suggest);

        /* 订单号与流转步骤时间 */
        setText("order-no", car.orderNo);
        setText("step-1-time", car.orderTime);

        renderSchedule();
        recalc();
    }

    /* ==================== 费用联动：套餐 / 驾驶人 / 支付方式 ==================== */

    var state = { pkg: 0, driver: "none", pay: "full" };

    /* 天数 = 还车日期 − 取车日期（自然日差），与车辆档案的 days 口径一致 */
    function parseDate(s) {
        var p = s.split("-");
        return new Date(+p[0], +p[1] - 1, +p[2]);
    }

    function daysBetween(a, b) {
        return Math.round((parseDate(b) - parseDate(a)) / 86400000);
    }

    function daysOf() {
        return daysBetween(schedule.pick.date, schedule.ret.date);
    }

    function recalc() {
        if (!current) return;

        var days = daysOf();
        var rent = current.price * days;
        var pkgFee = current.pkgFees[state.pkg] * days;
        var driverFee = state.driver === "add" ? RATES.extraDriverDay * days : 0;
        var sub = rent + pkgFee + driverFee;
        var sale = state.pay === "full" ? Math.round(sub * RATES.saleRate) : 0;
        var total = sub - sale;
        var deposit = Math.round(total * RATES.depositRate);
        var online = state.pay === "full" ? total : deposit;
        var offline = total - online;

        setText("fee-rent-name", "车辆租金 · " + days + "天");
        setMoney("fee-rent", rent);

        setText("fee-pkg-name", "保价套餐 · " + PACKAGES[state.pkg].title +
            (current.pkgFees[state.pkg] > 0 ? "（¥" + current.pkgFees[state.pkg] + "/天）" : ""));
        setMoney("fee-pkg", pkgFee);

        var driverRow = document.getElementById("fee-driver-row");
        if (driverRow) driverRow.hidden = state.driver !== "add";
        setMoney("fee-driver", driverFee);

        var saleRow = document.getElementById("fee-sale-row");
        if (saleRow) saleRow.hidden = state.pay !== "full";
        setText("fee-sale", "-" + fmt(sale));

        setMoney("fee-total", total);

        setText("fee-online-name", state.pay === "full" ? "在线支付" : "在线支付（订金）");
        setMoney("fee-online", online);

        var offlineRow = document.getElementById("fee-offline-row");
        if (offlineRow) offlineRow.hidden = state.pay === "full";
        setMoney("fee-offline", offline);

        /* 顶部总价与支付提示随配置同步刷新 */
        setText("order-total", total.toLocaleString("en-US"));
        setText("order-price-note", "(" + days + "天租期, 日均 ¥" + current.price + ")");
        setText("order-payfull", fmt(online));
        setText("order-payfull-text", state.pay === "full"
            ? "在线付全额通常可享受最优惠价格，提交订单支付"
            : "现在预订只需支付订金，余款 " + fmt(offline) + " 到店支付");
    }

    /* 保价套餐：单选式切换选中态，支持键盘操作，并联动费用 */
    var pkgs = Array.prototype.slice.call(document.querySelectorAll(".order-pkg"));
    pkgs.forEach(function (pkg, index) {
        function activate() {
            pkgs.forEach(function (o) { o.classList.remove("is-active"); });
            pkg.classList.add("is-active");
            state.pkg = index;
            recalc();
        }
        pkg.addEventListener("click", activate);
        pkg.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                activate();
            }
        });
    });

    /* 附加配置芯片：组内单选，驾驶人 / 支付方式参与计价 */
    Array.prototype.forEach.call(document.querySelectorAll(".order-chips"), function (group) {
        var chips = Array.prototype.slice.call(group.querySelectorAll(".order-chip"));
        chips.forEach(function (chip) {
            chip.addEventListener("click", function () {
                chips.forEach(function (o) { o.classList.remove("is-active"); });
                chip.classList.add("is-active");
                var key = group.getAttribute("data-group");
                var val = chip.getAttribute("data-value");
                if (key === "driver" || key === "pay") {
                    state[key] = val;
                    recalc();
                }
            });
        });
    });

    /* ==================== 订单须知标签页 ==================== */

    var tabs = Array.prototype.slice.call(document.querySelectorAll(".order-tab"));
    var panels = Array.prototype.slice.call(document.querySelectorAll(".order-panel"));
    tabs.forEach(function (tab, index) {
        tab.addEventListener("click", function () {
            tabs.forEach(function (o) {
                o.classList.remove("is-active");
                o.setAttribute("aria-selected", "false");
            });
            panels.forEach(function (o) {
                o.classList.remove("is-active");
                o.hidden = true;
            });
            tab.classList.add("is-active");
            tab.setAttribute("aria-selected", "true");
            panels[index].classList.add("is-active");
            panels[index].hidden = false;
        });
    });

    /* ==================== 修改取还车安排弹层 ==================== */

    var editMask = document.getElementById("edit-mask");
    var editForm = document.getElementById("edit-form");
    var editError = document.getElementById("edit-error");
    var pickDateInput = document.getElementById("edit-pick-date");
    var pickTimeSelect = document.getElementById("edit-pick-time");
    var pickStoreSelect = document.getElementById("edit-pick-store");
    var pickHoursText = document.getElementById("edit-pick-hours");
    var retDateInput = document.getElementById("edit-ret-date");
    var retTimeSelect = document.getElementById("edit-ret-time");
    var retStoreSelect = document.getElementById("edit-ret-store");
    var retHoursText = document.getElementById("edit-ret-hours");

    function todayStr() {
        var d = new Date();
        var m = d.getMonth() + 1;
        var day = d.getDate();
        return d.getFullYear() + "-" + (m < 10 ? "0" + m : m) + "-" + (day < 10 ? "0" + day : day);
    }

    /* 某地点某门店的营业时间 */
    function storeHours(place, store) {
        var list = STORES_BY_PLACE[place] || [];
        for (var i = 0; i < list.length; i++) {
            if (list[i].store === store) return list[i].hours;
        }
        return "";
    }

    /* 时段下拉：选项统一来自配置；当前值不在档位内时补一项，保证回显 */
    function fillTimeSelect(select, value) {
        select.innerHTML = "";
        var slots = TIME_SLOTS.slice();
        if (slots.indexOf(value) === -1) slots.push(value);
        slots.forEach(function (t) {
            var opt = document.createElement("option");
            opt.value = t;
            opt.textContent = t;
            select.appendChild(opt);
        });
        select.value = value;
    }

    /* 门店下拉：选项 = 该车取还地点在配置中的门店列表（仅同城切换） */
    function fillStoreSelect(select, place, value) {
        select.innerHTML = "";
        (STORES_BY_PLACE[place] || []).forEach(function (s) {
            var opt = document.createElement("option");
            opt.value = s.store;
            opt.textContent = s.store;
            select.appendChild(opt);
        });
        select.value = value;
    }

    function showEditError(msg) {
        editError.textContent = msg;
        editError.hidden = !msg;
    }

    function openEdit() {
        if (!current || !schedule.pick) return;
        pickDateInput.value = schedule.pick.date;
        pickDateInput.min = todayStr();          /* 取车日期下限：今天 */
        retDateInput.value = schedule.ret.date;
        fillTimeSelect(pickTimeSelect, schedule.pick.time);
        fillTimeSelect(retTimeSelect, schedule.ret.time);
        fillStoreSelect(pickStoreSelect, schedule.pick.place, schedule.pick.store);
        fillStoreSelect(retStoreSelect, schedule.ret.place, schedule.ret.store);
        pickHoursText.textContent = schedule.pick.hours;
        retHoursText.textContent = schedule.ret.hours;
        showEditError("");
        editMask.hidden = false;
        pickDateInput.focus();
    }

    function closeEdit() {
        editMask.hidden = true;
        showEditError("");
    }

    function saveEdit() {
        if (!pickDateInput.value || !retDateInput.value) {
            showEditError("请选择取车与还车日期");
            return;
        }
        if (parseDate(pickDateInput.value) < parseDate(todayStr())) {
            showEditError("取车日期不能早于今天");
            return;
        }
        if (daysBetween(pickDateInput.value, retDateInput.value) < MIN_RENTAL_DAYS) {
            showEditError("租期至少 " + MIN_RENTAL_DAYS + " 天，请调整还车日期");
            return;
        }

        /* 地点（城市/机场）不变，仅日期、时段与同城门店生效 */
        schedule.pick.date = pickDateInput.value;
        schedule.pick.time = pickTimeSelect.value;
        schedule.pick.store = pickStoreSelect.value;
        schedule.pick.hours = storeHours(schedule.pick.place, schedule.pick.store);
        schedule.ret.date = retDateInput.value;
        schedule.ret.time = retTimeSelect.value;
        schedule.ret.store = retStoreSelect.value;
        schedule.ret.hours = storeHours(schedule.ret.place, schedule.ret.store);

        renderSchedule();
        recalc();
        closeEdit();
    }

    /* 两处「修改」链接共用同一弹层；href="#" 的默认跳转由 click-fx 统一拦截 */
    Array.prototype.forEach.call(document.querySelectorAll(".order-edit"), function (link) {
        link.addEventListener("click", openEdit);
    });

    editForm.addEventListener("submit", function (e) {
        e.preventDefault();
        saveEdit();
    });

    document.getElementById("edit-cancel").addEventListener("click", closeEdit);

    /* 点遮罩空白处关闭 */
    editMask.addEventListener("click", function (e) {
        if (e.target === editMask) closeEdit();
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !editMask.hidden) closeEdit();
    });

    /* 门店切换时联动营业时间显示 */
    pickStoreSelect.addEventListener("change", function () {
        pickHoursText.textContent = storeHours(schedule.pick.place, pickStoreSelect.value);
    });
    retStoreSelect.addEventListener("change", function () {
        retHoursText.textContent = storeHours(schedule.ret.place, retStoreSelect.value);
    });

    /* 读取 ?car= 参数；缺省或未知 id 回落到第一辆车 */
    var id = new URLSearchParams(location.search).get("car");
    fill(CARS[id] || CARS["audi-a1"]);
})();
