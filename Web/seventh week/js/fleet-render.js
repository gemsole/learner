/* ==================================================================
   国际页配置驱动渲染（在占位处同步执行，避免列表区闪动）：
   1) 预订表单的取/还车城市下拉（城市分组来自配置）
   2) 取/还车时段下拉（档位来自配置，与订单页弹层共用同一份）
   3) 「指定品牌」筛选复选框（品牌与标识图来自配置）
   4) 在售车型列表（唯一数据源 js/cars-data.js）
   ================================================================== */
(function () {
    "use strict";

    var slotEl = document.currentScript;
    if (!slotEl || !window.APP_CONFIG || !window.CARS_DATA) return;

    /* 1) 城市下拉：保留 HTML 中既有的「请选择」占位项，追加分组 */
    Array.prototype.forEach.call(
        document.querySelectorAll('select[name="pickup-city"], select[name="return-city"]'),
        function (select) {
            window.APP_CONFIG.get("cityGroups").forEach(function (group) {
                var og = document.createElement("optgroup");
                og.label = group.group;
                group.cities.forEach(function (city) {
                    var opt = document.createElement("option");
                    opt.value = city.value;
                    opt.textContent = city.label;
                    og.appendChild(opt);
                });
                select.appendChild(og);
            });
        }
    );

    /* 2) 时段下拉：清空后按配置档位重建（首项默认选中，与原静态一致） */
    Array.prototype.forEach.call(
        document.querySelectorAll('select[name="pickup-time"], select[name="return-time"]'),
        function (select) {
            select.innerHTML = "";
            window.APP_CONFIG.get("timeSlots").forEach(function (t) {
                var opt = document.createElement("option");
                opt.value = t;
                opt.textContent = t;
                select.appendChild(opt);
            });
        }
    );

    /* 3) 品牌筛选：「不限」+ 配置中的品牌列表 */
    var brandBox = document.getElementById("brand-opts");
    if (brandBox) {
        var brandHTML =
            '<label class="opt"><input type="checkbox" name="brand" value="all" checked><i class="opt-box"></i>不限</label>';
        window.APP_CONFIG.get("brands").forEach(function (brand) {
            brandHTML +=
                "\n                        " +
                '<label class="opt">' +
                '<input type="checkbox" name="brand" value="' + brand.value + '"><i class="opt-box"></i>' +
                '<img class="brand-mark" src="' + brand.mark + '" alt="">' +
                brand.label +
                "</label>";
        });
        brandBox.innerHTML = brandHTML;
    }

    /* 4) 在售车型列表：结构与国际页原静态标记逐项对应 */
    var cardsHTML = window.CARS_DATA.map(function (car) {
        var l = car.list;
        var lis = car.highlights.map(function (item) {
            return "            <li>" + item + "</li>";
        }).join("\n");

        return "<article class=\"intl-car\" data-type=\"" + l.type + "\" data-seats=\"" + l.seats +
            "\" data-brand=\"" + l.brand + "\" data-price=\"" + car.price + "\"\n" +
            "                data-deposit=\"" + l.deposit + "\" data-worry=\"" + l.worry + "\" data-gear=\"" + l.gear + "\">\n" +
            "                <div class=\"intl-car-media\"><img src=\"" + car.img + "\" alt=\"" + car.name + "\"></div>\n" +
            "                <div class=\"intl-car-body\">\n" +
            "                    <h3 class=\"intl-car-title\">" + car.category + " <em>|</em> " + car.name +
            "<span class=\"intl-car-plate\">" + car.plate + "</span></h3>\n" +
            "                    <ul class=\"intl-car-specs\">\n" + lis + "\n                    </ul>\n" +
            "                    <p class=\"intl-car-space\">空间：" + car.listSpace + "</p>\n" +
            "                    <p class=\"intl-car-meta\">" + l.browse + " 人正在浏览该车 <i>|</i> 最新预定：" + l.latest + "</p>\n" +
            "                </div>\n" +
            "                <div class=\"intl-car-side\">\n" +
            "                    <p class=\"intl-car-price\"><strong>¥" + car.price + "</strong>/天<span>总价：¥" +
            (car.price * car.days) + "</span></p>\n" +
            "                    <a href=\"./order.html?car=" + car.id + "\" class=\"intl-car-book\">预 定</a>\n" +
            "                </div>\n" +
            "            </article>";
    }).join("\n\n            ");

    slotEl.insertAdjacentHTML("afterend", "\n\n            " + cardsHTML + "\n");

    /* 占位脚本完成使命后移除 */
    if (slotEl.parentNode) slotEl.parentNode.removeChild(slotEl);
})();
