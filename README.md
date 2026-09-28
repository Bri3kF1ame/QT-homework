# 实验一：带键盘事件的计算器

Qt Widgets 实现的桌面计算器，支持鼠标与键盘两种输入方式，二者复用同一套输入处理逻辑。

## 功能

- 四则运算：加、减、乘、除
- 小数输入（同一操作数最多一个小数点）
- 退格、清除（C）、清除当前项（CE）、正负号切换（±）
- 连续运算（如 `2 + 3 × 4` 按从左到右计算）
- 异常处理：除数为 0、连续操作符、结果后继续输入、错误后自动恢复
- 显示区同时显示当前数字与运算表达式

## 键盘映射

| 按键 | 功能 | 按键 | 功能 |
| --- | --- | --- | --- |
| `0`–`9` | 数字 | `+` | 加 |
| `.` | 小数点 | `-` | 减 |
| `Enter` / `=` | 等于 | `*` | 乘 |
| `Backspace` | 退格 | `/` | 除 |
| `Esc` | 清除（C） | `Delete` | 清除当前项（CE） |
| `C` | 清除（C） | `N` | 正负号 |

## 目录结构

```
exp1_Calculator/
├── Calculator.pro      # qmake 工程文件
├── main.cpp            # 程序入口
├── mainwindow.h        # 主窗口类声明与计算器状态
├── mainwindow.cpp      # 输入处理、运算、键盘事件
├── mainwindow.ui       # Qt Designer 界面（网格布局 + 样式表）
└── screenshots/        # 各交互场景运行截图与测试记录
```

## 构建运行

使用 Qt Creator 打开 `Calculator.pro` 直接构建运行，或命令行：

```bash
qmake Calculator.pro
make            # Windows + MinGW 下为 mingw32-make
./Calculator
```

开发环境：Qt 6.11.2 (MinGW 64-bit)。
