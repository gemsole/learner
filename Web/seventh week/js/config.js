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

    /* 订单页「套餐包含」页签：费用清单与保险明细文案（分组结构） */
    var ORDER_INCLUDE = {
        feeBadge: "¥",
        feeTitle: "租金及服务费用",
        feeItems: ["车辆租金", "税费", "无限制里程", "门店基础服务费", "车辆清洁与整备"],
        insBadge: "保",
        insTitle: "保险明细",
        groups: [
            {
                title: "车损盗窃险 · 保自己的车",
                items: [
                    { name: "碰撞险", desc: "正常驾驶租赁车辆期间发生碰撞时，起赔额以上由保险公司承担，您只需承担起赔额以内的费用。" },
                    { name: "盗抢险", desc: "车辆在租期内被盗抢的，起赔额以上由保险公司承担。" }
                ]
            },
            {
                title: "第三者责任险 · 保被撞的人和车",
                items: [
                    { name: "第三者责任险", desc: "驾驶租赁车辆发生事故造成第三方人身伤亡或财物损失时，在保额内由保险公司赔付。" }
                ]
            }
        ],
        extra: "超级补充全险 · 起赔额以内的费用也能赔付，可在上方「保价套餐」中升级选购"
    };

    /* 订单页限时活动与免费取消说明 */
    var ORDER_PROMO = {
        tag: "限时活动",
        text: "下单后分享行程给好友，最高可返 400 元奖励金",
        /* 倒计时：活动从页面加载时刻起持续的小时数，前端据此实时递减展示 */
        countdownHours: 6,
        countdownLabel: "距活动结束"
    };

    /* 订单页「租车流程」页签：步骤标题 + 说明，按顺序渲染为竖向时间轴 */
    var ORDER_FLOW = [
        { title: "选定车型并提交订单", desc: "在线选择车型、取还车时间与门店，确认费用后提交订单。" },
        { title: "完成支付", desc: "按所选支付方式支付订金或全额，支付成功即时锁定车辆。" },
        { title: "到店办理取车", desc: "携带驾驶证件与护照，在预约时段内到店核验身份。" },
        { title: "验车交车", desc: "与门店共同查验车况并签署单据，交车后即可启程。" },
        { title: "还车结算", desc: "按约定时间还车，现场验车，费用多退少补当场结清。" }
    ];

    /* 订单页「订单条款」页签：编号条款卡 */
    var ORDER_TERMS = [
        { title: "修改与取消", desc: "取车前可免费修改订单与取消订单，还车后费用按实际发生多退少补。" },
        { title: "押金退还", desc: "车辆押金于还车验车无误后 7 个工作日内按原支付路径退回。" },
        { title: "油量结算", desc: "油量按「取车刻度还车」结算，不足部分收取油费及加油服务费。" },
        { title: "违章处理", desc: "行程期间产生的交通违章与罚单由承租人承担，门店将协助通知与代缴。" }
    ];

    /* 订单页「注意事项」页签：警示条目 */
    var ORDER_NOTICES = [
        "主驾驶人须持有效驾照并完成认证，部分国家与地区需额外提供公证翻译件。",
        "驾驶人年龄一般要求 21-65 周岁，且驾龄满 1 年，高端车型另有要求。",
        "未经许可不得跨境行驶，不得将车辆用于竞赛、测试或营运等非常规用途。",
        "发生事故请第一时间报警，并联系门店与保险方，注意保留现场影像资料。"
    ];

    /* 免费取消：deadline 以取车时间（当地时间）为准，由订单页按当前取还车安排动态拼接 */
    var FREE_CANCEL = {
        title: "取车前免费取消",
        deadlinePrefix: "取车时间（当地时间 ",
        deadlineSuffix: "）前可免费取消",
        lateNote: "超过取车时间取消或未取车，将不退还预付款"
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
        storesByPlace: STORES_BY_PLACE,
        /* 「套餐包含」页签内容 / 限时活动 / 免费取消说明 */
        orderInclude: ORDER_INCLUDE,
        orderPromo: ORDER_PROMO,
        freeCancel: FREE_CANCEL,
        /* 租车流程 / 订单条款 / 注意事项页签内容 */
        orderFlow: ORDER_FLOW,
        orderTerms: ORDER_TERMS,
        orderNotices: ORDER_NOTICES
    };

    /* 统一读取接口 */
    return {
        get: function (key) {
            return data[key];
        }
    };
})();
