from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Avaliacao, AvaliacaoSintoma, Paciente, Profissional, Sintoma
from app.services.reports import build_reports
from app.shared.formatters import assessment_view


PAGE_SIZE = landscape(A4)
PRIMARY = colors.HexColor("#111827")
BORDER = colors.HexColor("#111827")
GRID = colors.HexColor("#D1D5DB")
MUTED = colors.HexColor("#374151")
ASSESSMENT_COLUMN_WIDTHS = [
    2.35 * cm,
    3.15 * cm,
    1.75 * cm,
    1.25 * cm,
    1.25 * cm,
    2.35 * cm,
    3.05 * cm,
    1.9 * cm,
    8.55 * cm,
]


def reports_pdf(db, profissional_id, include_all=False):
    reports = build_reports(db, profissional_id, include_all=include_all)
    assessments = _assessment_rows(db, profissional_id, include_all)
    symptoms = _symptom_rows(db, profissional_id, include_all)

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=PAGE_SIZE,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.1 * cm,
        bottomMargin=1.1 * cm,
        title="Relatório Sistema-X",
    )
    styles = _styles()
    story = [
        Paragraph("Relatório Sistema-X", styles["ReportTitle"]),
        Paragraph("Indicadores, gráficos e tabelas da triagem SXF", styles["ReportSubtitle"]),
        Spacer(1, .35 * cm),
        _indicators_table(reports["indicators"], styles),
        Spacer(1, .35 * cm),
        _analyses_table(reports["analyses"], styles),
        Spacer(1, .45 * cm),
        _charts_section(reports, assessments, symptoms, styles),
        PageBreak(),
        Paragraph("Tabelas completas", styles["ReportSection"]),
        Spacer(1, .25 * cm),
        _table_block("Indicadores por sexo", _by_sex_data(reports), styles),
        Spacer(1, .35 * cm),
        _table_block("Indicadores por faixa etária", _by_age_data(reports), styles),
        Spacer(1, .35 * cm),
        _table_block("Sintomas marcados", _symptoms_data(symptoms), styles),
        PageBreak(),
        Paragraph("Avaliações registradas", styles["ReportSection"]),
        Spacer(1, .25 * cm),
        _table_block(
            "Lista completa de avaliações",
            _assessments_data(assessments),
            styles,
            repeat_header=True,
            col_widths=ASSESSMENT_COLUMN_WIDTHS,
        ),
    ]

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    output.seek(0)
    return output


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="ReportSection",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="ReportSmall",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="ReportSmallCenter",
        parent=styles["ReportSmall"],
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="ReportTableHeader",
        fontName="Helvetica-Bold",
        fontSize=5.8,
        leading=7,
        textColor=PRIMARY,
        wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        name="ReportTableCell",
        fontName="Helvetica",
        fontSize=5.8,
        leading=7,
        textColor=PRIMARY,
        wordWrap="CJK",
    ))
    return styles


def _indicators_table(indicators, styles):
    items = [
        ("Avaliações", indicators["totalAssessments"]),
        ("Taxa de encaminhamento", f"{indicators['referralRate']}%"),
        ("Score médio", indicators["averageScore"]),
        ("Sintoma mais frequente", indicators["mostFrequentSymptom"]),
        ("Idade média", indicators["averageAge"]),
        ("Resultados positivos", indicators["positiveResults"]),
    ]
    cells = []
    for label, value in items:
        cells.append([
            Paragraph(str(label), styles["ReportSmall"]),
            Paragraph(f"<b>{value}</b>", styles["ReportSmall"]),
        ])

    table = Table([cells[:3], cells[3:]], colWidths=[8 * cm, 8 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), .8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), .5, GRID),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _analyses_table(analyses, styles):
    rows = [[
        Paragraph("<b>Análise</b>", styles["ReportSmall"]),
        Paragraph("<b>Valor</b>", styles["ReportSmall"]),
        Paragraph("<b>Descrição</b>", styles["ReportSmall"]),
    ]]
    for item in analyses:
        rows.append([
            Paragraph(item["title"], styles["ReportSmall"]),
            Paragraph(str(item["value"]), styles["ReportSmall"]),
            Paragraph(item["description"], styles["ReportSmall"]),
        ])
    return _styled_table(rows, [6 * cm, 4 * cm, 14 * cm], styles, repeat_rows=1)


def _charts_section(reports, assessments, symptoms, styles):
    charts = [
        _pie_chart("Recomendações", _counts(assessments, "recommendation")),
        _bar_chart("Avaliações por mês", _counts(assessments, "monthLabel")),
        _bar_chart("Sintomas frequentes", _counts(symptoms, "symptom")),
        _line_chart("Score médio por mês", _monthly_scores(assessments)),
    ]
    return KeepTogether([
        Paragraph("Gráficos", styles["ReportSection"]),
        Spacer(1, .25 * cm),
        Table(
            [[charts[0], charts[1]], [charts[2], charts[3]]],
            colWidths=[12 * cm, 12 * cm],
            rowHeights=[6.2 * cm, 6.2 * cm],
            style=[
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), .8, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), .5, GRID),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ],
        ),
    ])


def _pie_chart(title, counts):
    drawing = Drawing(330, 165)
    drawing.add(String(8, 150, title, fontName="Helvetica-Bold", fontSize=9, fillColor=PRIMARY))
    if not counts:
        drawing.add(String(100, 80, "Sem dados", fontSize=9, fillColor=PRIMARY))
        return drawing
    pie = Pie()
    pie.x = 18
    pie.y = 25
    pie.width = 105
    pie.height = 105
    pie.data = list(counts.values())
    pie.labels = list(counts.keys())
    pie.slices.strokeColor = colors.white
    pie.slices[0].fillColor = colors.HexColor("#2563EB")
    if len(counts) > 1:
        pie.slices[1].fillColor = colors.HexColor("#16A34A")
    if len(counts) > 2:
        pie.slices[2].fillColor = colors.HexColor("#D97706")
    drawing.add(pie)
    _legend(drawing, counts, 155, 112)
    return drawing


def _bar_chart(title, counts):
    drawing = Drawing(330, 165)
    drawing.add(String(8, 150, title, fontName="Helvetica-Bold", fontSize=9, fillColor=PRIMARY))
    if not counts:
        drawing.add(String(100, 80, "Sem dados", fontSize=9, fillColor=PRIMARY))
        return drawing
    labels = list(counts.keys())[:8]
    values = [counts[label] for label in labels]
    chart = VerticalBarChart()
    chart.x = 28
    chart.y = 35
    chart.height = 90
    chart.width = 265
    chart.data = [values]
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(values) + 1
    chart.valueAxis.valueStep = max(1, round((max(values) + 1) / 4))
    chart.categoryAxis.categoryNames = [_short(label, 12) for label in labels]
    chart.categoryAxis.labels.fontSize = 6
    chart.valueAxis.labels.fontSize = 6
    chart.bars[0].fillColor = colors.HexColor("#2563EB")
    drawing.add(chart)
    return drawing


def _line_chart(title, points):
    drawing = Drawing(330, 165)
    drawing.add(String(8, 150, title, fontName="Helvetica-Bold", fontSize=9, fillColor=PRIMARY))
    if not points:
        drawing.add(String(100, 80, "Sem dados", fontSize=9, fillColor=PRIMARY))
        return drawing
    values = [(index, value) for index, (_, value) in enumerate(points)]
    line = LinePlot()
    line.x = 35
    line.y = 35
    line.height = 90
    line.width = 250
    line.data = [values]
    line.lines[0].strokeColor = colors.HexColor("#2563EB")
    line.lines[0].strokeWidth = 2
    line.xValueAxis.valueMin = 0
    line.xValueAxis.valueMax = max(1, len(values) - 1)
    line.yValueAxis.valueMin = 0
    line.yValueAxis.valueMax = max(value for _, value in values) + .2
    line.xValueAxis.labels.fontSize = 6
    line.yValueAxis.labels.fontSize = 6
    drawing.add(line)
    for index, (label, _) in enumerate(points[:6]):
        drawing.add(String(30 + index * 42, 15, label, fontSize=5.5, fillColor=PRIMARY))
    return drawing


def _table_block(title, data, styles, repeat_header=True, col_widths=None):
    return KeepTogether([
        Paragraph(title, styles["ReportSection"]),
        Spacer(1, .15 * cm),
        _styled_table(
            data,
            col_widths or _column_widths(len(data[0]) if data else 1),
            styles,
            repeat_rows=1 if repeat_header else 0,
        ),
    ])


def _styled_table(rows, col_widths, styles, repeat_rows=0):
    if not rows:
        rows = [["Sem dados"]]
    rows = _paragraph_rows(rows, styles)
    table = Table(rows, colWidths=col_widths, repeatRows=repeat_rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, -1), PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("BOX", (0, 0), (-1, -1), .8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), .35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def _paragraph_rows(rows, styles):
    prepared = []
    for row_index, row in enumerate(rows):
        style = styles["ReportTableHeader"] if row_index == 0 else styles["ReportTableCell"]
        prepared.append([_cell(value, style) for value in row])
    return prepared


def _cell(value, style):
    if isinstance(value, Paragraph):
        return value
    text = escape("" if value is None else str(value)).replace("\n", "<br/>")
    return Paragraph(text, style)


def _assessment_rows(db, profissional_id, include_all):
    query = db.query(Avaliacao)
    if not include_all:
        query = query.filter(Avaliacao.profissional_id == profissional_id)
    return query.order_by(Avaliacao.realizado_em.desc()).all()


def _symptom_rows(db, profissional_id, include_all):
    query = (
        db.query(Sintoma.descricao, Sintoma.categoria, Avaliacao.paciente_id)
        .join(AvaliacaoSintoma, AvaliacaoSintoma.sintoma_id == Sintoma.id)
        .join(Avaliacao, Avaliacao.id == AvaliacaoSintoma.avaliacao_id)
        .filter(AvaliacaoSintoma.presente.is_(True))
    )
    if not include_all:
        query = query.filter(Avaliacao.profissional_id == profissional_id)
    return query.order_by(Sintoma.categoria, Sintoma.descricao).all()


def _by_sex_data(reports):
    rows = [["Sexo", "Total", "Encaminhamentos", "Taxa", "Score médio", "Idade média"]]
    rows.extend([
        [row["sex"], row["total"], row["referrals"], f"{row['referralRate']}%", row["averageScore"], row["averageAge"]]
        for row in reports["tables"]["bySex"]
    ])
    return rows


def _by_age_data(reports):
    rows = [["Faixa", "Total", "Encaminhamentos", "Taxa", "Score médio", "Positivos"]]
    rows.extend([
        [row["ageGroup"], row["total"], row["referrals"], f"{row['referralRate']}%", row["averageScore"], row["positiveResults"]]
        for row in reports["tables"]["byAgeGroup"]
    ])
    return rows


def _symptoms_data(symptoms):
    rows = [["Sintoma", "Categoria", "Paciente ID"]]
    rows.extend([[row.descricao, row.categoria, row.paciente_id] for row in symptoms])
    return rows


def _assessments_data(assessments):
    rows = [["Data", "Paciente", "Sexo", "Score", "Limiar", "Recomendação", "Etapa", "Resultado", "Observação"]]
    for avaliacao in assessments:
        view = assessment_view(avaliacao)
        rows.append([
            view["date"],
            avaliacao.paciente.nome,
            view["sex"],
            view["score"],
            view["threshold"],
            view["recommendation"],
            view["journey_stage"],
            view["exam_result"],
            avaliacao.observacao or "",
        ])
    return rows


def _counts(rows, attr):
    counts = {}
    for row in rows:
        value = getattr(row, attr, None)
        if attr == "recommendation":
            value = "Encaminhar" if row.encaminhar else "Não prioritário"
        elif attr == "monthLabel":
            value = row.realizado_em.strftime("%m/%Y")
        elif attr == "symptom":
            value = row.descricao
        if value is None:
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def _monthly_scores(assessments):
    values = {}
    for avaliacao in assessments:
        key = avaliacao.realizado_em.strftime("%m/%Y")
        values.setdefault(key, []).append(float(avaliacao.score_calculado))
    return [(key, round(sum(items) / len(items), 2)) for key, items in values.items()]


def _legend(drawing, counts, x, y):
    palette = [colors.HexColor("#2563EB"), colors.HexColor("#16A34A"), colors.HexColor("#D97706"), colors.HexColor("#DC2626")]
    for index, (label, value) in enumerate(list(counts.items())[:6]):
        yy = y - index * 16
        drawing.add(String(x, yy, f"{_short(label, 22)}: {value}", fontSize=7, fillColor=PRIMARY))
        drawing.add(String(x - 12, yy, "■", fontSize=7, fillColor=palette[index % len(palette)]))


def _column_widths(count):
    available = 25.6 * cm
    return [available / count] * count


def _short(value, length):
    text = str(value)
    return text if len(text) <= length else f"{text[:length - 1]}..."


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_SIZE[0] - 1.2 * cm, .55 * cm, f"Página {doc.page}")
    canvas.drawString(1.2 * cm, .55 * cm, "Sistema-X")
    canvas.restoreState()
