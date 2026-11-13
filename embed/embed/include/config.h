#pragma once

#include <Arduino.h>

// 所有可配置项集中在此文件，业务代码只读取，不直接声明配置值。

namespace cfg {

// ---------------- OLED / I2C ----------------
constexpr uint8_t OLED_SDA_PIN = 21;          // I2C SDA
constexpr uint8_t OLED_SCL_PIN = 22;          // I2C SCL
constexpr uint8_t OLED_I2C_ADDR = 0x3C;       // SSD1306 常见地址 0x3C / 0x3D
constexpr uint16_t OLED_WIDTH = 128;          // 屏幕宽度(px)
constexpr uint16_t OLED_HEIGHT = 64;          // 屏幕高度(px)
constexpr int8_t OLED_RESET_PIN = -1;         // 四针模块无独立复位脚
constexpr uint32_t I2C_CLOCK_HZ = 400000UL;   // I2C 时钟频率

// ---------------- 显示排版 ----------------
constexpr uint8_t FACE_TEXT_SIZE = 3;         // 颜文字字号（1~8）
constexpr uint8_t LABEL_TEXT_SIZE = 1;        // 表情名称字号
constexpr int16_t FACE_CENTER_Y = 24;         // 颜文字垂直中心
constexpr int16_t LABEL_CENTER_Y = 48;        // 名称垂直中心
constexpr int16_t PROGRESS_BAR_Y = 58;        // 轮播进度条顶部
constexpr int16_t PROGRESS_BAR_HEIGHT = 4;    // 进度条高度
constexpr uint32_t RENDER_INTERVAL_MS = 80;   // 重绘周期

// ---------------- 按键 ----------------
constexpr uint8_t BUTTON_PIN = 0;             // 开发板 BOOT 键，低电平有效
constexpr uint32_t BUTTON_DEBOUNCE_MS = 30;   // 消抖时间
constexpr uint8_t BUTTON_ACTIVE_LEVEL = LOW;  // 触发电平

// ---------------- 轮播 ----------------
constexpr uint32_t AUTO_ROTATE_INTERVAL_MS = 3000;  // 自动切换间隔，0 表示关闭

// ---------------- 串口日志 ----------------
constexpr uint32_t SERIAL_BAUD = 115200;

}  // namespace cfg
