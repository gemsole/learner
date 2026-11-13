#pragma once

#include <stddef.h>

// 表情内容清单：新增/删除表情只需修改此表，无需改动业务代码。

struct Expression {
  const char *face;   // 颜文字（仅使用 ASCII 字符，保证默认字体可渲染）
  const char *label;  // 屏幕下方的说明文字
};

constexpr Expression EXPRESSIONS[] = {
    {"(^_^)", "HAPPY"},
    {"(-_-)", "SLEEPY"},
    {"(>_<)", "SQUINT"},
    {"(O_O)", "SHOCK"},
    {"(T_T)", "CRYING"},
    {"(^o^)", "EXCITED"},
    {"(x_x)", "DEAD"},
    {"(o_O)", "CONFUSED"},
    {"(-.-)Z", "SNORE"},
    {"\\(^o^)/", "CHEERS"},
};

constexpr size_t EXPRESSION_COUNT = sizeof(EXPRESSIONS) / sizeof(EXPRESSIONS[0]);
