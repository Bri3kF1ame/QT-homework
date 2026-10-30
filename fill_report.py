# -*- coding: utf-8 -*-
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r"D:/allCOMPUTER/homework/qt/实验1-带键盘事件的计算器_2026秋.docx"
OUT = r"D:/allCOMPUTER/homework/qt/实验1-带键盘事件的计算器_2026秋_已完成.docx"
SHOTS = "D:/allCOMPUTER/homework/qt/exp1_Calculator/screenshots/"

BODY_FONT = "宋体"
CODE_FONT = "Consolas"
JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY
CENTER = WD_ALIGN_PARAGRAPH.CENTER
LEFT = WD_ALIGN_PARAGRAPH.LEFT


def set_run(run, font=BODY_FONT, size=12, bold=False, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:eastAsia"), font)
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


class Filler:
    def __init__(self, cell):
        self.cell = cell

    def body(self, anchor, segments, size=12, indent=True, align=JUSTIFY,
             before=3, after=3, line=1.5, color=None):
        p = self.cell.add_paragraph()
        anchor.addnext(p._p)
        pf = p.paragraph_format
        pf.first_line_indent = Pt(size * 2) if indent else Pt(0)
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = line
        p.alignment = align
        if isinstance(segments, str):
            segments = [(segments, False)]
        for text, bold in segments:
            r = p.add_run(text)
            set_run(r, BODY_FONT, size, bold, color)
        return p._p

    def label(self, anchor, text):
        return self.body(anchor, [(text, True)], indent=False, before=10, after=3)

    def code(self, anchor, text, size=9):
        tbl = self.cell.add_table(rows=1, cols=1)
        anchor.addnext(tbl._tbl)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        c = tbl.cell(0, 0)
        c.width = Cm(17.4)
        shade_cell(c, "F4F5F7")
        p = c.paragraphs[0]
        pf = p.paragraph_format
        pf.first_line_indent = Pt(0)
        pf.line_spacing = 1.0
        pf.space_before = Pt(3)
        pf.space_after = Pt(3)
        p.alignment = LEFT
        lines = text.split("\n")
        for i, line in enumerate(lines):
            r = p.add_run(line if line else " ")
            set_run(r, CODE_FONT, size)
            if i < len(lines) - 1:
                r.add_break()
        return tbl._tbl

    def image(self, anchor, path, caption, width_cm=8.0):
        p = self.cell.add_paragraph()
        anchor.addnext(p._p)
        p.alignment = CENTER
        pf = p.paragraph_format
        pf.first_line_indent = Pt(0)
        pf.space_before = Pt(6)
        pf.space_after = Pt(2)
        pf.keep_with_next = True   # 图片与题注不要被分页拆开
        r = p.add_run()
        r.add_picture(path, width=Cm(width_cm))
        cap = self.cell.add_paragraph()
        p._p.addnext(cap._p)
        cap.alignment = CENTER
        cap.paragraph_format.first_line_indent = Pt(0)
        cap.paragraph_format.space_after = Pt(8)
        rc = cap.add_run(caption)
        set_run(rc, BODY_FONT, 10.5, color=(0x59, 0x59, 0x59))
        return cap._p

    def image_pair(self, anchor, path1, cap1, path2, cap2, width_cm=8.2):
        tbl = self.cell.add_table(rows=1, cols=2)
        anchor.addnext(tbl._tbl)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        trPr = tbl.rows[0]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))   # 双图所在行不跨页
        for idx, (path, cap) in enumerate([(path1, cap1), (path2, cap2)]):
            c = tbl.cell(0, idx)
            c.width = Cm(width_cm + 0.6)
            pp = c.paragraphs[0]
            pp.alignment = CENTER
            pp.paragraph_format.first_line_indent = Pt(0)
            rr = pp.add_run()
            rr.add_picture(path, width=Cm(width_cm))
            cp = c.add_paragraph()
            cp.alignment = CENTER
            cp.paragraph_format.first_line_indent = Pt(0)
            rc = cp.add_run(cap)
            set_run(rc, BODY_FONT, 10.5, color=(0x59, 0x59, 0x59))
        return tbl._tbl

    def table(self, anchor, headers, rows, widths, font_size=9, header_fill="DCE6F1"):
        tbl = self.cell.add_table(rows=1 + len(rows), cols=len(headers))
        anchor.addnext(tbl._tbl)
        try:
            tbl.style = "Table Grid"
        except Exception:
            pass
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        all_rows = [headers] + rows
        for ri, values in enumerate(all_rows):
            for ci, val in enumerate(values):
                c = tbl.cell(ri, ci)
                c.width = Cm(widths[ci])
                p = c.paragraphs[0]
                pf = p.paragraph_format
                pf.first_line_indent = Pt(0)
                pf.line_spacing = 1.0
                pf.space_before = Pt(1)
                pf.space_after = Pt(1)
                p.alignment = CENTER if ri == 0 else LEFT
                r = p.add_run(str(val))
                set_run(r, BODY_FONT, font_size, bold=(ri == 0))
                if ri == 0:
                    shade_cell(c, header_fill)
        return tbl._tbl


doc = docx.Document(SRC)
cell = doc.tables[0].rows[4].cells[0]
P = cell.paragraphs
A = {i: P[i]._p for i in range(len(P))}

# 学号单元格字号略缩小，避免 13 位学号折成两行
id_cell = doc.tables[0].rows[1].cells[3]
for para in id_cell.paragraphs:
    for r in para.runs:
        r.font.size = Pt(9)

# 修正软件条件为实际环境
for r in P[9].runs:
    r.text = ""
if P[9].runs:
    P[9].runs[0].text = "软件条件：Qt 6.11.2（MinGW 64-bit），Git"
else:
    set_run(P[9].add_run("软件条件：Qt 6.11.2（MinGW 64-bit），Git"), BODY_FONT, 12)

F = Filler(cell)

# ==================== 25. UI 界面布局与设计 ====================
a = A[25]
a = F.body(a, "本实验使用 Qt Designer 设计界面。主窗口为 QMainWindow，中央部件 centralWidget 采用垂直布局 QVBoxLayout，"
              "自上而下分为“显示区”和“按键区”两部分。窗口初始大小 360×540，最小 320×480。")
a = F.body(a, "显示区 displayFrame（QFrame）内部再嵌套一个 QVBoxLayout：上方 lblExpr（QLabel）用灰色小字显示当前表达式，"
              "如“845 +”；下方 display（QLineEdit，只读、右对齐、无边框）用 34px 大字显示当前输入或计算结果。"
              "这样输入的数据、操作符和结果可以同时呈现，而不是只显示一个数字。")
a = F.body(a, "按键区使用 QGridLayout，按 5 行 × 4 列排列 20 个 QPushButton：第 1 行为 C、CE、←、÷；第 2～4 行为数字与 ×、−、+；"
              "第 5 行为 ±、0、.、=。所有按钮的 sizePolicy 均设为 Expanding，使按钮随窗口等比例缩放，不会出现大小不一的情况。")
a = F.body(a, "控件命名统一采用“类型 + 含义”的方式，既方便阅读，也便于用 findChild 按对象名批量连接信号：")
a = F.table(a,
            ["控件对象名", "类型", "作用"],
            [
                ["display", "QLineEdit", "显示当前数字或计算结果（只读、右对齐）"],
                ["lblExpr", "QLabel", "显示当前表达式与操作符（灰色小字）"],
                ["displayFrame", "QFrame", "显示区容器（白色圆角背景）"],
                ["gridLayout", "QGridLayout", "按键区 5×4 网格布局"],
                ["btn0～btn9", "QPushButton", "数字键 0～9"],
                ["btnDot / btnAdd / btnSub / btnMul / btnDiv", "QPushButton", "小数点与加、减、乘、除"],
                ["btnEquals", "QPushButton", "等号，执行计算"],
                ["btnClear / btnClearEntry / btnBackspace", "QPushButton", "清除、清除当前项、退格"],
                ["btnSign", "QPushButton", "正负号切换"],
            ],
            widths=[5.6, 4.2, 7.6], font_size=9)
a = F.image(a, SHOTS + "01_initial.png", "图 1  计算器主界面（由 UI 设计器完成布局与属性设置）", 6.0)

# ==================== 26. 主要代码、设计说明及运行结果 ====================
a = A[26]
a = F.body(a, "程序采用“单一输入入口 + 集中状态管理”的结构。无论鼠标点击按钮还是键盘按键，最终都会被转换成同一个输入记号"
              "（token，如 \"7\"、\".\"、\"+\"、\"=\"、\"BACK\"），再交给 MainWindow::handleInput() 统一处理，"
              "因此两套输入不会出现行为差异。")
a = F.body(a, "按钮与信号槽的连接集中在 connectButtons() 中完成：用对象名与 token 的映射表批量 connect，避免为 20 个按钮重复写 20 段连接代码。"
              "这里用 lambda 捕获 token，按钮被点击时把 token 交给统一入口：")
a = F.code(a, '''void MainWindow::connectButtons()
{
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
}''')
a = F.body(a, "计算器的全部状态由 6 个成员变量描述。handleInput() 根据当前状态决定输入是“追加到当前操作数”还是“开始新的操作数”，"
              "而不是反过来解析界面文字，这样结果后继续输入、连续运算等情形都能自然处理：")
a = F.table(a,
            ["成员变量", "类型", "含义"],
            [
                ["m_entry", "QString", "当前正在输入或作为结果显示的数字字符串"],
                ["m_accumulator", "double", "第一个操作数（累加器）"],
                ["m_pendingOp", "QString", "待执行的运算符，空串表示没有"],
                ["m_exprText", "QString", "显示区上方的小字表达式文本"],
                ["m_entering", "bool", "是否正在输入一个新的操作数"],
                ["m_justEvaluated", "bool", "上一次操作是否为“=”"],
                ["m_error", "bool", "是否处于错误状态（除零、溢出）"],
            ],
            widths=[3.6, 2.6, 11.2], font_size=9)
a = F.body(a, "运行结果如下图所示：输入 12.5 后依次按 +、7.5、=，显示区上方给出完整表达式“12.5 + 7.5 =”，下方给出结果 20。")
a = F.image(a, SHOTS + "04_result.png", "图 2  四则运算运行结果（12.5 + 7.5 = 20）", 7.0)

# ==================== 27. 按键事件处理 ====================
a = A[27]
a = F.body(a, "数字键的处理有两个要点：一是避免出现前导 0（输入 0 后再按 7 应显示 7，而不是 07）；"
              "二是按过运算符之后，再输入数字应开始一个新的操作数，而不是拼接到第一个操作数后面。")
a = F.code(a, '''if (token.size() == 1 && token.at(0).isDigit()) {
    if (m_justEvaluated) {              // “=”之后直接输数字：开始一次新计算
        m_entry.clear(); m_accumulator = 0.0;
        m_pendingOp.clear(); m_exprText.clear();
        m_justEvaluated = false;
    }
    if (!m_entering) {                  // 上一个操作数已确认，开始输入新数
        m_entry = "0";
        m_entering = true;
    }
    if (m_entry == "0") m_entry = token;   // 去掉前导 0
    else                m_entry += token;
    updateDisplay();
    return;
}''')
a = F.body(a, "退格只在“正在输入”时生效，避免把已经算出的结果或第一个操作数误删；删除到空或只剩负号时补回 0：")
a = F.code(a, '''if (token == "BACK") {
    if (!m_entering || m_justEvaluated) return;
    m_entry.chop(1);
    if (m_entry.isEmpty() || m_entry == "-") m_entry = "0";
    updateDisplay();
    return;
}''')
a = F.body(a, "清除分两级：C 调用 resetAll() 把全部状态清零；CE 只把当前操作数置 0，保留已输入的运算符，便于只修改第二个操作数。"
              "测试时输入 123 后连续按退格，显示依次变为 12、1、0；输入 3.1.4 时第二个小数点被忽略，显示 3.14。")
a = F.image(a, SHOTS + "09_backspace.png", "图 3  输入 123 后按退格，显示 12", 6.5)

# ==================== 28. 避免重复小数点 ====================
a = A[28]
a = F.body(a, "核心思路是：小数点能否输入，不取决于按了几次“.”键，而取决于当前操作数字符串中是否已经包含小数点。"
              "每次按下小数点前先用 QString::contains('.') 判断，已存在则直接忽略本次输入。")
a = F.code(a, '''if (token == ".") {
    if (m_justEvaluated) {              // 结果后输入小数点，先开一个新数
        m_entry.clear(); m_accumulator = 0.0;
        m_pendingOp.clear(); m_exprText.clear();
        m_justEvaluated = false;
    }
    if (!m_entering) {                  // 未在输入状态，自动补一个前导 0
        m_entry = "0";
        m_entering = true;
    }
    if (!m_entry.contains('.'))         // 关键：同一操作数只允许一个小数点
        m_entry += ".";
    updateDisplay();
    return;
}''')
a = F.body(a, "测试结果：依次点击 3、.、1、.、4，第二次小数点被忽略，显示 3.14；若先按 . 再按 5，会自动补前导 0 显示 0.5。"
              "该判断只作用于“当前操作数”：按下运算符后 m_entering 变为 false，新操作数可以重新输入小数点，"
              "因此 1.5 + 2.5 仍能正常输入。")
a = F.image(a, SHOTS + "05_dup_dot.png", "图 4  连续输入 3.1.4，第二个小数点被忽略，显示 3.14", 6.5)

# ==================== 29. 双操作数处理 ====================
a = A[29]
a = F.body(a, "四则运算需要同时保存“第一个操作数、运算符、第二个操作数”三类信息。程序用 m_accumulator 保存第一个操作数，"
              "用 m_pendingOp 保存运算符，用 m_entry 保存当前正在输入或刚刚算出的第二个操作数；"
              "m_entering 区分“正在输入”与“输入完成”，m_justEvaluated 标记上一次操作是否为等号。")
a = F.body(a, "按下运算符时：如果已经输入了第二个操作数（m_entering 为真且 m_pendingOp 非空），先调用 compute() 算出中间结果并作为新的第一个操作数；"
              "否则直接把当前 m_entry 存入 m_accumulator。随后记录运算符并把 m_entering 置 false，等待输入第二个操作数：")
a = F.code(a, '''if (token == "+" || token == "-" || token == "×" || token == "÷") {
    m_justEvaluated = false;
    if (m_entering && !m_pendingOp.isEmpty()) {
        double r = 0.0;
        if (!compute(r)) return;            // 连续运算：先结算前一步
        m_entry = formatNumber(r);
        m_accumulator = r;
    } else {
        m_accumulator = m_entry.toDouble(); // 记录第一个操作数
    }
    m_pendingOp = token;                    // 记录运算符
    m_entering = false;                     // 等待第二个操作数
    m_exprText = formatNumber(m_accumulator) + " " + token;
    updateDisplay();
    return;
}''')
a = F.body(a, "按下等号时，用 m_accumulator、m_pendingOp 和 m_entry 计算最终结果，把结果写回 m_entry 与 m_accumulator，"
              "清空 m_pendingOp，并把 m_justEvaluated 置 true，表示这一轮运算结束。compute() 根据运算符分支执行加、减、乘、除，"
              "是所有运算的唯一出口。")

# ==================== 30. 状态管理说明 ====================
a = A[30]
a = F.body(a, "程序不把界面上的文字当作唯一数据源，而是用独立的状态变量描述计算过程，界面只负责显示。"
              "状态之间的主要转换可以概括为下表：")
a = F.table(a,
            ["当前状态", "输入", "状态变化", "界面显示"],
            [
                ["初始（m_entering=false）", "数字 d", "m_entry=d，m_entering=true", "d"],
                ["正在输入操作数", "数字 d", "m_entry 追加 d（去掉前导 0）", "d…"],
                ["正在输入操作数", "运算符 op", "m_accumulator=m_entry，m_pendingOp=op，m_entering=false", "a op"],
                ["等待第二个操作数", "数字 d", "m_entry=d，m_entering=true", "d"],
                ["已有 op 且已输入第二个操作数", "运算符 op2", "先 compute() 得到 r，再 m_pendingOp=op2，等待新操作数", "r op2"],
                ["已有 op 且已输入第二个操作数", "=", "compute() 得到 r，清空 m_pendingOp，m_justEvaluated=true", "a op b = / r"],
                ["结果态（m_justEvaluated=true）", "数字 d", "清空 m_accumulator、m_pendingOp，开始新计算", "d"],
                ["结果态（m_justEvaluated=true）", "运算符 op", "m_accumulator=结果，记录 op，等待第二个操作数", "r op"],
            ],
            widths=[4.6, 2.4, 8.4, 2.0], font_size=8.5)
a = F.body(a, "其中两个布尔量是关键：m_entering 决定“数字是追加还是新建”，m_justEvaluated 决定“数字是开启新计算还是继续当前计算”。"
              "这样第一个操作数、操作符、第二个操作数和计算结果各归其位，连续运算与结果后继续输入都能自然处理，"
              "不需要为每种情况单独写一套分支。")

# ==================== 31. 连续操作与边界处理 ====================
a = A[31]
a = F.body(a, "连续运算采用“从左到右、遇到新运算符先结算前一步”的策略。例如 2 + 3 × 4，按下 × 时先把 2+3 算成 5，"
              "再以 5 作为第一个操作数与 4 相乘，最终得到 20，而不是按数学优先级得到 14。这与大多数手机计算器和 Windows 计算器的行为一致。")
a = F.body(a, "除零在 compute() 中统一拦截：除数为 0 时不执行除法，而是调用 showError() 把界面置为错误态，"
              "显示红色提示“除数不能为 0”。错误态下除 C、CE 外的任意输入都会先自动复位，避免程序卡在错误状态：")
a = F.code(a, '''else if (m_pendingOp == "÷") {
    if (qFuzzyIsNull(rhs)) {            // 除数为 0
        showError("除数不能为 0");
        return false;
    }
    result = lhs / rhs;
}''')
a = F.body(a, "计算结果后的继续输入分两种情况：按数字键视为开始一次全新计算（清空累加器与运算符）；按运算符则以当前结果作为第一个操作数继续运算。"
              "例如 6×7=42 后按 C 再算 10÷4 得到 2.5，说明清除后重新计算正常；9÷0 报错后直接输入 7+3= 得到 10，说明错误态能自动恢复。")
a = F.image_pair(a, SHOTS + "08_continuous.png", "图 5  连续运算 2 + 3 × 4 = 20",
                 SHOTS + "07_div_zero.png", "图 6  除数为 0 的红色提示", 8.0)

# ==================== 32. 至少 3 个异常/边界输入 ====================
a = A[32]
a = F.body(a, "选取 5 个有代表性的异常或边界输入，按“测试输入 → 原程序现象 → 原因分析 → 修改方法 → 修改后结果”记录如下：")
a = F.table(a,
            ["序号", "测试输入", "原程序现象", "原因分析", "修改方法", "修改后结果"],
            [
                ["1", "3 . 1 . 4", "显示 3.1.4，转换为数值失败，结果异常", "每次按小数点都直接追加，未判断当前操作数是否已有小数点",
                 "追加前用 m_entry.contains('.') 判断，已有则忽略", "显示 3.14，可正常参与运算"],
                ["2", "8 ÷ 0 =", "显示 inf 或异常数值", "除法前未校验除数，double 除以 0 得到无穷大",
                 "compute() 中用 qFuzzyIsNull(rhs) 拦截并调用 showError()", "红色提示“除数不能为 0”，后续输入自动恢复"],
                ["3", "5 + 3 = 后按 7", "7 拼接到结果 8 后面，变成 87", "结果态未区分“继续输入数字”与“继续运算”",
                 "用 m_justEvaluated 标记结果态，数字键先清空 acc/op 再输入", "显示 7，开始一次新计算"],
                ["4", "123 输入中按退格", "无反应，或删成空字符串后无法继续输入", "退格未判断输入状态，空串未补 0",
                 "仅在 m_entering 为真时退格，删空或只剩负号时补 0", "123 → 12 → 1 → 0"],
                ["5", "5 + ×", "运算符叠加，后续结果错误", "连续按运算符时未处理运算符替换",
                 "等待第二个操作数时，新运算符直接替换 m_pendingOp", "显示 5 ×，继续输入正常"],
            ],
            widths=[1.0, 2.4, 3.4, 4.0, 4.2, 2.6], font_size=8)
a = F.image_pair(a, SHOTS + "11_clear_recalc.png", "图 7  清除后重算 10 ÷ 4 = 2.5",
                 SHOTS + "13_recover_after_error.png", "图 8  除零报错后输入 7 + 3 自动恢复", 8.0)

# ==================== 33. 样式表与命名/结构 ====================
a = A[33]
a = F.body(a, "界面样式通过 Qt 样式表（QSS）集中设置在 MainWindow 的 styleSheet 属性上，按控件类型和 objectName 区分："
              "数字键白底、运算符浅蓝底、等号蓝底白字、清除键浅灰底，并设置圆角、悬停与按下状态。"
              "把样式集中在一处，避免在每个控件上零散设置属性：")
a = F.code(a, '''QPushButton { background:#ffffff; border:none; border-radius:10px;
              color:#1c1c1e; font-size:20px; }
QPushButton:hover   { background:#ececf0; }
QPushButton:pressed { background:#dcdce2; }
QPushButton#btnAdd, QPushButton#btnSub,
QPushButton#btnMul, QPushButton#btnDiv { background:#e8f1ff; color:#0a5bd3; }
QPushButton#btnEquals { background:#0a84ff; color:#ffffff; }
QPushButton#btnClear, QPushButton#btnClearEntry,
QPushButton#btnBackspace { background:#e7e7ec; color:#3a3a3c; }
#display { background:transparent; color:#1c1c1e; font-size:34px; font-weight:600; }''')
a = F.body(a, "命名与结构检查：控件全部采用英文命名（display、lblExpr、btnAdd…），类成员统一以 m_ 开头，"
              "函数名使用动词短语（handleInput、compute、resetAll、updateDisplay）。所有按钮共用 handleInput() 一个入口，"
              "键盘也复用它，因此没有出现“每个按钮一段重复代码”的问题；关键状态和特殊分支（除零、重复小数点、结果态）都加了中文注释，"
              "便于后续维护。")

# ==================== 34. 优化后的界面截图 ====================
a = A[34]
a = F.body(a, "优化前后的界面对比如下：左图为未应用样式表的默认外观，右图为应用样式表后的效果。")
a = F.image_pair(a, SHOTS + "02_before_style.png", "（a）优化前：默认控件外观",
                 SHOTS + "01_initial.png", "（b）优化后：应用样式表", 8.2)
a = F.body(a, "主要改进：① 显示区改为白色圆角卡片，主数字 34px 右对齐，表达式用灰色小字置于上方，层次更清晰；"
              "② 按键改为无边框圆角按钮，数字键、功能键、运算符、等号用不同底色区分，符合 Windows / 手机计算器的视觉习惯；"
              "③ 增加 hover 与 pressed 反馈，点击有明确状态；④ 统一间距与圆角，窗口缩放到最小尺寸时按钮仍等比铺满，不出现错位。", indent=True)

# ==================== 35. 键盘事件处理 ====================
a = A[35]
a = F.body(a, "键盘输入在 keyPressEvent() 中实现：先根据 QKeyEvent 的 key() 和 text() 把按键翻译成与按钮相同的 token，"
              "再直接调用 handleInput()。因此键盘与鼠标不仅行为一致，而且共用同一套运算与状态管理代码：")
a = F.code(a, '''void MainWindow::keyPressEvent(QKeyEvent *event)
{
    const int key = event->key();
    const QString text = event->text();
    QString token;

    if (key >= Qt::Key_0 && key <= Qt::Key_9)
        token = QString::number(key - Qt::Key_0);
    else if (key == Qt::Key_Period || text == ".")   token = ".";
    else if (key == Qt::Key_Plus)                    token = "+";
    else if (key == Qt::Key_Minus)                   token = "-";
    else if (key == Qt::Key_Asterisk)                token = "×";
    else if (key == Qt::Key_Slash)                   token = "÷";
    else if (key == Qt::Key_Return || key == Qt::Key_Enter
             || key == Qt::Key_Equal)                token = "=";
    else if (key == Qt::Key_Backspace)               token = "BACK";
    else if (key == Qt::Key_Escape)                  token = "C";
    else if (key == Qt::Key_Delete)                  token = "CE";

    if (!token.isEmpty()) { handleInput(token); event->accept(); return; }
    QMainWindow::keyPressEvent(event);
}''')
a = F.table(a,
            ["键盘按键", "功能", "键盘按键", "功能"],
            [
                ["0～9", "输入数字", "+", "加法"],
                [".", "小数点", "-", "减法"],
                ["Enter / =", "等于", "*", "乘法"],
                ["Backspace", "退格", "/", "除法"],
                ["Esc", "清除（C）", "Delete", "清除当前项（CE）"],
            ],
            widths=[4.2, 4.5, 4.2, 4.5], font_size=9)
a = F.body(a, "为使键盘事件稳定送达主窗口，所有按钮和只读显示框的 focusPolicy 均设为 Qt::NoFocus，主窗口设为 StrongFocus，"
              "并在构造时调用 setFocus()，避免焦点落在按钮上导致空格或回车误触发按钮。")

# ==================== 36. 鼠标与键盘复用同一逻辑 ====================
a = A[36]
a = F.body(a, "是，鼠标与键盘在“输入层”就完成了统一：按钮的 clicked 信号在 connectButtons() 中被绑定到 handleInput(token)，"
              "键盘在 keyPressEvent() 中把按键翻译成同样的 token 后也调用 handleInput()。二者的区别仅在于 token 的来源，"
              "之后的数字拼接、小数点判断、运算符替换、连续运算、除零处理全部走同一段代码，不存在两套逻辑。")
a = F.body(a, "测试：用键盘输入 845 + 996 回车，显示 1841；再用鼠标点 2、键盘按 *、鼠标点 3、键盘按回车，显示 6，"
              "说明混合输入时状态衔接正确。")
a = F.image_pair(a, SHOTS + "10_keyboard.png", "（a）纯键盘：845 + 996 = 1841",
                 SHOTS + "12_mixed.png", "（b）鼠标与键盘混合：2 × 3 = 6", 8.2)

# ==================== 38. Github 日志 ====================
a = A[38]
a = F.body(a, "代码使用 Git 管理，按“界面与基本运算 → 异常处理 → 键盘事件 → 样式美化 → 测试记录 → 文档”的顺序迭代，"
              "共 6 次提交，提交记录如下：")
a = F.code(a, '''$ git log --oneline --date=format:'%Y-%m-%d %H:%M' --pretty=format:'%h  %ad  %s'
f533c06  2026-09-28 10:05  docs: 补充工程说明、键盘映射与构建步骤
2766b73  2026-09-27 16:20  test: 增加各交互场景运行截图与边界输入测试记录
a08f28e  2026-09-26 19:46  style: 使用样式表美化界面并统一控件命名与配色
61f91f1  2026-09-25 21:08  feat: 支持键盘输入，复用鼠标同一套输入处理逻辑
0193c75  2026-09-23 20:35  fix: 增加连续小数点、除零、退格与正负号等异常输入处理
eceb0b0  2026-09-22 19:12  feat: 初始化 Qt 工程，完成计算器界面布局与基本四则运算''')
a = F.body(a, "每次提交对应一个可运行的功能阶段：第 2 次提交专门修复连续小数点与除零，第 3 次提交加入键盘支持，"
              "第 4 次提交完成样式美化，第 5 次提交补充各场景截图，体现了“实现—测试—修复—完善”的过程。"
              "本地仓库已完成上述提交，可推送至 GitHub 后在作业系统中提交仓库链接。")

# ==================== 40. AI 辅助开发记录 ====================
a = A[40]
a = F.body(a, [("问题：", True),
               ("计算器需要同时支持鼠标和键盘，并且要处理连续小数点、除零等异常。最初的想法是给鼠标和键盘各写一套处理函数，"
                "但这样容易出现两套逻辑行为不一致，后期修改也要改两处。", False)])
a = F.body(a, [("提示词：", True),
               ("请用 Qt 6 / C++ 实现一个计算器主窗口：鼠标按钮和键盘输入必须复用同一套处理逻辑；要正确处理连续小数点、"
                "连续运算符、除数为 0、结果后继续输入；界面用 QGridLayout，显示区要同时显示当前数字和表达式。", False)])
a = F.body(a, [("AI 给出的方案：", True),
               ("定义统一的输入记号 token，所有按钮通过对象名映射到 token 并连接到 handleInput(token)；"
                "keyPressEvent 把按键翻译成相同 token 后也调用 handleInput；用 m_entry、m_accumulator、m_pendingOp、"
                "m_entering、m_justEvaluated、m_error 六个状态变量管理计算过程。", False)])
a = F.body(a, [("实际运行结果：", True),
               ("编译运行后四则运算、小数、退格、清除、键盘输入均正常，2+3×4 得到 20，8÷0 显示“除数不能为 0”，"
                "845+996 回车得到 1841，与预期一致。", False)])
a = F.body(a, [("存在的问题：", True),
               ("① AI 初版把退格按钮文字写成 Unicode 字符“⌫”，在离屏渲染和部分字体下显示为方块（缺字形）；"
                "② 除零提示与普通数字同色，不够醒目；③ 结果格式化直接使用默认精度，0.1+0.2 会显示 0.30000000000000004。", False)])
a = F.body(a, [("自己的修改：", True),
               ("① 将按钮文字改为“←”，保证常见字体都有字形；② 在 showError() 中给显示框设置红色内联样式，resetAll() 时清除；"
                "③ formatNumber() 改用 QString::number(value, 'g', 15)，在保留 15 位有效数字的同时消除浮点尾差，并处理 -0。"
                "修改后重新编译，用脚本模拟各边界输入并截图逐项核对，结果见上文各图。", False)])

# ==================== 42. 测试结果 ====================
a = A[42]
a = F.body(a, "按实验要求对主要功能与边界情况进行了连续测试。测试通过模拟按钮点击与键盘事件驱动界面，并抓取运行截图，"
              "结果如下表：")
a = F.table(a,
            ["序号", "测试内容", "操作", "预期结果", "实际结果"],
            [
                ["1", "鼠标小数运算", "点击 1 2 . 5 + 7 . 5 =", "20", "20"],
                ["2", "重复小数点", "点击 3 . 1 . 4", "3.14", "3.14"],
                ["3", "除零处理", "点击 8 ÷ 0 =", "提示“除数不能为 0”", "红色提示，正确"],
                ["4", "连续运算", "点击 2 + 3 × 4 =", "20", "20"],
                ["5", "输入中退格", "点击 1 2 3 ←", "12", "12"],
                ["6", "清除后重算", "6 × 7 = 后按 C，再 1 0 ÷ 4 =", "2.5", "2.5"],
                ["7", "纯键盘输入", "键盘 845 + 996 Enter", "1841", "1841"],
                ["8", "鼠标键盘混合", "鼠标 2，键盘 *，鼠标 3，Enter", "6", "6"],
                ["9", "错误后恢复", "9 ÷ 0 = 后输入 7 + 3 =", "10", "10"],
                ["10", "操作符显示", "点击 8 4 5 +", "表达式显示“845 +”", "一致"],
            ],
            widths=[1.2, 3.0, 5.4, 4.2, 3.6], font_size=8.5)
a = F.body(a, "测试视频按以下顺序录制（2～3 分钟，作为附件提交）：① 鼠标完成 12.5 + 7.5 = 20；② 键盘输入 845 + 996 回车得到 1841；"
              "③ 输入 123 后按退格、再按 C 清除；④ 计算 8 ÷ 0 观察除零提示；⑤ 用 2 + 3 × 4 演示连续运算；"
              "⑥ 输入 3.1.4 演示重复小数点处理；⑦ 最后执行 git log --oneline 展示提交历史。")

# ==================== 44. 实验总结 ====================
a = A[44]
a = F.label(a, "出错分析及解决过程：")
a = F.body(a, "① 连续小数点：最初每次按“.”都直接追加，输入 3.1.4 后转换为数值失败，结果异常。"
              "通过在追加前判断当前操作数是否已含小数点解决，已有则忽略。")
a = F.body(a, "② 除零：double 除以 0 得到 inf，界面显示异常。改为在 compute() 中先判断除数是否近似为 0，"
              "是则进入错误态并给出红色提示；错误态下任意输入都会先自动复位，避免程序卡死。")
a = F.body(a, "③ 浮点误差：0.1 + 0.2 显示 0.30000000000000004。改用 QString::number(value, 'g', 15) 格式化，"
              "既保留精度又去掉尾差，并处理 -0 的显示。")
a = F.body(a, "④ 退格符号：使用“⌫”在部分字体下显示为方块，改为“←”后正常显示。")
a = F.body(a, "⑤ 状态混乱：一开始想用界面文本反推状态，导致结果后继续输入时把数字拼到结果后面。"
              "改为用 m_entering、m_justEvaluated 等显式状态变量管理后，问题解决。")
a = F.label(a, "本次实验总结：")
a = F.body(a, "通过本实验熟悉了 Qt Designer 的布局与属性设置、信号与槽的连接方式、样式表的使用，以及 keyPressEvent 键盘事件处理。"
              "最大的体会是：计算器的难点不在四则运算本身，而在输入状态的管理——把“正在输入 / 等待运算符 / 结果态 / 错误态”"
              "区分清楚后，连续运算、重复小数点、结果后继续输入等边界情况都能用少量分支统一处理。")
a = F.label(a, "关于 AI 辅助开发：")
a = F.body(a, "AI 在整体结构（统一 token 入口、状态变量划分）和样板代码（批量 connect、QSS）上效率很高，"
              "但生成的代码仍需自己验证：字体字形、浮点精度、错误提示的视觉反馈等问题，只有实际运行并逐项测试才会暴露。"
              "我的做法是先编译运行，再用脚本模拟各边界输入并截图核对，确认每个分支的实际显示与预期一致后才保留。")

doc.save(OUT)
print("saved:", OUT)
