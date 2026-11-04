/* ==================================================================
   在售车辆唯一数据源
   国际页在售列表（js/fleet-render.js 渲染）与订单页档案（js/order.js）
   都从 CARS_DATA 读取，两处不再各存一份，杜绝不一致。
   字段说明：
   - list      国际页列表展示与筛选所需（data-* 与文案）
   - specs     订单页参数条；highlights 国际页参数条（两页侧重不同）
   - space/suggest  订单页文案；listSpace 国际页「空间：」文案
   - price/days/pkgFees 计价基础（套餐按天费用随车辆不同）
   ================================================================== */
var CARS_DATA = [
    {
        id: "audi-a1",
        list: { type: "hot", seats: "5-", brand: "audi", deposit: 1, worry: 1, gear: 1, browse: "32", latest: "3 分钟前" },
        name: "奥迪A1", category: "小型两厢", plate: "京A·23F86",
        img: "./images/fast-car3.jpg",
        highlights: ["小型车", "2门4座", "1.4T", "城市代步轻快"],
        listSpace: "前排舒适，建议乘坐 4 人 + 1 行李箱",
        specs: ["自动挡", "小型车", "2门4座", "1.4T"],
        space: "车身灵巧，城市穿行轻松",
        suggest: "建议乘坐 4 人 + 1 行李箱",
        price: 318, days: 2, pkgFees: [0, 42, 85, 128],
        orderNo: "YX20261102-0236", orderTime: "2026-10-30 08:12",
        pickup: { date: "2026-11-02", time: "09:00", place: "日本 东京- 东京成田国际机场", store: "航站楼1", hours: "07:00-22:00" },
        ret: { date: "2026-11-04", time: "09:00", place: "日本 东京- 东京成田国际机场", store: "航站楼1", hours: "07:00-22:00" }
    },
    {
        id: "benz-v",
        list: { type: "mpv", seats: "5+", brand: "benz", deposit: 1, worry: 1, gear: 1, browse: "18", latest: "8 分钟前" },
        name: "奔驰V级", category: "商务MPV", plate: "沪C·80K12",
        img: "./images/fast-car4.jpg",
        highlights: ["商务车", "5门7座", "2.0T", "空间宽裕"],
        listSpace: "三排座椅，建议乘坐 7 人 + 4 行李箱",
        specs: ["自动挡", "商务车", "5门7座", "2.0T"],
        space: "空间较大，乘坐舒适",
        suggest: "建议乘坐 7 人 + 4 行李箱",
        price: 528, days: 3, pkgFees: [0, 68, 136, 198],
        orderNo: "YX20261105-1041", orderTime: "2026-10-30 09:47",
        pickup: { date: "2026-11-05", time: "10:00", place: "新加坡 新加坡- 樟宜国际机场", store: "航站楼3", hours: "24小时营业" },
        ret: { date: "2026-11-08", time: "10:00", place: "新加坡 新加坡- 樟宜国际机场", store: "航站楼3", hours: "24小时营业" }
    },
    {
        id: "porsche-cayenne",
        list: { type: "suv", seats: "5-", brand: "porsche", deposit: 0, worry: 1, gear: 1, browse: "41", latest: "1 分钟前" },
        name: "保时捷卡宴", category: "硬派越野", plate: "京N·71B30",
        img: "./images/fast-car5.jpg",
        highlights: ["越野车", "5门5座", "3.0T", "专业四驱"],
        listSpace: "后备箱宽大，建议乘坐 5 人 + 3 行李箱",
        specs: ["自动挡", "越野车", "5门5座", "3.0T"],
        space: "空间较大，通过性强",
        suggest: "建议乘坐 5 人 + 3 行李箱",
        price: 1180, days: 2, pkgFees: [0, 150, 300, 460],
        orderNo: "YX20261107-2318", orderTime: "2026-10-30 11:26",
        pickup: { date: "2026-11-07", time: "10:00", place: "德国 法兰克福- 法兰克福国际机场", store: "航站楼2", hours: "06:00-23:00" },
        ret: { date: "2026-11-09", time: "10:00", place: "德国 法兰克福- 法兰克福国际机场", store: "航站楼2", hours: "06:00-23:00" }
    },
    {
        id: "bmw-z4",
        list: { type: "conv", seats: "5-", brand: "bmw", deposit: 1, worry: 0, gear: 0, browse: "27", latest: "5 分钟前" },
        name: "宝马Z4", category: "敞篷个性", plate: "浙B·56T19",
        img: "./images/fast-car6.jpg",
        highlights: ["个性车", "2门2座", "2.0L", "海边兜风首选"],
        listSpace: "双人座舱，建议乘坐 2 人 + 1 行李箱",
        specs: ["手动挡", "个性车", "2门2座", "2.0L"],
        space: "敞篷座舱，海边兜风惬意",
        suggest: "建议乘坐 2 人 + 1 行李箱",
        price: 580, days: 4, pkgFees: [0, 88, 168, 246],
        orderNo: "YX20261112-0873", orderTime: "2026-10-30 15:03",
        pickup: { date: "2026-11-12", time: "12:00", place: "美国 洛杉矶- 洛杉矶国际机场", store: "航站楼B", hours: "06:00-24:00" },
        ret: { date: "2026-11-16", time: "12:00", place: "美国 洛杉矶- 洛杉矶国际机场", store: "航站楼B", hours: "06:00-24:00" }
    },
    {
        id: "audi-tt",
        list: { type: "sport", seats: "5-", brand: "audi", deposit: 1, worry: 1, gear: 1, browse: "56", latest: "2 分钟前" },
        name: "奥迪TT", category: "运动轿跑", plate: "沪B·31P66",
        img: "./images/fast-car1.jpg",
        highlights: ["跑车", "2门4座", "2.0T", "操控灵活"],
        listSpace: "后排紧凑，建议乘坐 2 人 + 2 行李箱",
        specs: ["自动挡", "跑车", "2门4座", "2.0T"],
        space: "操控灵活，造型动感",
        suggest: "建议乘坐 2 人 + 2 行李箱",
        price: 688, days: 3, pkgFees: [0, 96, 188, 286],
        orderNo: "YX20261114-1502", orderTime: "2026-10-30 18:40",
        pickup: { date: "2026-11-14", time: "15:00", place: "法国 巴黎- 巴黎戴高乐国际机场", store: "航站楼2E", hours: "06:30-23:30" },
        ret: { date: "2026-11-17", time: "15:00", place: "法国 巴黎- 巴黎戴高乐国际机场", store: "航站楼2E", hours: "06:30-23:30" }
    },
    {
        id: "ferrari-458",
        list: { type: "sport", seats: "5-", brand: "ferrari", deposit: 0, worry: 0, gear: 1, browse: "89", latest: "刚刚" },
        name: "法拉利458", category: "超级跑车", plate: "粤B·08A88",
        img: "./images/fast-car2.jpg",
        highlights: ["跑车", "2门2座", "4.5L", "性能旗舰"],
        listSpace: "双人座舱，行李请精简",
        specs: ["自动挡", "跑车", "2门2座", "4.5L"],
        space: "性能旗舰，驾驶激情",
        suggest: "建议乘坐 2 人 + 1 行李箱",
        price: 2980, days: 2, pkgFees: [0, 320, 640, 980],
        orderNo: "YX20261121-3064", orderTime: "2026-10-30 21:15",
        pickup: { date: "2026-11-21", time: "09:00", place: "澳大利亚 悉尼- 悉尼金斯福德·史密斯机场", store: "航站楼1", hours: "07:00-21:00" },
        ret: { date: "2026-11-23", time: "09:00", place: "澳大利亚 悉尼- 悉尼金斯福德·史密斯机场", store: "航站楼1", hours: "07:00-21:00" }
    }
];
