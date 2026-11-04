/* ==================================================================
   站点配置层（唯一配置来源）
   客服电话、城市/品牌选项、保价套餐、费率、取还车时段、同城门店、
   最短租期等可选项统一在此维护；页面与业务脚本只通过
   APP_CONFIG.get(key) 读取，不得另行声明这些值。
   ================================================================== */
var APP_CONFIG = (function () {
    "use strict";

    /* 客服电话：头部热线与页脚系统条共用 */
    var PHONE = "400-888-8888";

    /* 国际页预订表单的城市下拉（分组 + 城市项） */
    var CITY_GROUPS = [
        {
            group: "亚洲",
            cities: [
                { value: "tokyo", label: "东京" },
                { value: "osaka", label: "大阪" },
                { value: "bangkok", label: "曼谷" },
                { value: "singapore", label: "新加坡" }
            ]
        },
        {
            group: "欧洲",
            cities: [
                { value: "paris", label: "巴黎" },
                { value: "frankfurt", label: "法兰克福" }
            ]
        },
        {
            group: "北美",
            cities: [
                { value: "los-angeles", label: "洛杉矶" },
                { value: "new-york", label: "纽约" }
            ]
        },
        {
            group: "大洋洲",
            cities: [
                { value: "sydney", label: "悉尼" },
                { value: "melbourne", label: "墨尔本" }
            ]
        }
    ];

    /* 国际页「指定品牌」筛选：品牌标识图片 + 中文名 */
    var BRANDS = [
        { value: "bmw", label: "宝马", mark: "./images/车标/宝马.png" },
        { value: "audi", label: "奥迪", mark: "./images/车标/奥迪.png" },
        { value: "tesla", label: "特斯拉", mark: "./images/车标/特斯拉.jpg" },
        { value: "ferrari", label: "法拉利", mark: "./images/车标/法拉利.png" },
        { value: "benz", label: "奔驰", mark: "./images/车标/奔驰.jpg" },
        { value: "porsche", label: "保时捷", mark: "./images/车标/保时捷.jpg" }
    ];

    /* 订单页保价套餐：卡片文案（按天费用随车辆档案 pkgFees） */
    var PACKAGES = [
        {
            title: "标准套餐",
            cover: "碰撞盗抢险(起赔额:1千)",
            desc: "不含玻璃轮胎底盘，不含三者险"
        },
        {
            title: "三者险套餐",
            cover: "碰撞盗抢险(起赔额:1千)+三者险",
            desc: "承保事故第三方人身财物损失，降低高额赔付风险"
        },
        {
            title: "全额险套餐",
            cover: "碰撞盗抢险(起赔额:1千)+三者险+人身险",
            desc: "已含三者险，另含全车人员人身财物保障"
        },
        {
            title: "超安心套餐",
            cover: "碰撞盗抢险(起赔额:1千)+三者险+补充全险",
            desc: "已保玻璃轮胎底盘，24小时道路救援，境外安选"
        }
    ];

    /* 各取还地点可选门店及营业时间：
       每个地点的既有默认门店与营业时间与页面原数据保持一致，其余为演示数据 */
    var STORES_BY_PLACE = {
        "日本 东京- 东京成田国际机场": [
            { store: "航站楼1", hours: "07:00-22:00" },
            { store: "航站楼2", hours: "06:00-23:00" },
            { store: "航站楼3", hours: "24小时营业" }
        ],
        "新加坡 新加坡- 樟宜国际机场": [
            { store: "航站楼1", hours: "06:00-24:00" },
            { store: "航站楼2", hours: "07:00-23:00" },
            { store: "航站楼3", hours: "24小时营业" }
        ],
        "德国 法兰克福- 法兰克福国际机场": [
            { store: "航站楼1", hours: "06:00-22:00" },
            { store: "航站楼2", hours: "06:00-23:00" },
            { store: "航站楼3", hours: "07:00-21:00" }
        ],
        "美国 洛杉矶- 洛杉矶国际机场": [
            { store: "航站楼B", hours: "06:00-24:00" },
            { store: "航站楼1", hours: "05:30-24:00" },
            { store: "航站楼2", hours: "06:30-23:00" }
        ],
        "法国 巴黎- 巴黎戴高乐国际机场": [
            { store: "航站楼1", hours: "06:00-22:00" },
            { store: "航站楼2E", hours: "06:30-23:30" },
            { store: "航站楼3", hours: "07:00-22:00" }
        ],
        "澳大利亚 悉尼- 悉尼金斯福德·史密斯机场": [
            { store: "航站楼1", hours: "07:00-21:00" },
            { store: "航站楼2", hours: "06:30-22:00" },
            { store: "航站楼3", hours: "07:00-23:00" }
        ]
    };

    var data = {
        phone: PHONE,
        /* 取还车时段档位：国际页预订表单与订单页弹层共用 */
        timeSlots: ["09:00", "12:00", "15:00", "18:00"],
        /* 最短租期（天）：订单页弹层保存时校验 */
        minRentalDays: 2,
        cityGroups: CITY_GROUPS,
        brands: BRANDS,
        packages: PACKAGES,
        /* 计价费率：额外驾驶人单价 / 在线付全额折扣 / 预付订金比例 */
        rates: { extraDriverDay: 68, saleRate: 0.03, depositRate: 0.2 },
        /* 同城可选门店：仅允许同一地点内的航站楼切换，不产生异地费用 */
        storesByPlace: STORES_BY_PLACE
    };

    /* 统一读取接口 */
    return {
        get: function (key) {
            return data[key];
        }
    };
})();
