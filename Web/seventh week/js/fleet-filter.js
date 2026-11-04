// 车型组 / 车辆座位(单选) / 指定品牌(多选) / 排序条 → 联动在售车辆列表：
// 座位用原生 radio 保证互斥；品牌为复选框并集筛选；纯前端演示逻辑。
(function () {
    var cards = Array.prototype.slice.call(document.querySelectorAll('.intl-car'));
    if (!cards.length) return;

    var list = document.querySelector('.car-list');
    var empty = document.querySelector('.fleet-empty');
    var tag = document.querySelector('.intl-list-head .section-tag');
    var typeCards = Array.prototype.slice.call(document.querySelectorAll('.type-card'));
    var seatInputs = Array.prototype.slice.call(document.querySelectorAll('input[name="seat"]'));
    var brandInputs = Array.prototype.slice.call(document.querySelectorAll('input[name="brand"]'));
    var brandAll = document.querySelector('input[name="brand"][value="all"]');
    var sortInputs = Array.prototype.slice.call(document.querySelectorAll('input[name="sort"]'));

    /* 记住初始顺序，便于「综合推荐」复原 */
    cards.forEach(function (card, i) { card.dataset.index = i; });

    var state = { type: 'all', seat: 'all', brands: [], sort: 'default' };

    function apply() {
        var visible = [];
        cards.forEach(function (card) {
            var d = card.dataset;
            var show =
                (state.type === 'all' || d.type === state.type) &&
                (state.seat === 'all' || d.seats === state.seat) &&
                (!state.brands.length || state.brands.indexOf(d.brand) !== -1) &&
                (state.sort !== 'deposit' || d.deposit === '1') &&
                (state.sort !== 'worry' || d.worry === '1') &&
                (state.sort !== 'gear' || d.gear === '1');
            card.hidden = !show;
            if (show) visible.push(card);
        });

        /* 排序：价格降序，其余保持登记顺序 */
        if (state.sort === 'price-desc') {
            visible.sort(function (a, b) { return b.dataset.price - a.dataset.price; });
        } else {
            visible.sort(function (a, b) { return a.dataset.index - b.dataset.index; });
        }
        visible.forEach(function (card) { list.appendChild(card); });

        /* 空状态与库存读数 */
        if (empty) empty.hidden = visible.length !== 0;
        if (tag) tag.textContent = 'LIVE INVENTORY · ' + visible.length + ' UNITS';
    }

    /* 车型组：单选高亮 */
    typeCards.forEach(function (card) {
        card.addEventListener('click', function () {
            typeCards.forEach(function (o) { o.classList.remove('is-active'); });
            card.classList.add('is-active');
            state.type = card.dataset.filter || 'all';
            apply();
        });
    });

    /* 车辆座位：原生 radio，浏览器保证互斥 */
    seatInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            state.seat = input.value;
            apply();
        });
    });

    /* 指定品牌：多选取并集；「不限」与具体品牌互斥协调 */
    function selectedBrands() {
        return brandInputs
            .filter(function (b) { return b.checked && b.value !== 'all'; })
            .map(function (b) { return b.value; });
    }

    brandInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            if (input.value === 'all') {
                /* 勾选「不限」清空具体品牌；「不限」本身不可取消 */
                if (input.checked) {
                    brandInputs.forEach(function (b) { if (b.value !== 'all') b.checked = false; });
                } else {
                    input.checked = true;
                }
            } else if (input.checked) {
                /* 勾选具体品牌时取消「不限」 */
                brandAll.checked = false;
            } else if (!brandInputs.some(function (b) { return b.checked && b.value !== 'all'; })) {
                /* 取消最后一个具体品牌时回落到「不限」 */
                brandAll.checked = true;
            }
            state.brands = selectedBrands();
            apply();
        });
    });

    /* 排序条：保持单选语义（不允许全部取消） */
    sortInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            input.checked = true;
            sortInputs.forEach(function (o) { if (o !== input) o.checked = false; });
            state.sort = input.value;
            apply();
        });
    });
})();
