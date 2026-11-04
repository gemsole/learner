/* ==========================================================================
 * PixelMascot —— 可复用的像素风可爱小人组件（零依赖，自包含）
 * --------------------------------------------------------------------------
 * 用法：在页面中引入本脚本即可，组件会 self-inject 自己的 DOM 与样式（均带 pm- 前缀，
 * 不污染宿主站点全局样式），并自动初始化一个小人悬浮在页面右下角。
 *
 * 能力：
 *  - 动态状态：闲置呼吸、走路、眨眼、四处张望（巡视）、开心、生气
 *  - 交互：鼠标/触摸拖拽、单击气泡说话、连续快速点击进入生气态
 *  - 闲置：一段时间无人理会 → 自动在页面边缘随机走动、巡视并气泡询问
 *  - 布局：position:fixed 悬浮最上层，默认停靠右下角，拖动有边界，避免遮挡中央内容
 * ========================================================================== */
(function (global) {
    "use strict";

    /* ---------- 可配置项 ---------- */
    var CONFIG = {
        pixelSize: 5,          // 单个“像素”渲染成多少 px（5 → 16×5=80px 宽）
        speed: 70,             // 巡视走动速度（px/s）
        idleWait: 6500,        // 闲置多久后开始自动巡视（ms）
        angryClicks: 3,        // 短时间内连续点击次数触发生气
        angryWindow: 1100,     // 判定“连续”的时间窗（ms）
        margin: 10,            // 距视口边缘的最小留白（px）
        phrases: {
            happy: ["你好呀~", "干嘛呢？", "要我帮忙吗？", "嘿嘿，被你发现啦", "今天也要开心呀"],
            angry: ["别戳啦！我生气啦！", "再戳我就咬你！", "哼！不理你了！", "啊啊——别闹了！"],
            ask:   ["你在干什么呀？", "需要我帮忙吗？", "好无聊呀，陪我玩~", "你在忙什么呀？", "要我帮你看看吗？"],
            drag:  ["呀——别拎我！", "轻点儿~", "放我下来啦！"]
        }
    };

    var SVG_NS = "http://www.w3.org/2000/svg";
    var COL = 16, ROW = 18;          // 精灵网格：16 列 × 18 行

    /* ---------- 调色板 ---------- */
    var PALETTE = {
        W: "#ffffff",   // 白发/耳朵
        p: "#ffb6c1",   // 粉色（耳内、脸颊、卫衣上段）
        b: "#8fd3f4",   // 蓝色（卫衣下段）
        E: "#6b7fd4",   // 蓝紫眼瞳
        S: "#ffefea",   // 皮肤
        Y: "#ffd54f",   // 黄色弯月发饰
        G: "#3a3a3a",   // 深灰（嘴、短裤）
        R: "#ff5c7a"    // 生气时更深的腮红
    };

    /* ---------- 基础精灵（16 宽 × 18 高），"." 为透明 ---------- */
    var BASE = [
        "....pp....pp....", // 0  耳尖
        "...WppW..WppW...", // 1  耳朵
        "...WWWW..WWWW...", // 2  耳朵根部
        "..YWWWWWWWWWW...", // 3  刘海 + 弯月发饰(Y)
        "...WSSSSSSSSW...", // 4  头发下沿 + 额头
        "...WSSSSSSSSW...", // 5  额头
        "...WSEESSEESW...", // 6  眼睛（上）
        "...WSEESSEESW...", // 7  眼睛（下）
        "...WppSSSSppW...", // 8  脸颊腮红
        "...WSSSGGSSSW...", // 9  小嘴
        "....pppppppp....", // 10 卫衣领口（粉）
        "....pppppppp....", // 11 卫衣上段（粉）
        "....pppppppp....", // 12 卫衣上段（粉）
        "....bbbbbbbb....", // 13 卫衣下段（蓝）
        "....bbbbbbbb....", // 14 卫衣下段（蓝）
        ".....GGGGGG.....", // 15 短裤
        "......WW.WW.....", // 16 白袜小腿
        "......WW.WW....."  // 17 白袜脚
    ];

    /* 按“行号→内容”覆盖生成不同表情/姿态帧 */
    function mkFrame(overrides) {
        var rows = BASE.slice();
        for (var i in overrides) { rows[+i] = overrides[i]; }
        return rows;
    }

    var FRAMES = {
        idle:  mkFrame({}),
        blink: mkFrame({ 6: "...WSSSSSSSSW...", 7: "...WSGGSSGGSW..." }),
        happy: mkFrame({ 6: "...WSSSSSSSSW...", 7: "...WSGGSSGGSW...", 9: "...WSSGGGGSSW..." }),
        angry: mkFrame({ 5: "...WSGSSSSGSW...", 8: "...WRRSSSSRRW...", 9: "...WSSGGGGSSW..." }),
        walkA: mkFrame({ 16: "......WW.WW.....", 17: "......WW.WW....." }),
        walkB: mkFrame({ 16: ".....WW..WW.....", 17: ".....WW..WW....." })
    };

    /* ---------- 注入样式（全部 pm- 前缀） ---------- */
    var STYLE = [
        ".pm-m{position:fixed;z-index:2147483000;cursor:grab;user-select:none;touch-action:none;",
        "  line-height:1;font-family:'Segoe UI',system-ui,sans-serif;will-change:left,top;}",
        ".pm-m.pm-drag{cursor:grabbing;}",
        ".pm-face{transform-origin:50% 100%;}",
        ".pm-rock{transform-origin:50% 100%;}",
        ".pm-sprite{display:block;transform-origin:50% 100%;image-rendering:pixelated;}",
        ".pm-m.pm-breathe .pm-sprite{animation:pmBreathe 2.4s ease-in-out infinite;}",
        ".pm-m.pm-walk .pm-rock{animation:pmBob .32s ease-in-out infinite;}",
        ".pm-m.pm-look .pm-rock{animation:pmSway .8s ease-in-out infinite;}",
        "@keyframes pmBreathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.05)}}",
        "@keyframes pmBob{0%,100%{transform:translateY(1px)}50%{transform:translateY(-2px)}}",
        "@keyframes pmSway{0%,100%{transform:rotate(0)}25%{transform:rotate(-9deg)}75%{transform:rotate(9deg)}}",
        ".pm-bubble{position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%) translateY(5px);",
        "  max-width:190px;padding:7px 10px;background:#fff;border:2px solid #3a3a3a;border-radius:6px;",
        "  box-shadow:2px 2px 0 rgba(58,58,58,.18);font-size:13px;color:#3a3a3a;white-space:nowrap;",
        "  opacity:0;pointer-events:none;transition:opacity .16s ease,transform .16s ease;}",
        ".pm-bubble.pm-show{opacity:1;transform:translateX(-50%) translateY(0);}",
        ".pm-bubble::after{content:'';position:absolute;top:100%;left:50%;margin-left:-6px;",
        "  border:6px solid transparent;border-top-color:#3a3a3a;}",
        ".pm-fx{position:absolute;inset:0;pointer-events:none;overflow:visible;}",
        ".pm-heart{position:absolute;left:50%;top:40%;margin-left:-8px;font-size:14px;",
        "  animation:pmHeart 1.1s ease-out forwards;}",
        "@keyframes pmHeart{0%{transform:translate(0,0) scale(.6);opacity:0}",
        "  15%{opacity:1;transform:translate(var(--dx,0),-4px) scale(1)}",
        "  100%{transform:translate(var(--dx,0),-46px) scale(1.05);opacity:0}}",
        ".pm-anger{position:absolute;left:50%;top:6%;margin-left:-13px;font-size:22px;",
        "  animation:pmAnger .9s ease forwards;}",
        "@keyframes pmAnger{0%{transform:scale(.2);opacity:0}45%{transform:scale(1.3);opacity:1}100%{transform:scale(1);opacity:1}}"
    ].join("\n");

    /* ---------- 工具 ---------- */
    function rand(min, max) { return min + Math.random() * (max - min); }
    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

    /* ---------- 组件类 ---------- */
    function PixelMascot(options) {
        var cfg = Object.assign({}, CONFIG, options || {});
        // options.phrases 与默认短语逐项合并
        if (options && options.phrases) {
            cfg.phrases = Object.assign({}, CONFIG.phrases, options.phrases);
        }

        this.cfg = cfg;
        this.pos = { x: 0, y: 0 };
        this.state = "idle";
        this.tapCount = 0;
        this.lastTap = 0;
        this.facing = 1;

        var self = this;

        /* ----- 注入样式 ----- */
        if (!document.getElementById("pm-style")) {
            var st = document.createElement("style");
            st.id = "pm-style";
            st.textContent = STYLE;
            document.head.appendChild(st);
        }

        /* ----- 构建 DOM ----- */
        var c = this.el = document.createElement("div");
        c.className = "pm-m pm-breathe";

        this.bubble = document.createElement("div");
        this.bubble.className = "pm-bubble";

        this.fx = document.createElement("div");
        this.fx.className = "pm-fx";

        this.face = document.createElement("div");
        this.face.className = "pm-face";
        this.rock = document.createElement("div");
        this.rock.className = "pm-rock";
        this.svg = document.createElementNS(SVG_NS, "svg");
        this.svg.setAttribute("class", "pm-sprite");
        this.svg.setAttribute("width", COL * cfg.pixelSize);
        this.svg.setAttribute("height", ROW * cfg.pixelSize);
        this.svg.setAttribute("viewBox", "0 0 " + COL + " " + ROW);
        this.svg.setAttribute("shape-rendering", "crispEdges");

        this.rock.appendChild(this.svg);
        this.face.appendChild(this.rock);
        c.appendChild(this.bubble);
        c.appendChild(this.fx);
        c.appendChild(this.face);
        document.body.appendChild(c);

        this.setFrame("idle");
        this.render(FRAMES.idle);

        /* ----- 初始位置：右下角 ----- */
        var rect = this.svg.getBoundingClientRect();
        this.size = { w: rect.width, h: rect.height };
        this.pos.x = window.innerWidth - this.size.w - cfg.margin;
        this.pos.y = window.innerHeight - this.size.h - cfg.margin;
        this.applyPos(true);

        /* ----- 事件 ----- */
        this._bind();
        this._startIdleTimer();

        /* ----- 眨眼：闲置态每隔几秒眨一下 ----- */
        this._blinkTimer = setInterval(function () {
            if (self.state === "idle" && !self.dragging) {
                self.render(FRAMES.blink);
                setTimeout(function () { if (self.state === "idle") self.render(FRAMES.idle); }, 140);
            }
        }, 3200);
    }

    /* ----- 渲染精灵帧 ----- */
    PixelMascot.prototype.render = function (rows) {
        var s = this.svg;
        while (s.firstChild) s.removeChild(s.firstChild);
        for (var y = 0; y < ROW; y++) {
            var row = rows[y];
            for (var x = 0; x < COL; x++) {
                var ch = row[x];
                if (ch === "." || !PALETTE[ch]) continue;
                var r = document.createElementNS(SVG_NS, "rect");
                r.setAttribute("x", x);
                r.setAttribute("y", y);
                r.setAttribute("width", 1);
                r.setAttribute("height", 1);
                r.setAttribute("fill", PALETTE[ch]);
                s.appendChild(r);
            }
        }
    };

    PixelMascot.prototype.setFrame = function (name) {
        this.frame = name;
        this.render(FRAMES[name] || FRAMES.idle);
    };

    PixelMascot.prototype.setState = function (name) {
        if (this.state === name && name !== "walk") return;
        this.state = name;
        var c = this.el;
        c.classList.remove("pm-breathe", "pm-walk", "pm-look");
        if (name === "idle")          { this.setFrame("idle");  c.classList.add("pm-breathe"); }
        else if (name === "happy")    { this.setFrame("happy"); c.classList.add("pm-breathe"); }
        else if (name === "angry")    { this.setFrame("angry"); c.classList.add("pm-breathe"); }
        else if (name === "look")     { this.setFrame("idle");  c.classList.add("pm-look"); }
        else if (name === "walk")     { c.classList.add("pm-walk"); }
    };

    /* ----- 位置 / 朝向 ----- */
    PixelMascot.prototype.bounds = function () {
        return {
            minX: this.cfg.margin,
            minY: this.cfg.margin,
            maxX: window.innerWidth - this.size.w - this.cfg.margin,
            maxY: window.innerHeight - this.size.h - this.cfg.margin
        };
    };

    PixelMascot.prototype.applyPos = function (immediate) {
        var b = this.bounds();
        this.pos.x = clamp(this.pos.x, b.minX, b.maxX);
        this.pos.y = clamp(this.pos.y, b.minY, b.maxY);
        if (immediate) this.el.style.transition = "none";
        this.el.style.left = this.pos.x + "px";
        this.el.style.top = this.pos.y + "px";
    };

    PixelMascot.prototype.setFacing = function (dir) {
        this.facing = dir < 0 ? -1 : 1;
        this.face.style.transform = "scaleX(" + this.facing + ")";
    };

    /* ----- 气泡 ----- */
    PixelMascot.prototype.say = function (text, duration) {
        var self = this;
        this.bubble.textContent = text;
        this.bubble.classList.add("pm-show");
        clearTimeout(this._bubbleTimer);
        this._bubbleTimer = setTimeout(function () {
            self.bubble.classList.remove("pm-show");
        }, duration || 2200);
    };

    /* ----- 漂浮特效（爱心 / 生气符号） ----- */
    PixelMascot.prototype.burstHearts = function () {
        var n = 2 + Math.floor(Math.random() * 2);
        var glyphs = ["♥", "💖", "💕"];
        for (var i = 0; i < n; i++) {
            var h = document.createElement("span");
            h.className = "pm-heart";
            h.textContent = pick(glyphs);
            h.style.setProperty("--dx", Math.round(rand(-22, 22)) + "px");
            this.fx.appendChild(h);
            (function (node) {
                setTimeout(function () { if (node.parentNode) node.parentNode.removeChild(node); }, 1150);
            })(h);
        }
    };

    PixelMascot.prototype.showAnger = function () {
        if (this._anger && this._anger.parentNode) this._anger.parentNode.removeChild(this._anger);
        clearTimeout(this._angerTimer);
        var a = document.createElement("span");
        a.className = "pm-anger";
        a.textContent = "💢";
        this.fx.appendChild(a);
        var self = this;
        this._anger = a;
        this._angerTimer = setTimeout(function () {
            if (a.parentNode) a.parentNode.removeChild(a);
            self._anger = null;
        }, 1000);
    };

    /* ----- 交互 ----- */
    PixelMascot.prototype._bind = function () {
        var self = this;
        var c = this.el;
        var moved, downX, downY, downT, offX, offY;

        c.addEventListener("pointerdown", function (e) {
            e.preventDefault();
            moved = false;
            downX = e.clientX; downY = e.clientY; downT = Date.now();
            offX = downX - self.pos.x; offY = downY - self.pos.y;
            self._stopWander();                 // 有人来了，先别瞎溜达
            self._stopTimers();                 // 暂停自动恢复
            try { c.setPointerCapture(e.pointerId); } catch (err) {}
        });

        c.addEventListener("pointermove", function (e) {
            if (downT === undefined) return;
            var dx = e.clientX - downX, dy = e.clientY - downY;
            if (!moved && (Math.abs(dx) > 3 || Math.abs(dy) > 3)) {
                moved = true;
                self.dragging = true;
                c.classList.add("pm-drag");
                self.setState("idle");
                self.say(pick(self.cfg.phrases.drag), 1200);
            }
            if (moved) {
                self.pos.x = e.clientX - offX;
                self.pos.y = e.clientY - offY;
                self.el.style.transition = "none";
                self.applyPos(true);
            }
        });

        function end(e) {
            if (downT === undefined) return;
            downT = undefined;
            c.classList.remove("pm-drag");
            if (moved) {
                self.dragging = false;
            } else {
                self._onClick();
            }
            self._startIdleTimer();
            try { c.releasePointerCapture(e.pointerId); } catch (err) {}
        }
        c.addEventListener("pointerup", end);
        c.addEventListener("pointercancel", end);
    };

    PixelMascot.prototype._onClick = function () {
        var now = Date.now();
        if (now - this.lastTap > this.cfg.angryWindow) this.tapCount = 0;
        this.tapCount++;
        this.lastTap = now;

        clearTimeout(this._exprTimer);   // 取消上一次的表情恢复，避免打架
        this._stopWander();

        if (this.tapCount >= this.cfg.angryClicks) {
            this.tapCount = 0;
            this.setState("angry");
            this.showAnger();
            this.say(pick(this.cfg.phrases.angry), 2600);
            this._exprTimer = setTimeout((function (self) {
                return function () { self.setState("idle"); };
            })(this), 2600);
        } else {
            this.setState("happy");
            this.burstHearts();
            this.say(pick(this.cfg.phrases.happy), 1500);
            this._exprTimer = setTimeout((function (self) {
                return function () { self.setState("idle"); };
            })(this), 1500);
        }
    };

    /* ----- 闲置 → 自动巡视 ----- */
    PixelMascot.prototype._startIdleTimer = function () {
        var self = this;
        clearTimeout(this._idleTimer);
        this._idleTimer = setTimeout(function () { self._wander(); }, this.cfg.idleWait);
    };

    PixelMascot.prototype._stopTimers = function () {
        clearTimeout(this._idleTimer);
        clearTimeout(this._exprTimer);
        clearTimeout(this._wanderTimer);
        clearTimeout(this._wanderFallback);
        clearTimeout(this._angerTimer);
    };

    PixelMascot.prototype._stopWander = function () {
        // 使任何尚未触发的“到达”回调失效
        this._wanderSeq = (this._wanderSeq || 0) + 1;
        clearTimeout(this._wanderFallback);
        clearTimeout(this._wanderTimer);
        if (this._walkTimer) { clearInterval(this._walkTimer); this._walkTimer = null; }
        this.el.style.transition = "none";   // 立即停住
        var b = this.bounds();
        // 拿到当前实际位置（transition 可能进行中）
        var r = this.el.getBoundingClientRect();
        this.pos.x = clamp(r.left, b.minX, b.maxX);
        this.pos.y = clamp(r.top, b.minY, b.maxY);
        this.el.style.left = this.pos.x + "px";
        this.el.style.top = this.pos.y + "px";
        this.setState("idle");
    };

    PixelMascot.prototype._wander = function () {
        var self = this;
        var seq = ++this._wanderSeq || (this._wanderSeq = 1);
        var b = this.bounds();

        // 随机在“边缘带”里挑一个落脚点，避免停在正中央挡内容
        var target = { x: b.minX, y: b.minY };
        var edge = Math.floor(Math.random() * 4);
        if (edge === 0) { target.x = b.minX + rand(0, 40); target.y = rand(b.minY, b.maxY); }
        else if (edge === 1) { target.x = b.maxX - rand(0, 40); target.y = rand(b.minY, b.maxY); }
        else if (edge === 2) { target.y = b.minY + rand(0, 40); target.x = rand(b.minX, b.maxX); }
        else { target.y = b.maxY - rand(0, 40); target.x = rand(b.minX, b.maxX); }

        var dx = target.x - this.pos.x;
        var dy = target.y - this.pos.y;
        var dist = Math.hypot(dx, dy);
        var dur = Math.max(0.5, (dist / this.cfg.speed)).toFixed(2);

        this.setFacing(dx >= 0 ? 1 : -1);
        this.setState("walk");

        // 走路时双腿交替
        var alt = false;
        this._walkTimer = setInterval(function () {
            alt = !alt;
            self.setFrame(alt ? "walkB" : "walkA");
        }, 180);

        this.el.style.transition = "left " + dur + "s linear, top " + dur + "s linear";
        this.pos = target;
        this.el.style.left = target.x + "px";
        this.el.style.top = target.y + "px";

        var arrived = false;
        var onArrive = function () {
            if (arrived || seq !== self._wanderSeq) return;   // 已失效或被中断的巡视
            arrived = true;
            clearTimeout(self._wanderFallback);
            if (self._walkTimer) { clearInterval(self._walkTimer); self._walkTimer = null; }
            self.setState("look");
            self.setFacing(Math.random() < 0.5 ? 1 : -1);
            self.say(pick(self.cfg.phrases.ask), 3200);
            self._wanderTimer = setTimeout(function () { self._wander(); }, rand(3200, 5200));
        };
        this.el.addEventListener("transitionend", onArrive, { once: true });
        // 兜底：万一 transitionend 没触发
        this._wanderFallback = setTimeout(onArrive, dur * 1000 + 400);
    };

    /* ----- 视口变化时保持不出界 ----- */
    PixelMascot.prototype._onResize = function () {
        this.applyPos(true);
    };

    /* ---------- 自动初始化 ---------- */
    function init() {
        var m = new PixelMascot();
        window.addEventListener("resize", function () { m._onResize(); });
        global.PixelMascot = { create: function (o) { return new PixelMascot(o); }, CONFIG: CONFIG, FRAMES: FRAMES, PALETTE: PALETTE };
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})(window);