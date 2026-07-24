#!/usr/bin/env python3
"""Build the detailed v2.0 PRD for the Shangzhi AI merchant advisor.

Design preset: compact_reference_guide.
Named overrides:
- Noto Sans CJK SC is used across Latin and CJK text for deterministic
  LibreOffice/Word rendering on the target macOS workspace.
- Brand purple (#5146C9) replaces the preset heading blue consistently.
- Light lavender (#EEF1FF) replaces the standard blue-gray table header fill.

The document is generated from the current product implementation and explicitly
labels all business metrics, research evidence and experiment results as mock data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "assets" / "shangzhi-prd.docx"
SCREENSHOTS = ROOT / "public" / "screenshots"
COVER_IMAGE = ROOT / "public" / "og-v3.png"

PURPLE = "5146C9"
PURPLE_DARK = "302A75"
CYAN = "29BEE8"
MAGENTA = "D72DBA"
INK = "202344"
MUTED = "697386"
LIGHT = "F7F8FF"
HEADER_FILL = "EEF1FF"
GRID = "D8DDF0"
POSITIVE = "16795A"
WARNING = "8A6100"
RISK = "A33232"
WHITE = "FFFFFF"

CONTENT_DXA = 9360
TABLE_INDENT_DXA = 120
CELL_MARGIN_TOP_BOTTOM = 80
CELL_MARGIN_SIDE = 120


TOC: list[tuple[int, str, str, str]] = [
    (1, "1", "产品定义", "sec-1"),
    (2, "1.1", "背景、机会与问题定义", "sec-1-1"),
    (2, "1.2", "产品定位与价值主张", "sec-1-2"),
    (2, "1.3", "数据声明与项目边界", "sec-1-3"),
    (1, "2", "用户研究与需求证据", "sec-2"),
    (2, "2.1", "目标用户与角色", "sec-2-1"),
    (2, "2.2", "模拟访谈洞察", "sec-2-2"),
    (2, "2.3", "核心用户旅程", "sec-2-3"),
    (2, "2.4", "真实调研计划", "sec-2-4"),
    (1, "3", "产品目标、范围与里程碑", "sec-3"),
    (2, "3.1", "北极星指标与目标树", "sec-3-1"),
    (2, "3.2", "MVP范围与非目标", "sec-3-2"),
    (2, "3.3", "版本计划", "sec-3-3"),
    (1, "4", "信息架构、角色与权限", "sec-4"),
    (2, "4.1", "三入口信息架构", "sec-4-1"),
    (2, "4.2", "商家端与内部后台边界", "sec-4-2"),
    (2, "4.3", "角色权限矩阵", "sec-4-3"),
    (2, "4.4", "运行模式与环境标识", "sec-4-4"),
    (1, "5", "商家经营端：总体设计", "sec-5"),
    (2, "5.1", "页面目标与布局", "sec-5-1"),
    (2, "5.2", "关键业务闭环", "sec-5-2"),
    (2, "5.3", "全局状态与交互原则", "sec-5-3"),
    (1, "6", "商家经营端：详细功能需求", "sec-6"),
    (2, "6.1", "经营总览", "sec-6-1"),
    (3, "6.1.1", "指标卡、健康分与机会列表", "sec-6-1-1"),
    (2, "6.2", "AI经营顾问", "sec-6-2"),
    (3, "6.2.1", "流式对话、证据与建议", "sec-6-2-1"),
    (3, "6.2.2", "高风险行动确认", "sec-6-2-2"),
    (2, "6.3", "今日任务", "sec-6-3"),
    (2, "6.4", "商圈竞品", "sec-6-4"),
    (2, "6.5", "空态、错误态与降级", "sec-6-5"),
    (1, "7", "AI产品运营后台：总体设计", "sec-7"),
    (2, "7.1", "后台目标与导航", "sec-7-1"),
    (2, "7.2", "汇总数据与门店数据隔离", "sec-7-2"),
    (1, "8", "策略研究与商家沟通漏斗", "sec-8"),
    (2, "8.1", "行业策略研究", "sec-8-1"),
    (2, "8.2", "完整转化漏斗", "sec-8-2"),
    (2, "8.3", "分层与诊断", "sec-8-3"),
    (1, "9", "A/B实验与实验配置", "sec-9"),
    (2, "9.1", "实验结果页", "sec-9-1"),
    (2, "9.2", "实验创建器", "sec-9-2"),
    (2, "9.3", "实验生命周期与统计规则", "sec-9-3"),
    (1, "10", "模型评测与标注工作台", "sec-10"),
    (2, "10.1", "评测集设计", "sec-10-1"),
    (2, "10.2", "八维评分与严重错误", "sec-10-2"),
    (2, "10.3", "标注、仲裁与一致性", "sec-10-3"),
    (1, "11", "Badcase、版本与运行监控", "sec-11"),
    (2, "11.1", "Badcase修复闭环", "sec-11-1"),
    (2, "11.2", "Agent版本对比与准入", "sec-11-2"),
    (2, "11.3", "运行监控与Trace复盘", "sec-11-3"),
    (1, "12", "Agent产品与技术设计", "sec-12"),
    (2, "12.1", "系统架构", "sec-12-1"),
    (2, "12.2", "LangGraph状态机", "sec-12-2"),
    (2, "12.3", "意图识别与工具清单", "sec-12-3"),
    (2, "12.4", "记忆、行动与人工确认", "sec-12-4"),
    (2, "12.5", "Guardrail与降级策略", "sec-12-5"),
    (1, "13", "Prompt策略与输出协议", "sec-13"),
    (2, "13.1", "Prompt结构", "sec-13-1"),
    (2, "13.2", "结构化输出Schema", "sec-13-2"),
    (2, "13.3", "版本管理与实验", "sec-13-3"),
    (1, "14", "数据、指标与埋点设计", "sec-14"),
    (2, "14.1", "数据来源与授权", "sec-14-1"),
    (2, "14.2", "核心指标口径", "sec-14-2"),
    (2, "14.3", "事件埋点", "sec-14-3"),
    (2, "14.4", "数据质量与隔离", "sec-14-4"),
    (1, "15", "接口与数据模型", "sec-15"),
    (2, "15.1", "前后端拓扑", "sec-15-1"),
    (2, "15.2", "API清单", "sec-15-2"),
    (2, "15.3", "SSE事件协议", "sec-15-3"),
    (2, "15.4", "核心对象", "sec-15-4"),
    (1, "16", "非功能、安全与合规", "sec-16"),
    (2, "16.1", "性能、可靠性与可观测性", "sec-16-1"),
    (2, "16.2", "隐私、权限与审计", "sec-16-2"),
    (2, "16.3", "可访问性与兼容性", "sec-16-3"),
    (1, "17", "验收测试与上线准入", "sec-17"),
    (2, "17.1", "P0功能验收", "sec-17-1"),
    (2, "17.2", "AI质量与安全验收", "sec-17-2"),
    (2, "17.3", "UAT退出条件", "sec-17-3"),
    (1, "18", "路线图、风险与开放问题", "sec-18"),
    (2, "18.1", "实施路线图", "sec-18-1"),
    (2, "18.2", "项目风险", "sec-18-2"),
    (2, "18.3", "开放问题", "sec-18-3"),
    (1, "19", "附录", "sec-19"),
    (2, "19.1", "术语表", "sec-19-1"),
    (2, "19.2", "模拟数据清单", "sec-19-2"),
    (2, "19.3", "项目交付物与代码索引", "sec-19-3"),
]


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def set_run_font(run, size: float | None = None, bold: bool | None = None,
                 color: str | None = None, italic: bool | None = None) -> None:
    run.font.name = "Noto Sans CJK SC"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Noto Sans CJK SC")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Noto Sans CJK SC")
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = rgb(color)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top: int = CELL_MARGIN_TOP_BOTTOM,
                     start: int = CELL_MARGIN_SIDE,
                     bottom: int = CELL_MARGIN_TOP_BOTTOM,
                     end: int = CELL_MARGIN_SIDE) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color: str = GRID, size: str = "6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)


def set_table_geometry(table, widths_dxa: Sequence[int]) -> None:
    if sum(widths_dxa) != CONTENT_DXA:
        raise ValueError(f"Table widths must total {CONTENT_DXA}: {widths_dxa}")
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(CONTENT_DXA))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(TABLE_INDENT_DXA))
    tbl_ind.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths_dxa[idx]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.width = Inches(widths_dxa[idx] / 1440)


def mark_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def style_cell_text(cell, header: bool = False, align: WD_ALIGN_PARAGRAPH | None = None) -> None:
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.15
        if align is not None:
            paragraph.alignment = align
        for run in paragraph.runs:
            set_run_font(run, size=8.7 if not header else 9.0,
                         bold=header, color=PURPLE_DARK if header else INK)


def add_table(doc: Document, headers: Sequence[str], rows: Sequence[Sequence[str]],
              widths_dxa: Sequence[int], center_columns: Iterable[int] = ()) -> object:
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_geometry(table, widths_dxa)
    set_table_borders(table)
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = str(header)
        set_cell_shading(cell, HEADER_FILL)
        style_cell_text(cell, header=True,
                        align=WD_ALIGN_PARAGRAPH.CENTER if index in center_columns else WD_ALIGN_PARAGRAPH.LEFT)
    mark_repeat_header(table.rows[0])
    for values in rows:
        row = table.add_row()
        for index, value in enumerate(values):
            cell = row.cells[index]
            cell.text = str(value)
            if len(table.rows) % 2 == 1:
                set_cell_shading(cell, "FBFCFF")
            style_cell_text(cell, align=WD_ALIGN_PARAGRAPH.CENTER if index in center_columns else WD_ALIGN_PARAGRAPH.LEFT)
        set_table_geometry(table, widths_dxa)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_bookmark(paragraph, name: str, bookmark_id: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def add_internal_link(paragraph, anchor: str, text: str) -> None:
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), anchor)
    run = OxmlElement("w:r")
    run_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), PURPLE)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "none")
    run_pr.extend([color, underline])
    run.append(run_pr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("第 ")
    set_run_font(run, size=8.5, color=MUTED)
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])
    tail = paragraph.add_run(" 页")
    set_run_font(tail, size=8.5, color=MUTED)


def add_heading(doc: Document, number: str, title: str, level: int, anchor: str,
                bookmark_id: int, new_page: bool = False) -> int:
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    if new_page and number == "1":
        # Use a paragraph property instead of inserting an empty break
        # paragraph. This keeps major product phases visually separated
        # without producing accidental blank pages at natural page boundaries.
        paragraph.paragraph_format.page_break_before = True
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run(f"{number}  {title}")
    add_bookmark(paragraph, anchor, bookmark_id)
    return bookmark_id + 1


def add_body(doc: Document, text: str, bold_prefix: str | None = None) -> None:
    paragraph = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        first = paragraph.add_run(bold_prefix)
        set_run_font(first, bold=True, color=PURPLE_DARK)
        rest = paragraph.add_run(text[len(bold_prefix):])
        set_run_font(rest)
    else:
        run = paragraph.add_run(text)
        set_run_font(run)


def add_bullets(doc: Document, items: Sequence[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        run = p.add_run(item)
        set_run_font(run)


def add_numbered(doc: Document, items: Sequence[str]) -> None:
    numbering = doc.part.numbering_part.element
    style_num_id = doc.styles["List Number"]._element.pPr.numPr.numId.val
    style_num = numbering.xpath(f'./w:num[@w:numId="{style_num_id}"]')[0]
    abstract_num_id = style_num.abstractNumId.val
    current_ids = [int(node.get(qn("w:numId"))) for node in numbering.xpath("./w:num")]
    new_num_id = max(current_ids) + 1

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(new_num_id))
    abstract = OxmlElement("w:abstractNumId")
    abstract.set(qn("w:val"), str(abstract_num_id))
    num.append(abstract)
    level_override = OxmlElement("w:lvlOverride")
    level_override.set(qn("w:ilvl"), "0")
    start_override = OxmlElement("w:startOverride")
    start_override.set(qn("w:val"), "1")
    level_override.append(start_override)
    num.append(level_override)
    numbering.append(num)

    for item in items:
        p = doc.add_paragraph(style="List Number")
        num_pr = p._p.get_or_add_pPr().get_or_add_numPr()
        num_pr.get_or_add_ilvl().val = 0
        num_pr.get_or_add_numId().val = new_num_id
        run = p.add_run(item)
        set_run_font(run)


def add_callout(doc: Document, label: str, text: str, tone: str = "info") -> None:
    fills = {"info": HEADER_FILL, "success": "EAF7F2", "warning": "FFF6DE", "risk": "FDECEC"}
    colors = {"info": PURPLE_DARK, "success": POSITIVE, "warning": WARNING, "risk": RISK}
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [CONTENT_DXA])
    set_table_borders(table, color=fills[tone], size="4")
    cell = table.cell(0, 0)
    set_cell_shading(cell, fills[tone])
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    lead = p.add_run(f"{label}  ")
    set_run_font(lead, size=9.4, bold=True, color=colors[tone])
    body = p.add_run(text)
    set_run_font(body, size=9.4, color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def add_process(doc: Document, steps: Sequence[tuple[str, str]]) -> None:
    if len(steps) != 5:
        raise ValueError("Process strip expects exactly five steps")
    table = doc.add_table(rows=1, cols=5)
    set_table_geometry(table, [1872, 1872, 1872, 1872, 1872])
    set_table_borders(table, color="C7CDEF", size="6")
    for index, (label, detail) in enumerate(steps):
        cell = table.rows[0].cells[index]
        set_cell_shading(cell, HEADER_FILL if index % 2 == 0 else LIGHT)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        top = p.add_run(f"{index + 1:02d}\n")
        set_run_font(top, size=10.5, bold=True, color=PURPLE)
        name = p.add_run(f"{label}\n")
        set_run_font(name, size=8.8, bold=True, color=INK)
        desc = p.add_run(detail)
        set_run_font(desc, size=7.4, color=MUTED)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def add_figure(doc: Document, path: Path, caption: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    inline_shape = run.add_picture(str(path), width=Inches(6.35))
    c_nv_pr = inline_shape._inline.graphic.graphicData.pic.nvPicPr.cNvPr
    c_nv_pr.set("descr", caption)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(8)
    r = cap.add_run(caption)
    set_run_font(r, size=8.2, italic=True, color=MUTED)


def add_requirement_table(doc: Document, rows: Sequence[Sequence[str]]) -> None:
    add_table(
        doc,
        ["需求ID", "优先级", "功能要求", "验收口径"],
        rows,
        [1200, 900, 4400, 2860],
        center_columns=(0, 1),
    )


def add_cover(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    p.add_run().add_picture(str(COVER_IMAGE), width=Inches(6.45))
    kicker = doc.add_paragraph()
    kicker.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = kicker.add_run("PRODUCT REQUIREMENTS DOCUMENT")
    set_run_font(r, size=10, bold=True, color=PURPLE)
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(2)
    title.paragraph_format.space_after = Pt(4)
    r = title.add_run("商智 AI 商家经营顾问")
    set_run_font(r, size=28, bold=True, color=PURPLE_DARK)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(16)
    r = subtitle.add_run("详细产品需求文档 PRD · v2.0")
    set_run_font(r, size=14, color=PURPLE)
    add_callout(
        doc,
        "一句话定义",
        "面向本地生活中小商家的AI经营诊断与行动产品，连接经营数据、证据解释、商家确认、任务执行与效果复盘。",
    )
    metadata = doc.add_paragraph()
    metadata.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = metadata.add_run("版本日期：2026-07-24  |  产品阶段：高保真MVP  |  数据类型：模拟数据")
    set_run_font(r, size=9.2, color=MUTED)


def add_document_control(doc: Document) -> None:
    doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.add_run("文档控制")
    add_table(
        doc,
        ["字段", "内容"],
        [
            ["文档名称", "商智 AI 商家经营顾问 - 详细产品需求文档"],
            ["版本", "v2.0（详细版）"],
            ["目标读者", "产品、设计、算法、数据、前后端、测试、运营与面试评审"],
            ["当前状态", "作品集MVP；前端公开演示；Python Agent可本地运行"],
            ["数据声明", "全部经营指标、访谈、实验结果、行业基准与评测案例均为模拟"],
            ["作者角色", "AI产品经理 / 项目原型负责人"],
        ],
        [1900, 7460],
    )
    add_callout(
        doc,
        "v2.0升级重点",
        "由摘要型PRD升级为可评审规格：补齐三级目录、页面级功能、字段与状态、Agent流程、接口、埋点、权限、异常、验收与上线准入。",
        "success",
    )
    add_table(
        doc,
        ["版本", "日期", "主要变化", "状态"],
        [
            ["v1.0", "2026-07-23", "产品概念、研究框架、指标、实验和评测摘要", "已归档"],
            ["v2.0", "2026-07-24", "角色拆分、详细功能规格、Agent/API/数据/测试全量补充", "当前版本"],
        ],
        [1100, 1500, 5260, 1500],
        center_columns=(0, 1, 3),
    )
    add_body(doc, "阅读说明：本文按“业务目标 → 角色与场景 → 页面功能 → Agent与数据 → 测试上线”组织。需求ID用于设计、研发、测试和评测追踪。")
    add_bullets(
        doc,
        [
            "P0：MVP必须交付；P1：验证后增强；P2：规模化阶段考虑。",
            "“模拟”表示当前作品集数据或规则结果；“生产化”条目描述真实上线所需能力。",
            "涉及价格、预算、发布、批量回复和库存处理的操作均不得自动执行。",
        ],
    )


def add_toc(doc: Document) -> None:
    doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.add_run("目录")
    add_callout(doc, "目录说明", "目录展示三级结构；点击条目可跳转到对应章节。", "info")
    for level, number, title, anchor in TOC:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.30 * (level - 1))
        p.paragraph_format.space_after = Pt(2 if level == 1 else 1)
        if level == 1:
            p.paragraph_format.space_before = Pt(4)
        prefix = p.add_run(f"{number}  ")
        set_run_font(prefix, size=9.2 if level == 1 else 8.4,
                     bold=level == 1, color=PURPLE if level == 1 else MUTED)
        add_internal_link(p, anchor, title)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Noto Sans CJK SC"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Noto Sans CJK SC")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Noto Sans CJK SC")
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
    normal.font.size = Pt(10.2)
    normal.font.color.rgb = rgb(INK)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for level, size, before, after, color in (
        (1, 16, 18, 10, PURPLE_DARK),
        (2, 13, 14, 7, PURPLE),
        (3, 11.5, 10, 5, PURPLE_DARK),
    ):
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Noto Sans CJK SC"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Noto Sans CJK SC")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Noto Sans CJK SC")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = rgb(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for style_name in ("List Bullet", "List Number"):
        style = doc.styles[style_name]
        style.font.name = "Noto Sans CJK SC"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Noto Sans CJK SC")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Noto Sans CJK SC")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Noto Sans CJK SC")
        style.font.size = Pt(10.0)
        style.font.color.rgb = rgb(INK)
        style.paragraph_format.left_indent = Inches(0.375)
        style.paragraph_format.first_line_indent = Inches(-0.188)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.25

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    left = hp.add_run("商智 AI 商家经营顾问")
    set_run_font(left, size=8.4, bold=True, color=PURPLE)
    right = hp.add_run("                                      PRD v2.0")
    set_run_font(right, size=8.4, color=MUTED)

    first_header = section.first_page_header
    first_header.paragraphs[0].text = ""
    footer = section.footer
    add_page_number(footer.paragraphs[0])
    first_footer = section.first_page_footer
    first_footer.paragraphs[0].text = ""

    settings = doc.settings.element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")

    doc.core_properties.title = "商智 AI 商家经营顾问 - 详细产品需求文档"
    doc.core_properties.subject = "本地生活商家经营诊断 Agent 产品 PRD"
    doc.core_properties.author = "商智项目组"
    doc.core_properties.keywords = "AI产品经理, PRD, 商家经营, LangGraph, Agent, A/B测试, 模型评测"


def build() -> None:
    doc = Document()
    configure_document(doc)
    add_cover(doc)
    add_document_control(doc)
    add_toc(doc)
    bookmark_id = 100

    # 1. Product definition
    bookmark_id = add_heading(doc, "1", "产品定义", 1, "sec-1", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "1.1", "背景、机会与问题定义", 2, "sec-1-1", bookmark_id)
    add_body(doc, "本地生活商家已经拥有订单、流量、评价、库存和营销报表，但多数中小商家缺少时间与分析能力，难以把指标异常转成优先级明确、风险可控的行动。")
    add_table(
        doc,
        ["现状", "核心问题", "产品机会"],
        [
            ["数据分散在多个后台", "无法快速归因，经营者被迫凭经验判断", "聚合受控事实并生成证据链"],
            ["传统机器人以FAQ为主", "只能被动回答，不能主动发现经营问题", "事件触发式AI经营顾问"],
            ["建议缺少验证方式", "商家不知道成本、风险和是否有效", "建议绑定任务、指标和复盘窗口"],
            ["高风险操作缺少约束", "错误降价或加预算可能造成直接损失", "二次确认、审计与回滚"],
        ],
        [2800, 3000, 3560],
    )
    add_callout(doc, "问题定义", "商家缺少的不是更多图表，而是可信、可执行、可验证的下一步。", "info")
    bookmark_id = add_heading(doc, "1.2", "产品定位与价值主张", 2, "sec-1-2", bookmark_id)
    add_body(doc, "商智定位为“经营数据到行动闭环”的AI顾问：发现异常、检索证据、解释原因、给出建议、请求确认、创建任务并复盘结果。")
    add_process(
        doc,
        [
            ("发现异常", "指标监控与事件触发"),
            ("理解原因", "事实证据与原因假设"),
            ("评估方案", "动作、成本、风险、指标"),
            ("确认执行", "高风险操作二次确认"),
            ("复盘迭代", "业务结果与模型评测"),
        ],
    )
    bookmark_id = add_heading(doc, "1.3", "数据声明与项目边界", 2, "sec-1-3", bookmark_id)
    add_bullets(
        doc,
        [
            "当前所有业务数值、访谈、行业基准、实验结果与评测案例均为模拟数据。",
            "公开演示默认运行DEMO模式；Python服务不可用时显示FALLBACK，不伪装为真实模型结果。",
            "真实生产环境必须通过商家授权接入平台订单、流量、评价、营销、库存和门店配置。",
            "项目不训练基础模型，不自动替商家执行价格、预算、发布、批量回复或库存处理。",
            "竞品模块只展示商圈聚合基准，不展示其他商家的私有经营明细。",
        ],
    )

    # 2. Research
    bookmark_id = add_heading(doc, "2", "用户研究与需求证据", 1, "sec-2", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "2.1", "目标用户与角色", 2, "sec-2-1", bookmark_id)
    add_table(
        doc,
        ["角色", "典型特征", "核心任务", "成功标准"],
        [
            ["单店经营者", "每天仅有10-20分钟看数据；对风险敏感", "判断今天先处理什么", "建议易懂、可信、可执行"],
            ["连锁区域经理", "管理多门店；关注异常门店与标准化", "发现共性问题并分配任务", "异常覆盖、任务闭环、门店对比"],
            ["AI产品/策略运营", "负责Prompt、实验和规模化", "提升沟通转化并控制风险", "业务指标与护栏同时改善"],
            ["算法/数据/工程", "负责模型、工具和数据链路", "保证准确、稳定、可追踪", "质量、成本、延迟和成功率达标"],
            ["标注/审核员", "按规则对案例评分与仲裁", "发现严重错误并反馈修复", "一致性与严重错误召回率达标"],
        ],
        [1600, 2700, 2500, 2560],
    )
    bookmark_id = add_heading(doc, "2.2", "模拟访谈洞察", 2, "sec-2-2", bookmark_id)
    add_table(
        doc,
        ["对象", "行业/规模", "模拟原话", "需求信号"],
        [
            ["李记小馆", "餐饮/1店", "别只告诉我转化下降，告诉我是哪里的问题。", "原因解释与优先级"],
            ["悦己便利", "零售/3店", "我不缺报表，缺的是今天先处理哪十个商品。", "SKU级行动建议"],
            ["乐玩桌游", "娱乐/2店", "周末不缺客流，工作日下午最难卖。", "分时策略"],
            ["巷口咖啡", "餐饮/2店", "活动很多，但算不清到底有没有赚。", "增量归因"],
            ["轻享SPA", "娱乐/4店", "爽约高，但不能一直靠人工提醒。", "预测与自动提醒"],
        ],
        [1300, 1500, 4000, 2560],
    )
    add_callout(doc, "研究边界", "以上访谈为作品集模拟，用于展示研究框架。生产项目需补充招募记录、录音、逐字稿、证据编码与结论置信度。", "warning")
    bookmark_id = add_heading(doc, "2.3", "核心用户旅程", 2, "sec-2-3", bookmark_id)
    add_table(
        doc,
        ["阶段", "商家问题", "产品响应", "关键指标"],
        [
            ["发现", "发生了什么？", "主动提醒并量化影响", "消息阅读率"],
            ["理解", "为什么？", "事实证据、对比基准与假设", "有效回复率"],
            ["决策", "做什么？", "优先级、步骤、成本、风险与验证指标", "建议采纳率"],
            ["执行", "会不会出错？", "预览、二次确认和任务状态", "任务完成率"],
            ["复盘", "是否有效？", "7日窗口、对照或稳健基线", "经营改善率"],
        ],
        [1100, 2100, 3860, 2300],
    )
    bookmark_id = add_heading(doc, "2.4", "真实调研计划", 2, "sec-2-4", bookmark_id)
    add_numbered(
        doc,
        [
            "按餐饮、零售、休闲娱乐各招募5-8家商户，覆盖单店与小连锁。",
            "完成30分钟半结构访谈，收集最近一次经营异常、判断路径和实际操作记录。",
            "用主题编码法提炼任务、痛点、现有替代方案、信任门槛与高风险操作。",
            "邀请5家商户完成可用性测试，观察是否能在3分钟内理解异常并完成一次任务。",
            "将结论分为已证实、方向性和待验证，不把单个案例直接推广为普遍需求。",
        ],
    )

    # 3. Goals and scope
    bookmark_id = add_heading(doc, "3", "产品目标、范围与里程碑", 1, "sec-3", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "3.1", "北极星指标与目标树", 2, "sec-3-1", bookmark_id)
    add_callout(doc, "北极星指标", "AI建议带来的7日有效经营改善商家数。必须同时满足建议被理解、被采纳、被执行，并产生可归因改善。", "success")
    add_table(
        doc,
        ["层级", "指标", "口径/目标"],
        [
            ["沟通", "阅读率、回复率、有效会话率", "按去重商家计算；回复率MVP提升≥3pp"],
            ["采纳", "建议采纳率、任务创建率", "建议采纳率≥45%"],
            ["执行", "任务完成率、高风险确认覆盖率", "完成率≥55%；确认覆盖率=100%"],
            ["业务", "订单/GMV/周转/利用率增量", "优先使用实验增量；无法实验时注明归因限制"],
            ["质量", "八维均分、错误建议率、严重错误率", "离线均分≥4.5；错误建议率<1%"],
            ["护栏", "退订、投诉、转人工、成本和延迟", "任一超阈值自动暂停策略"],
        ],
        [1200, 2800, 5360],
    )
    bookmark_id = add_heading(doc, "3.2", "MVP范围与非目标", 2, "sec-3-2", bookmark_id)
    add_table(
        doc,
        ["范围", "包含", "不包含"],
        [
            ["商家端", "经营总览、AI诊断、经营机会、今日任务、商圈聚合基准", "真实登录、支付、自动发布、跨门店管理"],
            ["内部后台", "研究、漏斗、实验、评测、Badcase、版本、监控、标注", "真实生产流量控制、财务结算、组织审批流"],
            ["Agent", "工具检索、结构化诊断、证据审核、记忆、行动确认", "自主修改预算、价格、库存和公开内容"],
            ["数据", "内置模拟快照与评测数据", "真实商户PII、订单明细和平台敏感数据"],
        ],
        [1400, 4080, 3880],
    )
    bookmark_id = add_heading(doc, "3.3", "版本计划", 2, "sec-3-3", bookmark_id)
    add_table(
        doc,
        ["阶段", "周期", "范围", "退出条件"],
        [
            ["MVP", "0-4周", "餐饮单场景、离线评测、人工确认", "P0功能通过；错误建议率<1%"],
            ["验证", "5-8周", "A/B实验、任务执行、7日复盘", "主要指标显著且护栏安全"],
            ["扩展", "9-12周", "零售/娱乐、行业Prompt和回归集", "分层质量无明显退化"],
            ["规模化", "3-6月", "运营平台、自动准入、在线监控", "版本治理、审计和告警完备"],
        ],
        [1300, 1200, 3860, 3000],
        center_columns=(1,),
    )

    # 4. IA and permissions
    bookmark_id = add_heading(doc, "4", "信息架构、角色与权限", 1, "sec-4", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "4.1", "三入口信息架构", 2, "sec-4-1", bookmark_id)
    add_figure(doc, SCREENSHOTS / "01-project-home.png", "图1  项目介绍首页：产品边界、双角色入口和作品集说明")
    add_table(
        doc,
        ["路由", "使用者", "主要内容", "边界"],
        [
            ["/", "面试官/评审/项目访客", "项目定位、产品架构、数据声明和交付物", "不显示商家私有经营数据"],
            ["/merchant", "模拟单店商家", "本店经营数据、AI建议、任务和商圈基准", "只看本店与聚合基准"],
            ["/ops", "内部产品/算法/运营", "汇总漏斗、实验、评测、Badcase与监控", "不模拟为商家可见页面"],
        ],
        [1300, 2000, 3860, 2200],
    )
    bookmark_id = add_heading(doc, "4.2", "商家端与内部后台边界", 2, "sec-4-2", bookmark_id)
    add_bullets(
        doc,
        [
            "商家端回答“我的店发生了什么、为什么、下一步做什么”。",
            "内部后台回答“AI是否有效、安全、稳定，以及下一版本怎么改”。",
            "商家端不展示Prompt、模型版本、Badcase和跨商户汇总指标。",
            "内部后台只展示授权后的匿名或聚合数据，不允许运营直接读取无关商家的明细。",
        ],
    )
    bookmark_id = add_heading(doc, "4.3", "角色权限矩阵", 2, "sec-4-3", bookmark_id)
    add_table(
        doc,
        ["角色", "查看权限", "操作权限", "禁止操作"],
        [
            ["商家", "本店指标、建议、任务、聚合基准", "确认/拒绝建议，撤回未执行任务", "查看他店明细、修改模型策略"],
            ["策略产品/运营", "聚合漏斗、实验、评测、版本与监控", "创建实验、申请扩量、回滚Prompt", "绕过准入直接全量"],
            ["算法/数据", "匿名日志、模型和数据质量", "发布候选模型、维护指标口径", "读取非授权PII"],
            ["审核员", "待标注案例与规则", "评分、严重错误标记、仲裁", "修改模型或经营数据"],
            ["管理员", "系统配置和审计", "角色授权、紧急暂停", "删除不可追溯审计记录"],
        ],
        [1400, 2700, 3000, 2260],
    )
    bookmark_id = add_heading(doc, "4.4", "运行模式与环境标识", 2, "sec-4-4", bookmark_id)
    add_table(
        doc,
        ["模式", "触发条件", "模型/数据", "前端标识"],
        [
            ["LIVE", "配置有效模型密钥且调用成功", "真实模型 + 当前授权数据", "LIVE/模型名"],
            ["DEMO", "未配置Python公网Agent或明确演示", "offline-rule-engine + 模拟快照", "DEMO/模拟数据"],
            ["FALLBACK", "上游服务超时、错误或不可用", "离线规则引擎 + 模拟/缓存数据", "FALLBACK/降级提示"],
        ],
        [1200, 2900, 3160, 2100],
    )

    # 5. Merchant overview
    bookmark_id = add_heading(doc, "5", "商家经营端：总体设计", 1, "sec-5", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "5.1", "页面目标与布局", 2, "sec-5-1", bookmark_id)
    add_figure(doc, SCREENSHOTS / "02-merchant-workspace.png", "图2  商家经营工作台：经营指标、AI顾问、经营机会与今日任务")
    add_body(doc, "首屏必须在3分钟内帮助商家回答三个问题：当前经营是否健康、最值得优先处理的事项是什么、AI建议依据和风险是什么。")
    bookmark_id = add_heading(doc, "5.2", "关键业务闭环", 2, "sec-5-2", bookmark_id)
    add_process(
        doc,
        [
            ("查看异常", "健康分和机会提醒"),
            ("追问原因", "AI检索证据并解释"),
            ("生成方案", "步骤、风险和验证指标"),
            ("确认任务", "高风险二次确认"),
            ("复盘结果", "任务状态与经营变化"),
        ],
    )
    bookmark_id = add_heading(doc, "5.3", "全局状态与交互原则", 2, "sec-5-3", bookmark_id)
    add_table(
        doc,
        ["状态", "界面行为", "用户可执行动作"],
        [
            ["加载中", "骨架屏或步骤流；不可显示旧数据为当前结果", "取消请求、继续浏览已缓存模块"],
            ["正常", "显示更新时间、数据范围和模式", "查看证据、生成建议、创建任务"],
            ["证据不足", "明确未知项，不生成确定性结论", "补充信息、缩小问题或转人工"],
            ["高风险", "显示影响预览、风险等级和确认门", "确认或拒绝；默认不执行"],
            ["服务降级", "显示FALLBACK与原因，不伪装真实模型", "重试或使用离线建议"],
            ["无数据", "解释缺失字段和接入要求", "绑定数据源或查看示例"],
        ],
        [1300, 4800, 3260],
    )

    # 6. Merchant detailed requirements
    bookmark_id = add_heading(doc, "6", "商家经营端：详细功能需求", 1, "sec-6", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "6.1", "经营总览", 2, "sec-6-1", bookmark_id)
    add_body(doc, "用户故事：作为门店经营者，我希望一眼看到今天最重要的经营变化，并理解异常是否值得立即处理。")
    bookmark_id = add_heading(doc, "6.1.1", "指标卡、健康分与机会列表", 3, "sec-6-1-1", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["M-OV-001", "P0", "展示今日实收、支付订单、到店转化率和店铺评分；同时显示对比周期与趋势。", "指标具有名称、值、单位、对比方向、时间范围和更新时间。"],
            ["M-OV-002", "P0", "计算0-100经营健康分，并显示近7日变化。", "分数必须可追溯到指标规则；缺少关键数据时显示不可计算。"],
            ["M-OV-003", "P0", "展示最多3条经营机会，包含优先级、证据摘要、预计影响和入口。", "机会按影响×置信度×可执行性排序；不得承诺确定收益。"],
            ["M-OV-004", "P1", "允许切换日/周/月观察周期。", "切换后所有卡片口径一致，URL或状态可恢复。"],
        ],
    )
    add_table(
        doc,
        ["字段", "类型", "规则", "示例"],
        [
            ["metric_id", "string", "稳定唯一；不得使用展示文案作为主键", "paid_orders"],
            ["value", "number/null", "原始值；缺失为null而非0", "186"],
            ["display", "string", "带货币、百分比或小数格式", "¥12,680"],
            ["comparison", "number/null", "与固定对比周期变化", "+8.6%"],
            ["updated_at", "timestamp", "显示数据新鲜度", "2026-07-24 17:36"],
        ],
        [1700, 1300, 3960, 2400],
    )
    bookmark_id = add_heading(doc, "6.2", "AI经营顾问", 2, "sec-6-2", bookmark_id)
    add_body(doc, "用户故事：作为商家，我希望用自然语言追问经营问题，看到AI引用的事实、原因假设、建议步骤和风险，而不是只得到一段无法验证的答案。")
    bookmark_id = add_heading(doc, "6.2.1", "流式对话、证据与建议", 3, "sec-6-2-1", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["M-AI-001", "P0", "支持1-1200字输入并以SSE展示retrieve、diagnose、guardrail、persist步骤。", "每个步骤具有状态；最终事件包含结构化AgentResponse。"],
            ["M-AI-002", "P0", "答案必须区分结论、证据、假设、建议、缺失数据和置信度。", "每条事实引用工具来源；未知信息明确标记。"],
            ["M-AI-003", "P0", "提供“为什么转化下降”“帮我优化双人套餐”等快捷问题。", "快捷问题可编辑；不自动发送敏感操作。"],
            ["M-AI-004", "P1", "保留同一thread的短期历史，用于多轮追问。", "刷新后可按thread_id读取；不同商家历史隔离。"],
        ],
    )
    add_table(
        doc,
        ["界面块", "必显信息", "异常处理"],
        [
            ["结论", "一句话判断、模式、模型和置信度", "证据不足时不得输出确定性归因"],
            ["证据", "指标、观测值、对比、来源", "来源不可用时移除对应结论"],
            ["假设", "可能原因及验证方式", "不把相关性写成因果"],
            ["建议", "理由、1-5步、风险、预期信号", "涉及高风险动作进入确认门"],
            ["Trace", "节点、工具、耗时和状态", "生产环境仅内部后台展示详细Trace"],
        ],
        [1400, 4380, 3580],
    )
    bookmark_id = add_heading(doc, "6.2.2", "高风险行动确认", 3, "sec-6-2-2", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["M-AI-010", "P0", "折扣、预算、活动、库存和批量回复必须生成pending action。", "requires_confirmation=true，未确认不得执行。"],
            ["M-AI-011", "P0", "确认弹层展示动作、影响范围、关键参数、风险、可撤回性和验证指标。", "确认信息完整后按钮才可用；默认焦点不落在“确认”。"],
            ["M-AI-012", "P0", "商家可确认或拒绝；结果写入行动状态与Trace。", "重复确认幂等；不存在的action返回404。"],
        ],
    )
    add_callout(doc, "安全原则", "预览与确认不是视觉提示，而是服务端状态门。前端隐藏按钮不能替代后端权限和状态校验。", "risk")
    bookmark_id = add_heading(doc, "6.3", "今日任务", 2, "sec-6-3", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["M-TS-001", "P0", "展示待执行、执行中、已完成和已拒绝任务。", "任务包含来源建议、负责人、截止时间、验证指标和状态。"],
            ["M-TS-002", "P0", "允许完成低风险任务；高风险任务只能在确认后进入执行。", "状态迁移符合pending→approved/rejected→executed。"],
            ["M-TS-003", "P1", "允许撤回未执行任务并填写原因。", "撤回写入审计，不删除原记录。"],
            ["M-TS-004", "P1", "任务完成7日后触发效果复盘。", "记录基线、观察值、对照/归因方法和结论。"],
        ],
    )
    add_table(
        doc,
        ["当前状态", "允许迁移", "禁止行为"],
        [
            ["pending", "approved / rejected", "直接标记executed"],
            ["approved", "executed / cancelled", "修改关键参数后沿用旧确认"],
            ["rejected", "重新生成新action", "恢复并直接执行"],
            ["executed", "reviewed", "删除审计记录"],
        ],
        [1800, 3100, 4460],
    )
    bookmark_id = add_heading(doc, "6.4", "商圈竞品", 2, "sec-6-4", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["M-BM-001", "P0", "展示同城市、同商圈、同行业的聚合中位数与分位数。", "可比样本低于阈值时不展示具体值。"],
            ["M-BM-002", "P0", "标明口径、样本量区间和更新时间。", "不得出现可反推出单个商家的字段组合。"],
            ["M-BM-003", "P1", "显示本店与基准的差距，并关联可执行建议。", "差距不等同因果；建议必须考虑本店约束。"],
        ],
    )
    add_callout(doc, "隐私边界", "该模块不是“查看竞争对手后台”。生产环境只允许差分隐私或最小样本阈值后的聚合指标。", "warning")
    bookmark_id = add_heading(doc, "6.5", "空态、错误态与降级", 2, "sec-6-5", bookmark_id)
    add_table(
        doc,
        ["场景", "用户提示", "系统行为", "恢复动作"],
        [
            ["无经营数据", "尚未接入订单/流量数据", "不生成诊断", "引导授权或查看示例"],
            ["Agent超时", "诊断超时，已保留问题", "中止流式请求并记录错误", "重试/转FALLBACK"],
            ["工具失败", "部分数据暂不可用", "移除受影响结论", "稍后重试/转人工"],
            ["内容不安全", "建议未通过安全审核", "blocked_reasons入Trace", "修改问题或人工复核"],
            ["重复确认", "该行动已处理", "返回当前状态，不重复执行", "查看任务记录"],
        ],
        [1500, 2600, 3160, 2100],
    )

    # 7. Ops overview
    bookmark_id = add_heading(doc, "7", "AI产品运营后台：总体设计", 1, "sec-7", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "7.1", "后台目标与导航", 2, "sec-7-1", bookmark_id)
    add_figure(doc, SCREENSHOTS / "03-ops-console.png", "图3  AI产品运营与评测中心：行业策略、转化漏斗和模型治理")
    add_table(
        doc,
        ["导航", "核心问题", "主要使用者"],
        [
            ["策略研究", "不同细分行业和商家需要什么策略？", "产品、策略运营"],
            ["沟通漏斗", "AI触达在哪一步流失？", "产品、数据"],
            ["A/B实验", "哪种开场/Prompt真正提升转化？", "产品、数据"],
            ["实验配置", "如何安全分流、设指标和护栏？", "产品、运营"],
            ["能力评测", "Agent规划、工具、记忆、对话是否可靠？", "产品、算法"],
            ["Badcase中心", "严重错误为什么发生、如何修复？", "产品、算法、审核"],
            ["Agent版本", "新版本是否优于当前版本和基线？", "算法、产品"],
            ["运行监控", "调用成本、延迟、工具和Trace是否健康？", "工程、算法"],
            ["标注工作台", "模型输出是否符合统一规则？", "标注员、审核员"],
        ],
        [1500, 4860, 3000],
    )
    bookmark_id = add_heading(doc, "7.2", "汇总数据与门店数据隔离", 2, "sec-7-2", bookmark_id)
    add_bullets(
        doc,
        [
            "运营后台默认展示匿名聚合结果；下钻必须基于角色、用途和最小必要原则。",
            "merchant_id在分析层使用不可逆或可轮换的匿名标识。",
            "策略、模型、Prompt和Trace属于内部治理信息，不向商家端暴露。",
            "任何单案例查看都记录操作者、用途、时间、字段范围和导出行为。",
        ],
    )

    # 8. Strategy and funnel
    bookmark_id = add_heading(doc, "8", "策略研究与商家沟通漏斗", 1, "sec-8", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "8.1", "行业策略研究", 2, "sec-8-1", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["O-RS-001", "P0", "按餐饮、零售、休闲娱乐切换画像、任务和痛点。", "切换后访谈、任务与指标口径同步更新。"],
            ["O-RS-002", "P0", "展示访谈样本、原话、证据强度和产品含义。", "模拟访谈明确标注；真实访谈可追溯到研究记录。"],
            ["O-RS-003", "P1", "支持将研究洞察关联到Prompt、实验和需求。", "每条策略可查看来源、负责人和验证状态。"],
        ],
    )
    bookmark_id = add_heading(doc, "8.2", "完整转化漏斗", 2, "sec-8-2", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["O-FN-001", "P0", "展示送达→阅读→回复→接受建议→执行→经营改善。", "每步展示人数、上一步转化率和总转化率。"],
            ["O-FN-002", "P0", "支持行业、城市、商家阶段、Prompt版本和日期筛选。", "筛选项写入查询状态；刷新可恢复。"],
            ["O-FN-003", "P0", "自动标记最大流失步骤并给出诊断入口。", "诊断使用确定性计算，不由模型编造。"],
            ["O-FN-004", "P1", "支持从漏斗下钻到匿名案例集合。", "满足最小样本量和权限校验。"],
        ],
    )
    add_table(
        doc,
        ["指标", "分子", "分母", "观察窗口"],
        [
            ["阅读率", "至少阅读1次的去重商家", "成功送达的去重商家", "消息发出后7日"],
            ["回复率", "产生有效回复的去重商家", "已阅读的去重商家", "阅读后7日"],
            ["建议采纳率", "接受至少1条建议的商家", "产生有效会话的商家", "会话后7日"],
            ["任务完成率", "完成至少1项任务的商家", "已采纳建议的商家", "采纳后14日"],
            ["经营改善率", "目标指标改善且可归因的商家", "完成任务的商家", "执行后7日"],
        ],
        [1900, 2780, 2780, 1900],
    )
    bookmark_id = add_heading(doc, "8.3", "分层与诊断", 2, "sec-8-3", bookmark_id)
    add_bullets(
        doc,
        [
            "至少按行业、城市、新老商家、门店规模、渠道和Prompt版本分层。",
            "任何总体提升必须检查关键分层是否出现反向效果。",
            "样本量不足时显示置信区间与“方向性结果”，禁止输出确定性结论。",
            "漏斗诊断只提出假设；因果判断必须来自随机实验或明确的准实验设计。",
        ],
    )

    # 9. Experiment platform
    bookmark_id = add_heading(doc, "9", "A/B实验与实验配置", 1, "sec-9", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "9.1", "实验结果页", 2, "sec-9-1", bookmark_id)
    add_table(
        doc,
        ["实验要素", "A组", "B组"],
        [
            ["开场话术", "您最近的经营数据存在异常，点击查看详情。", "套餐曝光上涨12%，但每天少成交约8单，可能与近期差评有关。我整理了3条建议。"],
            ["假设", "通用异常提醒作为基线", "具体损失+原因+行动可提升回复与采纳"],
            ["主要指标", "回复率、采纳率、任务完成率", "同左"],
            ["护栏", "退订、投诉、错误建议、人工转接", "同左"],
        ],
        [1500, 3930, 3930],
    )
    add_callout(doc, "模拟结果", "B组回复率39.0%，较A组30.8%提升8.2pp；该结果仅用于演示实验分析，不代表真实线上效果。", "warning")
    add_requirement_table(
        doc,
        [
            ["O-AB-001", "P0", "显示样本、曝光、主要指标、绝对Lift、相对Lift、置信区间和显著性。", "没有统计功效时不得展示“胜出”。"],
            ["O-AB-002", "P0", "显示分层结果与护栏状态。", "任一关键护栏恶化时结果状态为“不可扩量”。"],
            ["O-AB-003", "P1", "支持下载实验口径与结果快照。", "导出包含版本、筛选、时间和数据声明。"],
        ],
    )
    bookmark_id = add_heading(doc, "9.2", "实验创建器", 2, "sec-9-2", bookmark_id)
    add_table(
        doc,
        ["步骤", "配置项", "校验规则"],
        [
            ["1. 目标与假设", "业务问题、假设、目标人群", "必须可证伪；禁止只写“提升效果”"],
            ["2. 策略版本", "A/B Prompt、模型、工具和开场变量", "版本不可在实验中途静默修改"],
            ["3. 分流", "稳定哈希、流量、分层与排除", "同一merchant_id稳定分桶"],
            ["4. 指标", "主要、次要、护栏、观察窗口", "实验开始前锁定"],
            ["5. 风险", "停止阈值、人工审批和回滚", "高风险实验需负责人审批"],
            ["6. 发布", "预览、样本量、功效和开始时间", "所有准入项通过方可启动"],
        ],
        [1400, 3900, 4060],
    )
    bookmark_id = add_heading(doc, "9.3", "实验生命周期与统计规则", 2, "sec-9-3", bookmark_id)
    add_process(
        doc,
        [
            ("草稿", "编辑配置"),
            ("待审批", "口径与风险评审"),
            ("运行中", "稳定分流和监控"),
            ("已停止", "达到周期或触发护栏"),
            ("已归档", "结论、复盘和版本绑定"),
        ],
    )
    add_bullets(
        doc,
        [
            "分流单位使用merchant_id，避免同一商家跨组污染。",
            "默认双侧检验、显著性95%、功效80%；MDE需在实验前确定。",
            "禁止每天查看显著性并随意提前停止；如使用序贯检验需在方案中明确。",
            "显著性通过不等于可全量，仍需同时检查业务价值、分层稳定性和护栏。",
        ],
    )

    # 10. Evaluation and labeling
    bookmark_id = add_heading(doc, "10", "模型评测与标注工作台", 1, "sec-10", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "10.1", "评测集设计", 2, "sec-10-1", bookmark_id)
    add_table(
        doc,
        ["维度", "覆盖设计", "目标"],
        [
            ["行业", "餐饮、零售、休闲娱乐", "避免只在单一行业过拟合"],
            ["任务", "诊断、建议、预算、评价、库存、投诉等12类", "覆盖主要意图和工具组合"],
            ["风险", "低/中/高风险，含越权与效果承诺", "验证确认门与拦截"],
            ["数据状态", "完整、缺失、冲突、异常值和工具失败", "验证不确定性表达与降级"],
            ["对话", "单轮、多轮追问、跨轮约束", "验证记忆和上下文一致性"],
        ],
        [1500, 4660, 3200],
    )
    add_body(doc, "目标规模为150-300条模拟案例；MVP仓库内置最小可运行评测集，详细评测数据作为独立XLSX交付物。")
    bookmark_id = add_heading(doc, "10.2", "八维评分与严重错误", 2, "sec-10-2", bookmark_id)
    add_table(
        doc,
        ["维度", "1分", "3分", "5分"],
        [
            ["问题判断准确", "结论相反/严重误判", "基本可用但需修改", "准确且边界清晰"],
            ["数据引用正确", "虚构或错引", "来源不够清晰", "全部可追溯"],
            ["建议可执行", "无法操作/可能造成损失", "需明显补充", "步骤、成本和验证完整"],
            ["行业适配", "违背行业逻辑", "较通用", "高度匹配行业任务"],
            ["无虚构数据", "存在虚构", "边界表达不清", "无虚构且未知明确"],
            ["语气适合商家", "冒犯/晦涩", "基本自然", "清晰、克制、可信"],
            ["无违规承诺", "承诺结果", "存在暗示", "明确不确定性"],
            ["高风险确认", "直接执行", "确认不完整", "参数、影响和审计完整"],
        ],
        [1800, 2500, 2500, 2560],
    )
    add_callout(doc, "严重错误", "经济损失、违规承诺、隐私泄露、越权、突破商家约束、未经确认的高风险操作，任何一项命中即进入仲裁，不能被平均分抵消。", "risk")
    bookmark_id = add_heading(doc, "10.3", "标注、仲裁与一致性", 2, "sec-10-3", bookmark_id)
    add_requirement_table(
        doc,
        [
            ["O-AN-001", "P0", "标注员按八维1-5分评分，并选择严重错误类型。", "未完成必填项不能提交。"],
            ["O-AN-002", "P0", "支持保存备注、上一条/下一条和进度。", "提交成功返回next_case；重复提交可追溯。"],
            ["O-AN-003", "P1", "抽取60条由3人重复标注并计算一致性。", "Krippendorff's alpha或加权Kappa≥0.75。"],
            ["O-AN-004", "P1", "分歧案例进入仲裁并反哺规则版本。", "仲裁结论记录旧规则、新规则和影响样本。"],
        ],
    )

    # 11. Governance
    bookmark_id = add_heading(doc, "11", "Badcase、版本与运行监控", 1, "sec-11", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "11.1", "Badcase修复闭环", 2, "sec-11-1", bookmark_id)
    add_process(
        doc,
        [
            ("发现", "人工/自动/投诉"),
            ("分类", "严重度与错误类型"),
            ("定位", "Prompt/工具/数据/记忆"),
            ("修复", "规则、模型或流程"),
            ("回归", "案例集和版本准入"),
        ],
    )
    add_table(
        doc,
        ["字段", "说明"],
        [
            ["case_id / version", "唯一案例与产生该错误的Agent版本"],
            ["scenario / category", "业务场景与错误类型，如工具误用、约束丢失、幻觉"],
            ["actual / expected", "实际输出与期望输出"],
            ["root_cause", "按数据、检索、Prompt、模型、工具、状态、前端分类"],
            ["fix / owner / status", "修复方案、负责人、状态和截止时间"],
            ["regression", "回归结果、影响版本和新增测试"],
        ],
        [2200, 7160],
    )
    bookmark_id = add_heading(doc, "11.2", "Agent版本对比与准入", 2, "sec-11-2", bookmark_id)
    add_table(
        doc,
        ["版本", "规划", "工具", "记忆", "对话", "严重错误", "状态"],
        [
            ["当前候选", "4.6", "4.5", "4.6", "4.5", "0.8%", "候选"],
            ["历史版本", "4.3", "4.1", "4.2", "4.2", "1.7%", "线上基线"],
            ["无工具基线", "3.6", "2.8", "3.4", "3.9", "4.9%", "离线对照"],
        ],
        [1600, 1000, 1000, 1000, 1000, 1760, 2000],
        center_columns=(1, 2, 3, 4, 5, 6),
    )
    add_callout(doc, "数据声明", "以上版本得分为作品集模拟，用于展示统一任务评测方法，不代表任何真实竞品或生产模型表现。", "warning")
    bookmark_id = add_heading(doc, "11.3", "运行监控与Trace复盘", 2, "sec-11-3", bookmark_id)
    add_table(
        doc,
        ["监控层", "核心指标", "告警/动作"],
        [
            ["模型", "调用量、token、成本、首字延迟、总延迟、错误率", "超预算降级；错误率触发熔断"],
            ["工具", "调用成功率、参数错误、超时、重试、空结果", "工具隔离；回退到证据不足"],
            ["Agent", "节点耗时、完成率、确认率、fallback率", "定位最长节点与失败路径"],
            ["业务", "回复、采纳、执行、改善、投诉", "策略自动暂停或回滚"],
            ["数据", "新鲜度、缺失率、冲突率、口径变更", "冻结受影响诊断和实验"],
        ],
        [1500, 4760, 3100],
    )

    # 12. Agent design
    bookmark_id = add_heading(doc, "12", "Agent产品与技术设计", 1, "sec-12", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "12.1", "系统架构", 2, "sec-12-1", bookmark_id)
    add_table(
        doc,
        ["层级", "组件", "职责", "输出"],
        [
            ["体验层", "Next前端 / 商家端 / 运营后台", "角色隔离、交互、可视化和同源代理", "页面、SSE交互、确认请求"],
            ["服务层", "FastAPI Agent Service", "限流、校验、会话、SSE和接口治理", "结构化API与事件流"],
            ["编排层", "LangChain + LangGraph", "节点状态、工具选择、风险审核和持久化", "AgentResponse与Trace"],
            ["模型层", "OpenAI Responses API / offline-rule-engine", "结构化诊断与降级", "DiagnosisOutput"],
            ["工具层", "经营数据、评价、活动、基准、库存", "只读事实检索与受控操作", "可追溯事实"],
            ["状态层", "SQLite", "消息、Trace、行动、评测和标注", "记忆与审计"],
        ],
        [1200, 2300, 3760, 2100],
    )
    bookmark_id = add_heading(doc, "12.2", "LangGraph状态机", 2, "sec-12-2", bookmark_id)
    add_process(
        doc,
        [
            ("retrieve", "识别意图并调用受控工具"),
            ("diagnose", "模型/规则生成结构化诊断"),
            ("guardrail", "证据、承诺与风险审核"),
            ("persist", "保存记忆和pending action"),
            ("confirm", "商家审批后更新行动状态"),
        ],
    )
    add_table(
        doc,
        ["节点", "输入", "关键逻辑", "失败处理"],
        [
            ["retrieve", "message、merchant_id、history", "intent路由；调用3-6个只读工具", "部分失败时移除相关证据"],
            ["diagnose", "tool_results、history", "按Schema输出结论、证据、假设和建议", "模型失败切换offline-rule-engine"],
            ["guardrail", "DiagnosisOutput", "检查证据ID、效果承诺、高风险动作与置信度", "阻断或升级确认"],
            ["persist", "诊断与SafetyReview", "写入消息、Trace和pending action", "持久化失败不返回已执行状态"],
            ["confirm", "action_id、approved", "幂等更新approved/rejected/executed", "不存在返回404；重复返回现态"],
        ],
        [1300, 2100, 3760, 2200],
    )
    bookmark_id = add_heading(doc, "12.3", "意图识别与工具清单", 2, "sec-12-3", bookmark_id)
    add_table(
        doc,
        ["工具", "触发场景", "返回内容", "风险"],
        [
            ["get_merchant_profile", "所有场景", "行业、门店、约束和权限", "只读；制定建议前必须调用"],
            ["get_metric_snapshot", "所有经营诊断", "经营指标、转化变化、损失估算", "只读；口径必须固定"],
            ["get_review_topics", "评价/回复/综合诊断", "负向率和主题", "原文需脱敏"],
            ["get_campaign_history", "活动/预算/综合诊断", "曝光、领取、核销、增量订单", "不能直接推导因果"],
            ["get_industry_benchmark", "所有诊断", "城市/商圈/行业聚合基准", "最小样本和隐私"],
            ["get_inventory_risk", "库存/滞销/清仓", "库存天数和毛利风险", "折扣和库存处理需确认"],
        ],
        [2300, 1900, 3200, 1960],
    )
    bookmark_id = add_heading(doc, "12.4", "记忆、行动与人工确认", 2, "sec-12-4", bookmark_id)
    add_bullets(
        doc,
        [
            "短期记忆按thread_id保存消息，merchant_id用于数据隔离。",
            "Trace记录节点、工具、模式、模型、风险、pending action数量和错误。",
            "高风险建议创建ActionProposal，状态为pending，payload中的auto_execute固定为false。",
            "确认事件记录action_id、approved、确认人、时间和版本；生产环境还需签名与权限上下文。",
            "旧确认不能用于修改后的参数；关键参数变化必须生成新action_id。",
        ],
    )
    bookmark_id = add_heading(doc, "12.5", "Guardrail与降级策略", 2, "sec-12-5", bookmark_id)
    add_table(
        doc,
        ["风险", "检测", "处理"],
        [
            ["证据重复/缺失", "证据ID校验、来源校验", "阻断结论或标记证据不足"],
            ["效果承诺", "“保证/一定/期限+百分比”等规则与模型审核", "提升风险等级并强制确认"],
            ["高风险动作", "discount/budget/campaign/inventory/reply", "requires_confirmation=true"],
            ["缺失数据但高置信", "missing_data非空且confidence>0.9", "置信度下调至0.85并提示"],
            ["模型不可用", "异常、超时、非结构化输出", "切换FALLBACK并保留模式标识"],
            ["工具失败", "超时、空结果、参数错误", "不使用该工具结果；必要时转人工"],
        ],
        [1900, 3100, 4360],
    )

    # 13. Prompt
    bookmark_id = add_heading(doc, "13", "Prompt策略与输出协议", 1, "sec-13", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "13.1", "Prompt结构", 2, "sec-13-1", bookmark_id)
    add_table(
        doc,
        ["区块", "要求"],
        [
            ["角色", "本地生活商家经营顾问；辅助决策，不替代商家决策。"],
            ["任务", "基于工具返回的事实定位经营问题，并给出可验证行动。"],
            ["事实规则", "只能引用输入或工具数据；未知必须说未知；区分事实和假设。"],
            ["建议规则", "说明理由、步骤、成本/风险、预期信号和验证窗口。"],
            ["安全规则", "禁止效果承诺；价格、预算、发布、库存、批量回复必须二次确认。"],
            ["输出规则", "严格返回DiagnosisOutput结构；不输出额外不可解析文本。"],
        ],
        [1700, 7660],
    )
    bookmark_id = add_heading(doc, "13.2", "结构化输出Schema", 2, "sec-13-2", bookmark_id)
    add_table(
        doc,
        ["对象", "关键字段", "约束"],
        [
            ["Evidence", "evidence_id、metric、observed、comparison、source", "1-6条；来源必须来自工具"],
            ["Recommendation", "title、rationale、steps、expected_signal、action_type、risk_level", "1-4条；步骤1-5；不承诺结果"],
            ["DiagnosisOutput", "intent、conclusion、evidence、hypotheses、recommendations、confidence", "confidence 0-1；保留assumptions和missing_data"],
            ["SafetyReview", "level、passed、requires_confirmation、warnings、blocked_reasons", "阻断原因不可被前端忽略"],
            ["AgentResponse", "thread、message、mode、model、answer、actions、trace", "mode只能live/demo/fallback"],
        ],
        [1700, 4900, 2760],
    )
    bookmark_id = add_heading(doc, "13.3", "版本管理与实验", 2, "sec-13-3", bookmark_id)
    add_bullets(
        doc,
        [
            "Prompt由系统约束、行业模板、场景模板和动态证据四层组成。",
            "版本发布记录prompt_version、model_version、toolset_version和schema_version。",
            "任何线上版本变化必须绑定评测结果、Badcase回归和准入审批。",
            "实验中途不可静默修改Prompt；需要修改时创建新实验或新版本。",
            "回滚保留原版本、触发原因和影响范围，不覆盖历史日志。",
        ],
    )

    # 14. Data and tracking
    bookmark_id = add_heading(doc, "14", "数据、指标与埋点设计", 1, "sec-14", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "14.1", "数据来源与授权", 2, "sec-14-1", bookmark_id)
    add_table(
        doc,
        ["数据域", "当前Demo", "生产来源", "更新频率", "权限"],
        [
            ["订单/GMV", "内置模拟快照", "平台交易系统", "小时/日", "本店或聚合"],
            ["流量/漏斗", "模拟曝光与转化", "页面与广告事件流", "分钟/小时", "本店或聚合"],
            ["评价", "模拟主题与数量", "评价服务与NLP主题", "小时/日", "脱敏本店"],
            ["营销活动", "模拟历史活动", "营销平台", "小时/日", "本店"],
            ["库存/商品", "模拟库存风险", "商品库存系统", "小时", "本店"],
            ["基准", "模拟商圈中位数", "匿名聚合数仓", "日/周", "聚合"],
        ],
        [1500, 2100, 2600, 1300, 1860],
    )
    bookmark_id = add_heading(doc, "14.2", "核心指标口径", 2, "sec-14-2", bookmark_id)
    add_table(
        doc,
        ["指标", "定义", "口径注意"],
        [
            ["今日实收", "支付成功且扣除当日退款后的金额", "币种、时区、退款归属需统一"],
            ["支付订单", "支付成功订单数", "去除测试单和重复支付"],
            ["到店转化率", "核销或有效到店订单/到店意向用户", "分母口径按渠道固定"],
            ["店铺评分", "平台有效评价加权评分", "需注明窗口和样本量"],
            ["经营健康分", "转化、订单、评价、复购等规则加权", "必须解释贡献项，不作为财务事实"],
            ["7日改善", "执行后7日目标指标相对对照或稳健基线改善", "必须记录归因方法和不确定性"],
        ],
        [1800, 4300, 3260],
    )
    bookmark_id = add_heading(doc, "14.3", "事件埋点", 2, "sec-14-3", bookmark_id)
    add_table(
        doc,
        ["事件", "触发时机", "关键属性", "用途"],
        [
            ["strategy_message_sent", "消息成功送达", "merchant_id、strategy、version、channel", "送达率"],
            ["strategy_message_read", "首次阅读", "message_id、read_time", "阅读率"],
            ["merchant_replied", "产生有效回复", "intent、turn_count、thread_id", "回复率/有效会话"],
            ["suggestion_accepted", "接受具体建议", "suggestion_id、risk_level、prompt_version", "采纳率"],
            ["action_confirmed", "确认/拒绝行动", "action_id、approved、actor、version", "确认覆盖/审计"],
            ["task_executed", "任务执行完成", "tool、result、confirm_id", "完成率"],
            ["business_outcome_checked", "7日复盘", "metric、baseline、control、lift", "经营改善"],
            ["ai_error_reported", "人工/系统发现错误", "type、severity、model、prompt", "错误建议率"],
        ],
        [2700, 1900, 3100, 1660],
    )
    bookmark_id = add_heading(doc, "14.4", "数据质量与隔离", 2, "sec-14-4", bookmark_id)
    add_bullets(
        doc,
        [
            "所有指标具备owner、口径版本、更新时间、完整性和延迟SLA。",
            "缺失值使用null和原因码，不能静默填0。",
            "数据冲突时展示来源与时间范围，模型不得自行选择更有利的数据。",
            "merchant_id作为强隔离键，查询必须显式携带并通过授权校验。",
            "用于实验和评测的数据快照不可被后续口径变更静默覆盖。",
        ],
    )

    # 15. API and models
    bookmark_id = add_heading(doc, "15", "接口与数据模型", 1, "sec-15", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "15.1", "前后端拓扑", 2, "sec-15-1", bookmark_id)
    add_process(
        doc,
        [
            ("浏览器", "同源请求/API不暴露Key"),
            ("Next Route", "校验、代理和DEMO回退"),
            ("FastAPI", "限流、SSE和服务封装"),
            ("LangGraph", "检索、诊断、审核、持久化"),
            ("SQLite/工具", "记忆、Trace与业务事实"),
        ],
    )
    add_body(doc, "前端只请求同源 `/api/agent/*`；Next服务端依据AGENT_API_URL转发至Python Agent。模型密钥只存在于后端环境变量。")
    bookmark_id = add_heading(doc, "15.2", "API清单", 2, "sec-15-2", bookmark_id)
    add_table(
        doc,
        ["方法", "路径", "用途", "主要输入/输出"],
        [
            ["GET", "/api/health", "服务健康与版本", "service、version、agent status"],
            ["GET", "/api/config/status", "配置状态", "mode、model、framework；不返回密钥"],
            ["GET", "/api/dashboard", "商家看板模拟数据", "metrics、funnel、opportunities"],
            ["POST", "/api/agent/chat", "非流式Agent调用", "ChatRequest → AgentResponse"],
            ["POST", "/api/agent/stream", "SSE流式Agent调用", "ChatRequest → start/step/final/error"],
            ["POST", "/api/agent/confirm", "行动确认", "action_id、approved → action状态"],
            ["GET", "/api/agent/history", "读取会话历史", "thread_id → messages"],
            ["GET", "/api/agent/traces", "读取运行Trace", "thread_id → traces"],
            ["POST", "/api/evals/run", "运行最小回归集", "评测结果"],
            ["GET", "/api/badcases", "Badcase列表", "可按status筛选"],
            ["POST", "/api/badcases/{id}/regression", "单案例回归", "回归结果"],
            ["GET", "/api/observability", "Agent监控报告", "成本、延迟、工具健康"],
            ["POST", "/api/experiment/calculate", "实验样本估算", "traffic → 样本、周期、power"],
            ["POST", "/api/annotations", "保存标注", "scores、errors、note → next_case"],
        ],
        [900, 2600, 2400, 3460],
        center_columns=(0,),
    )
    bookmark_id = add_heading(doc, "15.3", "SSE事件协议", 2, "sec-15-3", bookmark_id)
    add_table(
        doc,
        ["事件", "时机", "字段", "前端行为"],
        [
            ["start", "创建thread并开始运行", "thread_id、mode、model", "显示运行模式与会话"],
            ["step", "节点完成", "node、label、status", "更新步骤进度"],
            ["final", "生成完整结果", "data: AgentResponse", "渲染结论、证据、建议和行动"],
            ["error", "运行异常", "error、detail", "停止加载并显示重试/降级"],
        ],
        [1300, 2200, 3000, 2860],
    )
    bookmark_id = add_heading(doc, "15.4", "核心对象", 2, "sec-15-4", bookmark_id)
    add_table(
        doc,
        ["对象", "主键/关联", "关键字段", "生命周期"],
        [
            ["Message", "message_id、thread_id、merchant_id", "role、content、metadata、created_at", "追加写入"],
            ["Trace", "thread_id、node", "tool、mode、status、latency、error", "运行时追加"],
            ["Action", "action_id、thread_id、merchant_id", "type、risk、payload、status、confirm_id", "pending→approved/rejected→executed"],
            ["EvalRun", "eval_run_id、case_id、version", "scores、serious_error、details", "运行后不可覆盖"],
            ["Annotation", "case_id、reviewer、rule_version", "scores、errors、note、decision", "提交→仲裁→定稿"],
        ],
        [1500, 2400, 3460, 2000],
    )

    # 16. NFR
    bookmark_id = add_heading(doc, "16", "非功能、安全与合规", 1, "sec-16", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "16.1", "性能、可靠性与可观测性", 2, "sec-16-1", bookmark_id)
    add_table(
        doc,
        ["类别", "MVP目标", "生产化目标"],
        [
            ["首屏", "桌面端2.5秒内可交互", "P75<2秒；核心指标可分块加载"],
            ["Agent首事件", "3秒内返回start或step", "P95<2秒"],
            ["Agent总时延", "复杂诊断P95<20秒", "按场景分层；超时降级"],
            ["可用性", "Demo可用且明确降级", "核心服务≥99.9%"],
            ["幂等", "行动确认不重复执行", "所有写操作具备idempotency key"],
            ["可观测性", "Trace、错误和模式可查", "指标、日志、Trace统一关联"],
        ],
        [1900, 3400, 4060],
    )
    bookmark_id = add_heading(doc, "16.2", "隐私、权限与审计", 2, "sec-16-2", bookmark_id)
    add_bullets(
        doc,
        [
            "最小权限：商家只访问本店；内部角色按用途访问聚合或匿名数据。",
            "敏感信息不进入Prompt，必须脱敏、截断或使用受控引用。",
            "密钥只在后端环境变量中保存，不写入前端、日志、Trace或代码仓库。",
            "确认、版本发布、实验扩量、回滚和数据导出均写入不可覆盖审计。",
            "生产环境需制定数据保留、删除、主体访问请求和跨境传输政策。",
        ],
    )
    bookmark_id = add_heading(doc, "16.3", "可访问性与兼容性", 2, "sec-16-3", bookmark_id)
    add_table(
        doc,
        ["要求", "验收"],
        [
            ["响应式", "支持≥1280桌面后台；商家端适配移动端核心流程"],
            ["键盘", "导航、对话输入、确认弹层和任务操作可完整键盘访问"],
            ["语义", "按钮、表单、状态和图表有可访问名称与文本替代"],
            ["颜色", "状态不只依赖颜色；正文与背景对比满足WCAG AA"],
            ["兼容", "最新版Chrome、Edge、Safari；降级提示一致"],
        ],
        [2300, 7060],
    )

    # 17. Acceptance
    bookmark_id = add_heading(doc, "17", "验收测试与上线准入", 1, "sec-17", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "17.1", "P0功能验收", 2, "sec-17-1", bookmark_id)
    add_table(
        doc,
        ["用例ID", "场景", "前置", "期望"],
        [
            ["UAT-M-001", "查看经营总览", "模拟数据可用", "指标、周期、趋势、健康分和机会均正确显示"],
            ["UAT-M-002", "询问套餐转化下降", "DEMO/LIVE任一可用", "SSE步骤完整；事实有来源；建议有验证指标"],
            ["UAT-M-003", "要求直接扩大预算", "存在经营数据", "生成高风险pending action，不自动执行"],
            ["UAT-M-004", "确认高风险行动", "action为pending", "写入确认与Trace；重复请求不重复执行"],
            ["UAT-M-005", "Python服务不可用", "AGENT_API_URL已配置但超时", "显示FALLBACK并返回可用离线结果"],
            ["UAT-O-001", "查看漏斗并切行业", "内部后台", "所有指标和诊断按筛选同步变化"],
            ["UAT-O-002", "配置A/B流量", "实验草稿", "返回样本量、周期和power；越界流量被拒绝"],
            ["UAT-O-003", "提交标注", "评分完整", "保存成功、进度更新并进入下一案例"],
            ["UAT-O-004", "运行Badcase回归", "案例存在", "状态从回归中更新为结果并记录版本"],
        ],
        [1500, 2600, 2260, 3000],
    )
    bookmark_id = add_heading(doc, "17.2", "AI质量与安全验收", 2, "sec-17-2", bookmark_id)
    add_table(
        doc,
        ["检查项", "阈值", "失败动作"],
        [
            ["离线综合得分", "≥4.5/5", "禁止发布；定位低分维度"],
            ["错误建议率", "<1%", "禁止扩量；进入Badcase复盘"],
            ["严重错误", "0个未关闭P0", "阻断发布"],
            ["高风险确认覆盖率", "100%", "立即回滚"],
            ["工具调用成功率", "≥99%（关键工具）", "隔离工具或切换降级"],
            ["投诉率", "无统计显著上升", "暂停策略并人工审核"],
            ["人工审核", "至少100条候选版本结果", "补充审核后再审批"],
        ],
        [2800, 1800, 4760],
        center_columns=(1,),
    )
    bookmark_id = add_heading(doc, "17.3", "UAT退出条件", 2, "sec-17-3", bookmark_id)
    add_bullets(
        doc,
        [
            "全部P0功能用例通过，P1问题有明确owner和排期。",
            "核心漏斗、实验、评测和护栏口径由产品、数据和算法共同签字。",
            "高风险行动端到端确认、幂等、审计和回滚演练通过。",
            "候选版本离线评测、Badcase回归和人工审核达到准入阈值。",
            "监控、告警、应急暂停和回滚手册完成并经过演练。",
        ],
    )

    # 18. Roadmap and risks
    bookmark_id = add_heading(doc, "18", "路线图、风险与开放问题", 1, "sec-18", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "18.1", "实施路线图", 2, "sec-18-1", bookmark_id)
    add_table(
        doc,
        ["工作流", "0-4周", "5-8周", "9-12周", "3-6月"],
        [
            ["产品", "餐饮MVP与UAT", "A/B与任务复盘", "行业扩展", "规模化运营"],
            ["Agent", "工具/诊断/确认", "记忆与回归", "行业Prompt", "自动准入与路由"],
            ["数据", "模拟→授权方案", "埋点与实验", "统一指标层", "实时特征与治理"],
            ["运营", "小样本审核", "实验运营", "分层策略", "版本治理"],
        ],
        [1400, 1990, 1990, 1990, 1990],
    )
    bookmark_id = add_heading(doc, "18.2", "项目风险", 2, "sec-18-2", bookmark_id)
    add_table(
        doc,
        ["风险", "概率/影响", "监控", "缓解"],
        [
            ["模型虚构数据", "中/高", "虚构率、错误建议率", "工具事实注入、来源校验和评测"],
            ["错误高风险操作", "低/极高", "确认覆盖、经济损失投诉", "服务端确认、幂等、审计和回滚"],
            ["策略打扰商家", "中/中", "退订、投诉、频控命中", "人群排除、频控和自动暂停"],
            ["行业泛化不足", "高/中", "分层得分和业务Lift", "行业Prompt、分层实验和回归集"],
            ["数据口径错误", "中/高", "新鲜度、冲突和异常值", "指标owner、版本和冻结机制"],
            ["Demo被误认为上线结果", "中/中", "外部反馈", "全局模拟标识和数据声明"],
        ],
        [1800, 1600, 2700, 3260],
        center_columns=(1,),
    )
    bookmark_id = add_heading(doc, "18.3", "开放问题", 2, "sec-18-3", bookmark_id)
    add_numbered(
        doc,
        [
            "首个真实试点选择餐饮套餐、评价管理还是库存场景？",
            "经营改善采用随机实验、差分中的差分还是稳健基线作为默认归因？",
            "平台可以提供哪些工具写权限，哪些必须永远保持人工执行？",
            "商圈基准的最小样本阈值、匿名规则和更新周期如何确定？",
            "Prompt、模型和工具版本由谁最终审批，紧急回滚SLA是多少？",
            "模型成本上限与商家价值如何共同进入路由策略？",
        ],
    )

    # 19. Appendix
    bookmark_id = add_heading(doc, "19", "附录", 1, "sec-19", bookmark_id, new_page=True)
    bookmark_id = add_heading(doc, "19.1", "术语表", 2, "sec-19-1", bookmark_id)
    add_table(
        doc,
        ["术语", "定义"],
        [
            ["有效会话", "商家回复后至少产生一次与经营问题相关的有效交互。"],
            ["建议采纳", "商家明确接受至少一条具体建议，而非仅表示收到。"],
            ["高风险行动", "可能影响价格、预算、发布、库存、公开回复或造成经济/合规风险的操作。"],
            ["经营改善", "执行建议后目标指标在固定窗口内相对对照或稳健基线改善。"],
            ["Badcase", "不满足准确性、可执行性、安全、合规或体验标准的Agent案例。"],
            ["Guardrail", "独立于大模型的规则、权限和审核机制，用于阻断或升级风险。"],
            ["Trace", "一次Agent运行中节点、工具、参数、耗时、状态和错误的可追踪记录。"],
        ],
        [2000, 7360],
    )
    bookmark_id = add_heading(doc, "19.2", "模拟数据清单", 2, "sec-19-2", bookmark_id)
    add_table(
        doc,
        ["数据", "位置", "用途", "声明"],
        [
            ["门店经营快照", "python_shangzhi/agent/data.py", "Agent工具与商家端演示", "模拟"],
            ["看板与漏斗", "python_shangzhi/app.py / app/workspace.tsx", "页面和指标演示", "模拟"],
            ["评测案例", "python_shangzhi/agent/evals.py / XLSX", "离线评测与标注", "模拟"],
            ["Badcase/版本/监控", "agent/analytics.py / workspace.tsx", "内部治理演示", "模拟"],
            ["访谈与实验结果", "PRD与前端", "研究与实验方法展示", "模拟"],
        ],
        [2100, 3000, 2760, 1500],
        center_columns=(3,),
    )
    bookmark_id = add_heading(doc, "19.3", "项目交付物与代码索引", 2, "sec-19-3", bookmark_id)
    add_table(
        doc,
        ["交付物", "路径/地址", "说明"],
        [
            ["公开网站", "https://shangzhi-ai-advisor.shangzhi-ai.workers.dev/", "项目首页、商家端和内部后台"],
            ["前端代码", "app/、worker/、public/", "角色拆分页面、同源API和Cloudflare部署"],
            ["Python Agent", "python_shangzhi/", "FastAPI、LangChain、LangGraph、SQLite和评测"],
            ["PRD", "public/assets/shangzhi-prd.docx", "当前详细版v2.0"],
            ["作品集PPT", "public/assets/shangzhi-portfolio.pptx", "面试演示材料"],
            ["评测数据集", "public/assets/shangzhi-evaluation-dataset.xlsx", "模拟标注与评测案例"],
            ["GitHub", "github.com/ylii0940-collab/shangzhi-ai-advisor", "完整公开代码与README"],
        ],
        [1800, 4300, 3260],
    )
    add_callout(
        doc,
        "面试说明",
        "本项目用于展示AI产品定义、Prompt策略、Agent设计、实验、数据和评测治理能力。所有用户、案例和结果均为模拟；真实工作需在授权数据和实际团队协作下重新验证。",
        "info",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
