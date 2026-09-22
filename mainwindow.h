#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class QKeyEvent;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

protected:
    // 键盘事件入口：把按键翻译成与按钮相同的 token，再交给 handleInput
    void keyPressEvent(QKeyEvent *event) override;

private:
    // 统一的输入处理入口：鼠标点击与键盘输入都调用它，保证行为一致
    void handleInput(const QString &token);

    // 基础操作
    void resetAll();                    // 全部清零（C）
    void updateDisplay();               // 刷新显示区
    void showError(const QString &msg); // 进入错误状态（如除零）

    // 双操作数运算
    bool compute(double &result);       // 用 m_accumulator / m_pendingOp / m_entry 计算结果
    QString formatNumber(double value) const; // 结果格式化，消除浮点误差与多余 0

    void connectButtons();              // 统一连接所有按钮的 clicked 信号

    Ui::MainWindow *ui;

    // ---- 计算器状态 ----
    QString m_entry;          // 当前正在输入（或作为结果显示）的数字字符串
    double  m_accumulator;    // 第一个操作数（累加器）
    QString m_pendingOp;      // 待执行的运算符，空串表示没有
    QString m_exprText;       // 显示区上方的小字表达式，如 "12.5 +"
    bool    m_entering;       // 是否正在输入一个新的操作数
    bool    m_error;          // 是否处于错误状态（除零、溢出等）
    bool    m_justEvaluated;  // 上一次操作是否为 “=”
};

#endif // MAINWINDOW_H
