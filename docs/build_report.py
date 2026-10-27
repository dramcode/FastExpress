"""Build the FastExpress software-quality report."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as PdfImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"
PDF_PATH = ROOT / "docs" / "Informe_Calidad_FastExpress.pdf"
CFG_PATH = EVIDENCE / "08-cfg.png"

INK = HexColor("#1a1814")
MUTED = HexColor("#5c564c")
PAPER = HexColor("#f7f4ee")
LINE = HexColor("#d9d2c5")
ACCENT = HexColor("#8c4a12")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(path, size)


def draw_cfg() -> None:
    image = Image.new("RGB", (1400, 1680), "white")
    draw = ImageDraw.Draw(image)
    label = font(18, bold=True)
    small = font(16)

    def center_text(box, text, face):
        lines = text.split("\n")
        heights = [face.getbbox(line)[3] for line in lines]
        total = sum(heights) + 4 * (len(lines) - 1)
        y = box[1] + (box[3] - box[1] - total) / 2
        for line, height in zip(lines, heights):
            width = face.getbbox(line)[2]
            draw.text((box[0] + (box[2] - box[0] - width) / 2, y), line, fill="#1a1814", font=face)
            y += height + 4

    def rounded(box, fill, text, face=label):
        draw.rounded_rectangle(box, radius=14, fill=fill, outline="#1a1814", width=3)
        center_text(box, text, face)

    def diamond(box, text):
        x1, y1, x2, y2 = box
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        draw.polygon(points, fill="#fff4c2", outline="#1a1814")
        draw.line(points + [points[0]], fill="#1a1814", width=3)
        center_text((x1 + 36, y1 + 28, x2 - 36, y2 - 28), text, small)

    def arrow(start, end, text=""):
        draw.line([start, end], fill="#1a1814", width=3)
        ex, ey = end
        sx, sy = start
        if ey >= sy:
            head = [(ex, ey), (ex - 7, ey - 12), (ex + 7, ey - 12)]
        else:
            head = [(ex, ey), (ex - 7, ey + 12), (ex + 7, ey + 12)]
        if abs(ex - sx) > abs(ey - sy):
            if ex >= sx:
                head = [(ex, ey), (ex - 12, ey - 7), (ex - 12, ey + 7)]
            else:
                head = [(ex, ey), (ex + 12, ey - 7), (ex + 12, ey + 7)]
        draw.polygon(head, fill="#1a1814")
        if text:
            draw.text(((sx + ex) / 2 + 6, (sy + ey) / 2 - 18), text, fill="#8c4a12", font=small)

    start = (560, 30, 840, 100)
    d1 = (500, 150, 900, 250)
    r1 = (80, 150, 360, 250)
    d2 = (500, 310, 900, 410)
    r2 = (80, 310, 360, 410)
    d3 = (500, 470, 900, 570)
    rate2 = (250, 630, 560, 710)
    rate4 = (840, 630, 1150, 710)
    subtotal = (500, 770, 900, 850)
    d4 = (500, 910, 900, 1010)
    zero = (80, 910, 360, 1010)
    d5 = (500, 1070, 900, 1170)
    ten = (80, 1070, 360, 1170)
    twenty = (1040, 1070, 1320, 1170)
    d6 = (500, 1230, 900, 1330)
    express = (80, 1230, 360, 1330)
    standard = (1040, 1230, 1320, 1330)
    total = (500, 1390, 900, 1470)
    end = (560, 1540, 840, 1610)

    rounded(start, "#e7f6d9", "1  Inicio")
    diamond(d1, "2  ¿peso < 0.01?")
    rounded(r1, "#f8d5cc", "3  Rechazo\npor debajo del mínimo")
    diamond(d2, "4  ¿peso > 20.00?")
    rounded(r2, "#f8d5cc", "5  Rechazo\nlímite excedido")
    diamond(d3, "6  ¿peso <= 5.00?")
    rounded(rate2, "#f4efe4", "7  tarifa = 2.00")
    rounded(rate4, "#f4efe4", "8  tarifa = 4.00")
    rounded(subtotal, "#f4efe4", "9  subtotal = 5.00 + peso x tarifa")
    diamond(d4, "10  ¿cliente = NUEVO?")
    rounded(zero, "#f4efe4", "11  descuento = 0%")
    diamond(d5, "12  ¿cliente = FRECUENTE?")
    rounded(ten, "#f4efe4", "13  descuento = 10%")
    rounded(twenty, "#f4efe4", "14  descuento = 20%")
    diamond(d6, "15  ¿envío = EXPRESS?")
    rounded(express, "#f4efe4", "16  recargo = 25%")
    rounded(standard, "#f4efe4", "17  recargo = 0%")
    rounded(total, "#e7f6d9", "18  total = (subtotal + recargo) - descuento")
    rounded(end, "#e7f6d9", "19  Fin")

    arrow((700, 100), (700, 150))
    arrow((500, 200), (360, 200), "sí")
    arrow((700, 250), (700, 310), "no")
    draw.line([(40, 200), (80, 200)], fill="#1a1814", width=3)
    draw.line([(40, 360), (80, 360)], fill="#1a1814", width=3)
    draw.line([(40, 200), (40, 1575)], fill="#1a1814", width=3)
    arrow((40, 1575), (560, 1575))
    arrow((500, 360), (360, 360), "sí")
    arrow((700, 410), (700, 470), "no")
    arrow((500, 520), (405, 630), "sí")
    arrow((900, 520), (995, 630), "no")
    arrow((405, 710), (620, 770))
    arrow((995, 710), (780, 770))
    arrow((700, 850), (700, 910))
    arrow((500, 960), (360, 960), "sí")
    arrow((700, 1010), (700, 1070), "no")
    arrow((500, 1120), (360, 1120), "sí")
    arrow((900, 1120), (1040, 1120), "no")
    draw.line([(360, 960), (430, 960)], fill="#1a1814", width=3)
    draw.line([(360, 1120), (430, 1120)], fill="#1a1814", width=3)
    draw.line([(430, 960), (430, 1280)], fill="#1a1814", width=3)
    arrow((430, 1280), (500, 1280))
    arrow((1180, 1170), (700, 1200))
    arrow((700, 1170), (700, 1230))
    arrow((500, 1280), (360, 1280), "sí")
    arrow((900, 1280), (1040, 1280), "no")
    arrow((220, 1330), (560, 1430))
    arrow((1180, 1330), (840, 1430))
    arrow((700, 1470), (700, 1540))
    image.save(CFG_PATH)


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial", boldItalic="Arial-Bold")


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name="CoverKicker", fontName="Arial", fontSize=11, textColor=ACCENT, spaceAfter=8))
    base.add(ParagraphStyle(name="CoverTitle", fontName="Arial-Bold", fontSize=26, leading=32, textColor=INK, spaceAfter=8))
    base.add(ParagraphStyle(name="CoverSub", fontName="Arial", fontSize=13, leading=18, textColor=MUTED, spaceAfter=6))
    base.add(ParagraphStyle(name="H1", fontName="Arial-Bold", fontSize=16, leading=20, textColor=INK, spaceBefore=12, spaceAfter=8))
    base.add(ParagraphStyle(name="H2", fontName="Arial-Bold", fontSize=13, leading=16, textColor=INK, spaceBefore=10, spaceAfter=6))
    base.add(ParagraphStyle(name="Body", fontName="Arial", fontSize=10.5, leading=15, textColor=INK, alignment=TA_LEFT, spaceAfter=8))
    base.add(ParagraphStyle(name="Caption", fontName="Arial", fontSize=9, leading=12, textColor=MUTED, spaceBefore=2, spaceAfter=10))
    base.add(ParagraphStyle(name="Cell", fontName="Arial", fontSize=8, leading=11, textColor=INK))
    base.add(ParagraphStyle(name="CellHead", fontName="Arial-Bold", fontSize=8, leading=11, textColor=INK))
    return base


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Arial", 8)
    canvas.drawString(18 * mm, A4[1] - 7.5 * mm, "FastExpress  ·  Informe de calidad de software")
    canvas.setFillColor(MUTED)
    canvas.setFont("Arial", 8)
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


def table(data, widths):
    style = styles()
    formatted = []
    for row_index, row in enumerate(data):
        face = style["CellHead"] if row_index == 0 else style["Cell"]
        formatted.append([Paragraph(str(cell), face) for cell in row])
    result = Table(formatted, colWidths=widths, repeatRows=1)
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#efe8da")),
                ("BACKGROUND", (0, 1), (-1, -1), white),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return result


def shot(name: str, caption: str, story, style):
    path = EVIDENCE / name
    image = PdfImage(str(path), width=174 * mm, height=174 * mm * 900 / 1440)
    story.append(image)
    story.append(Paragraph(caption, style["Caption"]))


def build() -> None:
    register_fonts()
    draw_cfg()
    style = styles()
    story = []
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("PROYECTO INTEGRADOR", style["CoverKicker"]))
    story.append(Paragraph("Módulo de cotización FastExpress", style["CoverTitle"]))
    story.append(Paragraph("Calidad de software: caja negra, caja blanca y cobertura.", style["CoverSub"]))
    story.append(Paragraph("Asignatura: Calidad de Software. El módulo cotiza un envío en USD y rechaza los pesos fuera de regla.", style["Body"]))
    story.append(Paragraph("Resultado de la ejecución", style["H1"]))
    story.append(
        Paragraph(
            "La suite automatizada terminó con 39 pruebas aprobadas. La cobertura medida con coverage.py es 100% de sentencias (236/236) y 100% de ramas (58/58). El mínimo del enunciado es 85% en líneas y ramas. Radon calcula complejidad ciclomática 7 para la función de tarifa, igual que el conteo manual del grafo.",
            style["Body"],
        )
    )

    story.append(Paragraph("1. Roles", style["H1"]))
    story.append(
        Paragraph(
            "El enunciado pide tres roles. Esta entrega cubre el trabajo de los tres. Los nombres del equipo se completan en la sustentación; no se inventan aquí.",
            style["Body"],
        )
    )
    story.append(
        table(
            [
                ["Rol", "Responsabilidad cubierta en esta entrega"],
                ["Backend", "Reglas BR-01 a BR-04, API REST, validaciones y errores."],
                ["Frontend", "Muelle de despacho, validación básica de peso y consumo de la API."],
                ["QA", "Matriz de caja negra, CFG, caminos, pruebas automatizadas, cobertura y este informe."],
            ],
            [35 * mm, 139 * mm],
        )
    )

    story.append(Paragraph("2. Reglas y fórmula", style["H1"]))
    story.append(Paragraph("El enunciado fija estas reglas:", style["Body"]))
    story.append(
        table(
            [
                ["Regla", "Texto del enunciado"],
                ["BR-01", "Toda orden tiene un costo base de $5.00 USD."],
                ["BR-02", "0.01 kg a 5.00 kg: $2.00 por kg. 5.01 kg a 20.00 kg: $4.00 por kg. Mayor a 20.00 kg: rechazar (límite excedido)."],
                ["BR-03", "NUEVO 0%. FRECUENTE 10%. VIP 20%."],
                ["BR-04", "ESTANDAR 0%. EXPRESS +25% sobre la tarifa subtotal."],
            ],
            [25 * mm, 149 * mm],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "El enunciado no dice si la banda es marginal ni en qué orden se aplican recargo y descuento. La implementación usa la banda completa sobre todo el peso. El subtotal es 5.00 más el peso por la tarifa de la banda. El recargo express es el 25% de ese subtotal. El descuento del cliente se aplica después, sobre el importe ya recargado. Cada importe se redondea al centavo con half-up. El campo Monto del plan de pruebas es el total calculado: el enunciado no define un monto de entrada.",
            style["Body"],
        )
    )

    story.append(Paragraph("3. Caja negra", style["H1"]))
    story.append(Paragraph("Particiones de equivalencia del peso", style["H2"]))
    story.append(
        table(
            [
                ["ID", "Partición", "Clase", "Representante", "Resultado observado"],
                ["EP-P1", "peso &lt; 0.01", "Inválida", "-5.00", "422 WEIGHT_BELOW_MINIMUM"],
                ["EP-P2", "0.01 a 5.00", "Válida, tarifa 2.00", "2.50", "200, monto 10.00"],
                ["EP-P3", "5.01 a 20.00", "Válida, tarifa 4.00", "10.00", "200, monto 45.00"],
                ["EP-P4", "peso &gt; 20.00", "Inválida, límite", "25.00", "422 WEIGHT_LIMIT_EXCEEDED"],
                ["EP-P5", "no numérico", "Inválida", "abc", "422 INVALID_WEIGHT"],
                ["EP-P6", "más de 2 decimales", "Inválida", "1.234", "422 INVALID_WEIGHT_PRECISION"],
            ],
            [18 * mm, 38 * mm, 38 * mm, 28 * mm, 52 * mm],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Los casos EP-P2 y EP-P3 usan cliente NUEVO y envío ESTANDAR, para aislar el peso.", style["Caption"]))

    story.append(Paragraph("Particiones de equivalencia del monto", style["H2"]))
    story.append(
        Paragraph(
            "Monto no entra en la solicitud. Si se envía un campo monto, la API responde 422 VALIDATION_ERROR y no calcula. Las particiones de abajo clasifican el monto de salida con NUEVO y ESTANDAR.",
            style["Body"],
        )
    )
    story.append(
        table(
            [
                ["ID", "Partición del monto", "Clase", "Cómo se produce"],
                ["EP-M1", "No hay monto", "Inválida", "Peso rechazado por EP-P1, EP-P4, EP-P5 o EP-P6."],
                ["EP-M2", "5.02 a 15.00", "Válida, banda ligera", "Base + peso x 2.00, con peso entre 0.01 y 5.00."],
                ["EP-M3", "25.04 a 85.00", "Válida, banda pesada", "Base + peso x 4.00, con peso entre 5.01 y 20.00."],
            ],
            [18 * mm, 40 * mm, 40 * mm, 76 * mm],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "Entre 15.00 y 25.04 hay un hueco: al cruzar 5.00 kg la tarifa salta de 2.00 a 4.00, así que un NUEVO/ESTANDAR no puede producir, por ejemplo, 20.00. La partición no es un intervalo continuo.",
            style["Body"],
        )
    )

    story.append(Paragraph("Análisis de valores límite (BVA) de peso y monto", style["H2"]))
    story.append(
        table(
            [
                ["Caso", "Peso", "Monto esperado", "Resultado observado"],
                ["Justo bajo el mínimo", "0.00", "Sin monto", "422 WEIGHT_BELOW_MINIMUM"],
                ["Mínimo válido", "0.01", "5.02", "200, tarifa 2.00, monto 5.02"],
                ["Tope de la banda ligera", "5.00", "15.00", "200, tarifa 2.00, monto 15.00"],
                ["Inicio de la banda pesada", "5.01", "25.04", "200, tarifa 4.00, monto 25.04"],
                ["Máximo válido", "20.00", "85.00", "200, tarifa 4.00, monto 85.00"],
                ["Justo sobre el máximo", "20.01", "Sin monto", "422 WEIGHT_LIMIT_EXCEEDED"],
            ],
            [42 * mm, 24 * mm, 36 * mm, 72 * mm],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Cliente NUEVO y envío ESTANDAR. El paso de la frontera es 0.01 kg, que es la precisión admitida.", style["Caption"]))

    story.append(Paragraph("Tabla de decisión: tipo de cliente x tipo de envío", style["H2"]))
    story.append(
        Paragraph(
            "Peso fijo 1.00 kg, dentro de la banda de 2.00. Subtotal = 7.00 en las seis reglas. Las combinaciones inválidas (REGULAR, URGENTE) quedan fuera de la tabla y se cubren como particiones de entrada.",
            style["Body"],
        )
    )
    story.append(
        table(
            [
                ["Regla", "Cliente", "Envío", "Recargo", "Descuento", "Monto", "Observado"],
                ["R1", "NUEVO", "ESTANDAR", "0.00", "0.00", "7.00", "Pass"],
                ["R2", "NUEVO", "EXPRESS", "1.75", "0.00", "8.75", "Pass"],
                ["R3", "FRECUENTE", "ESTANDAR", "0.00", "0.70", "6.30", "Pass"],
                ["R4", "FRECUENTE", "EXPRESS", "1.75", "0.88", "7.87", "Pass"],
                ["R5", "VIP", "ESTANDAR", "0.00", "1.40", "5.60", "Pass"],
                ["R6", "VIP", "EXPRESS", "1.75", "1.75", "7.00", "Pass"],
            ],
            [16 * mm, 28 * mm, 28 * mm, 22 * mm, 26 * mm, 22 * mm, 22 * mm],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "R4 redondea 8.75 x 0.10 = 0.875 a 0.88. R6 coincide con R1 porque 1.25 x 0.80 = 1: el recargo express y el descuento VIP se anulan. Es una consecuencia de la fórmula, no un error de cálculo. Las seis reglas están en tests/blackbox/test_quote_matrix.py.",
            style["Body"],
        )
    )

    story.append(Paragraph("4. Caja blanca", style["H1"]))
    story.append(
        Paragraph(
            "El sujeto es calculate_shipping_quote en backend/app/domain/quote_engine.py. La validación de formato y de catálogos vive fuera, para que el grafo sea el algoritmo de tarifa.",
            style["Body"],
        )
    )
    story.append(Paragraph("Grafo de flujo de control", style["H2"]))
    cfg = PdfImage(str(CFG_PATH), width=160 * mm, height=160 * mm * 1680 / 1400)
    story.append(cfg)
    story.append(Paragraph("Figura. CFG de calculate_shipping_quote. Los rombos son decisiones. Nodos 3 y 5 también llegan a Fin.", style["Caption"]))

    story.append(Paragraph("Complejidad ciclomática", style["H2"]))
    story.append(Paragraph("Método de predicados. Hay seis decisiones: nodos 2, 4, 6, 10, 12 y 15. V(G) = P + 1 = 6 + 1 = 7.", style["Body"]))
    story.append(Paragraph("Método de aristas y nodos. El grafo tiene 19 nodos y 24 aristas. V(G) = E − N + 2 = 24 − 19 + 2 = 7.", style["Body"]))
    story.append(Paragraph("Herramienta. radon cc app/domain/quote_engine.py -s reporta calculate_shipping_quote con rango B y complejidad 7. Los tres resultados coinciden.", style["Body"]))
    story.append(
        table(
            [
                ["Nodo", "Aristas que salen"],
                ["1 Inicio", "2"],
                ["2 peso &lt; 0.01", "3 (sí), 4 (no)"],
                ["3 Rechazo mínimo", "19"],
                ["4 peso &gt; 20", "5 (sí), 6 (no)"],
                ["5 Rechazo límite", "19"],
                ["6 peso &lt;= 5", "7 (sí), 8 (no)"],
                ["7 y 8 tarifas", "9"],
                ["9 subtotal", "10"],
                ["10 NUEVO", "11 (sí), 12 (no)"],
                ["11 descuento 0%", "15"],
                ["12 FRECUENTE", "13 (sí), 14 (no)"],
                ["13 y 14 descuentos", "15"],
                ["15 EXPRESS", "16 (sí), 17 (no)"],
                ["16 y 17 recargos", "18"],
                ["18 total", "19"],
            ],
            [55 * mm, 119 * mm],
        )
    )

    story.append(Paragraph("Caminos independientes", style["H2"]))
    story.append(
        Paragraph(
            "Una base de 7 caminos cubre cada decisión por su lado verdadero y su lado falso. Están automatizados en tests/whitebox/test_cfg_paths.py.",
            style["Body"],
        )
    )
    story.append(
        table(
            [
                ["Camino", "Decisiones que abre", "Entrada", "Salida observada"],
                ["P1", "2 sí", "0.00 kg", "WEIGHT_BELOW_MINIMUM"],
                ["P2", "2 no, 4 sí", "20.01 kg", "WEIGHT_LIMIT_EXCEEDED"],
                ["P3", "6 sí, 10 sí, 15 no", "5.00, NUEVO, ESTANDAR", "tarifa 2.00, monto 15.00"],
                ["P4", "6 sí, 10 no, 12 sí, 15 sí", "5.00, FRECUENTE, EXPRESS", "monto 16.87"],
                ["P5", "10 no, 12 no, 15 no", "5.00, VIP, ESTANDAR", "descuento 20%, monto 12.00"],
                ["P6", "6 no, 10 sí, 15 no", "5.01, NUEVO, ESTANDAR", "tarifa 4.00, monto 25.04"],
                ["P7", "6 no, 12 sí, 15 sí", "5.01, FRECUENTE, EXPRESS", "monto 28.17"],
            ],
            [18 * mm, 48 * mm, 52 * mm, 56 * mm],
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "P4 comprueba el redondeo: subtotal 15.00, recargo 3.75, bruto 18.75, 10% de 18.75 es 1.875 y half-up lo deja en 1.88. Monto 16.87. P7: subtotal 25.04, recargo 6.26, bruto 31.30, descuento 3.13, monto 28.17.",
            style["Body"],
        )
    )

    story.append(Paragraph("5. Cobertura", style["H1"]))
    story.append(
        Paragraph(
            "Comando: pytest con --cov=app --cov-branch. El umbral fail_under = 85 está en backend/pyproject.toml. La corrida usada para este informe cubre todas las sentencias y todas las ramas. No hay líneas excluidas. quote_engine.py aporta 12 ramas; quote_service.py aporta el resto (formato, catálogos y campos de más). El informe HTML queda en docs/evidence/coverage-html/index.html.",
            style["Body"],
        )
    )
    shot("07-cobertura.png", "Figura. Reporte de coverage.py: 100% de sentencias y 100% de ramas.", story, style)
    story.append(
        Paragraph(
            "Análisis: el porcentaje está por encima del 85% porque cada predicado del grafo tiene prueba en ambos lados y los rechazos HTTP (JSON inválido, recurso inexistente, método no permitido y error interno) también pasan por su manejador. El error interno no devuelve el texto de la excepción.",
            style["Body"],
        )
    )

    story.append(Paragraph("6. Ejecución en vivo de la interfaz", style["H1"]))
    story.append(
        Paragraph(
            "Con la API en el puerto 8000 y el muelle en el puerto 5173 se recorrió el flujo real en un navegador de escritorio de 1440×900. Las capturas salen de esa ejecución, no de un montaje.",
            style["Body"],
        )
    )
    shot("01-estandar-nuevo.png", "Figura. 2.50 kg, NUEVO, ESTANDAR. La API responde monto 10.00 y tarifa 2.00.", story, style)
    shot("02-frecuente-express.png", "Figura. Mismo peso, FRECUENTE y EXPRESS. Recargo 2.50, descuento 1.25, monto 11.25. La guía fijada queda en la sesión.", story, style)
    shot("03-frontera-5-00.png", "Figura. Frontera 5.00 kg. Sigue la tarifa de 2.00. Monto 15.00.", story, style)
    shot("04-frontera-5-01.png", "Figura. Frontera 5.01 kg. La tarifa pasa a 4.00. Cargo 20.04 y monto 25.04.", story, style)
    shot("05-limite-excedido.png", "Figura. 22.00 kg. El muelle muestra el rechazo de la API: límite excedido. No hay monto.", story, style)
    shot("06-peso-invalido.png", "Figura. El cliente bloquea «abc» antes de enviar la cotización y explica que el peso debe ser decimal.", story, style)

    story.append(Paragraph("7. Cómo reproducirlo", style["H1"]))
    story.append(
        Paragraph(
            "Backend: crear el entorno en backend, instalar requirements.txt, ejecutar pytest y uvicorn app.main:app --port 8000. Frontend: en frontend, npm install, npm test y npm run dev. Abrir http://localhost:5173. Este PDF se regenera con docs/build_report.py usando el mismo entorno.",
            style["Body"],
        )
    )
    story.append(Paragraph("Herramientas usadas", style["H2"]))
    story.append(
        table(
            [
                ["Pieza", "Herramienta"],
                ["API", "Python 3.14, FastAPI, Uvicorn, Decimal"],
                ["Pruebas de API y dominio", "pytest, pytest-cov, coverage.py"],
                ["Complejidad", "radon"],
                ["Interfaz", "React 19, TypeScript, Vite"],
                ["Movimiento", "Framer Motion"],
                ["Tipografía embebida", "Fontsource: Fraunces, Outfit, IBM Plex Mono"],
                ["Prueba de entrada", "Vitest"],
                ["Capturas", "Playwright sobre Microsoft Edge, contra los servidores en ejecución"],
                ["Informe", "ReportLab y Pillow"],
            ],
            [55 * mm, 119 * mm],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "No hay base de datos: la cotización es un cálculo. Las guías fijadas viven solo en la sesión del navegador y se etiquetan como folio local.",
            style["Body"],
        )
    )

    document = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Informe de calidad FastExpress",
        author="FastExpress",
    )
    document.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(PDF_PATH)


if __name__ == "__main__":
    build()
