#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QKeyEvent>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>

#include <cmath>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    connectButtons();

    // 按钮与显示区都不接收焦点，键盘事件统一由主窗口的 keyPressEvent 处理
    const QList<QPushButton *> buttons = findChildren<QPushButton *>();
    for (QPushButton *btn : buttons)
        btn->setFocusPolicy(Qt::NoFocus);
    ui->display->setFocusPolicy(Qt::NoFocus);
    setFocusPolicy(Qt::StrongFocus);

    resetAll();
    setFocus();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::connectButtons()
{
    // 按钮对象名 → 输入 token，鼠标点击后统一交给 handleInput 处理
    struct Binding { const char *name; const char *token; };
    static const Binding table[] = {
        {"btn0", "0"}, {"btn1", "1"}, {"btn2", "2"}, {"btn3", "3"}, {"btn4", "4"},
        {"btn5", "5"}, {"btn6", "6"}, {"btn7", "7"}, {"btn8", "8"}, {"btn9", "9"},
        {"btnDot", "."}, {"btnAdd", "+"}, {"btnSub", "-"}, {"btnMul", "×"},
        {"btnDiv", "÷"}, {"btnEquals", "="}, {"btnClear", "C"},
        {"btnClearEntry", "CE"}, {"btnBackspace", "BACK"}, {"btnSign", "SIGN"}
    };

    for (const Binding &b : table) {
        if (auto *btn = findChild<QPushButton *>(QString::fromLatin1(b.name))) {
            const QString token = QString::fromUtf8(b.token);
            connect(btn, &QPushButton::clicked, this,
                    [this, token] { handleInput(token); });
        }
    }
}

void MainWindow::keyPressEvent(QKeyEvent *event)
{
    // TODO: 键盘事件支持将在后续版本实现
    QMainWindow::keyPressEvent(event);
}

void MainWindow::handleInput(const QString &token)
{
    // 错误状态下，除清除类操作外，任何输入先复位，避免程序卡在错误态
    if (m_error && token != "C" && token != "CE")
        resetAll();

    // ---------- 1. 数字 ----------
    if (token.size() == 1 && token.at(0).isDigit()) {
        if (m_justEvaluated) {              // “=”之后直接输数字：开始新的计算
            m_entry.clear();
            m_accumulator = 0.0;
            m_pendingOp.clear();
            m_exprText.clear();
            m_justEvaluated = false;
        }
        if (!m_entering) {                  // 上一个操作数刚确认，开始输入新数
            m_entry = QStringLiteral("0");
            m_entering = true;
        }
        if (m_entry == QStringLiteral("0"))
            m_entry = token;                // 避免出现前导 0
        else
            m_entry += token;
        updateDisplay();
        return;
    }

    // ---------- 2. 小数点：同一操作数只允许出现一个 ----------
    if (token == QStringLiteral(".")) {
        if (m_justEvaluated) {
            m_entry.clear();
            m_accumulator = 0.0;
            m_pendingOp.clear();
            m_exprText.clear();
            m_justEvaluated = false;
        }
        if (!m_entering) {
            m_entry = QStringLiteral("0");
            m_entering = true;
        }
        m_entry += QLatin1Char('.');
        updateDisplay();
        return;
    }

    // ---------- 3. 四则运算符 ----------
    if (token == QStringLiteral("+") || token == QStringLiteral("-")
        || token == QStringLiteral("×") || token == QStringLiteral("÷")) {
        m_justEvaluated = false;
        if (m_entering && !m_pendingOp.isEmpty()) {
            // 已输入第二个操作数：先算前一步，实现连续运算
            double r = 0.0;
            if (!compute(r))
                return;                     // 除零/溢出等错误已在 compute 中提示
            m_entry = formatNumber(r);
            m_accumulator = r;
        } else {
            // 只输入了第一个操作数，或连续按运算符（后者相当于替换运算符）
            m_accumulator = m_entry.toDouble();
        }
        m_pendingOp = token;
        m_entering = false;                 // 接下来等待输入第二个操作数
        m_exprText = formatNumber(m_accumulator) + QLatin1Char(' ') + token;
        updateDisplay();
        return;
    }

    // ---------- 4. 等号 ----------
    if (token == QStringLiteral("=")) {
        if (m_pendingOp.isEmpty()) {        // 没有待执行的运算，直接忽略
            m_justEvaluated = true;
            return;
        }
        const double lhs = m_accumulator;
        const double rhs = m_entry.toDouble();
        double r = 0.0;
        if (!compute(r))
            return;
        m_exprText = formatNumber(lhs) + QLatin1Char(' ') + m_pendingOp
                     + QLatin1Char(' ') + formatNumber(rhs) + QStringLiteral(" =");
        m_entry = formatNumber(r);
        m_accumulator = r;
        m_pendingOp.clear();
        m_entering = false;
        m_justEvaluated = true;
        updateDisplay();
        return;
    }

    // ---------- 5. 清除 ----------
    if (token == QStringLiteral("C")) {
        resetAll();
        return;
    }
    if (token == QStringLiteral("CE")) {    // 只清当前操作数，保留运算符
        m_entry = QStringLiteral("0");
        m_entering = false;
        updateDisplay();
        return;
    }

    // ---------- 6. 退格：只在输入过程中有效 ----------
    if (token == QStringLiteral("BACK")) {
        if (!m_entering || m_justEvaluated)
            return;
        m_entry.chop(1);
        if (m_entry.isEmpty() || m_entry == QStringLiteral("-"))
            m_entry = QStringLiteral("0");
        updateDisplay();
        return;
    }

}

bool MainWindow::compute(double &result)
{
    const double lhs = m_accumulator;
    const double rhs = m_entry.toDouble();

    if (m_pendingOp == QStringLiteral("+"))
        result = lhs + rhs;
    else if (m_pendingOp == QStringLiteral("-"))
        result = lhs - rhs;
    else if (m_pendingOp == QStringLiteral("×"))
        result = lhs * rhs;
    else if (m_pendingOp == QStringLiteral("÷")) {
        result = lhs / rhs;
    } else {
        result = rhs;
    }

    if (!std::isfinite(result)) {           // 溢出或非法结果
        showError(QStringLiteral("数值超出范围"));
        return false;
    }
    return true;
}

QString MainWindow::formatNumber(double value) const
{
    if (!std::isfinite(value))
        return QStringLiteral("错误");

    // 15 位有效数字：既消除 0.1+0.2 这类浮点误差，又基本不损失精度
    QString s = QString::number(value, 'g', 15);
    if (s == QStringLiteral("-0"))
        s = QStringLiteral("0");
    return s;
}

void MainWindow::updateDisplay()
{
    if (m_error)
        return;                             // 错误提示由 showError 直接写显示区
    ui->display->setText(m_entry);
    ui->lblExpr->setText(m_exprText);
}

void MainWindow::showError(const QString &msg)
{
    m_error = true;
    m_pendingOp.clear();
    m_exprText.clear();
    m_entering = false;
    m_justEvaluated = false;
    m_entry = QStringLiteral("0");
    ui->display->setStyleSheet(QStringLiteral("color:#d93025;"));
    ui->display->setText(msg);
    ui->lblExpr->clear();
}

void MainWindow::resetAll()
{
    m_entry = QStringLiteral("0");
    m_accumulator = 0.0;
    m_pendingOp.clear();
    m_exprText.clear();
    m_entering = false;
    m_error = false;
    m_justEvaluated = false;
    ui->display->setStyleSheet(QString());
    ui->display->setText(m_entry);
    ui->lblExpr->clear();
}
