# ------------------------------------------------------------
# Módulo para generar informes en PDF
# Así el profesor (o nosotros) podemos guardar los resultados
# ------------------------------------------------------------

import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def generar_pdf(nombre_modulo, parametros, resultados, figura=None):
    """
    Crea un archivo PDF con los datos de la simulación.
    - nombre_modulo: título del módulo (ej. "GPON Planner")
    - parametros: diccionario con los valores de entrada
    - resultados: diccionario con los resultados
    - figura: objeto Figure de matplotlib (opcional)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    styles = getSampleStyleSheet()
    story = []

    # Título principal
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1E88E5'),
        alignment=1  # centrado
    )
    story.append(Paragraph("TelecomLab - Informe técnico", titulo_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Módulo:</b> {nombre_modulo}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Tabla de parámetros
    story.append(Paragraph("1. Parámetros introducidos", styles['Heading2']))
    data = [["Parámetro", "Valor"]]
    for k, v in parametros.items():
        data.append([k, str(v)])
    tabla1 = Table(data, colWidths=[2.5 * inch, 2.5 * inch])
    tabla1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E3F2FD')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tabla1)
    story.append(Spacer(1, 12))

    # Tabla de resultados
    story.append(Paragraph("2. Resultados obtenidos", styles['Heading2']))
    data2 = [["Métrica", "Valor"]]
    for k, v in resultados.items():
        data2.append([k, str(v)])
    tabla2 = Table(data2, colWidths=[2.5 * inch, 2.5 * inch])
    tabla2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#43A047')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F5E9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tabla2)

    # Si hay figura, la añadimos
    if figura is not None:
        story.append(Spacer(1, 12))
        story.append(Paragraph("3. Gráfico / Esquema", styles['Heading2']))
        img_buffer = io.BytesIO()
        figura.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img = Image(img_buffer)
        img.drawWidth = 6 * inch
        img.drawHeight = (
            img.imageHeight *
            (img.drawWidth / img.imageWidth)
        )
        story.append(img)

    # Pie de página
    story.append(Spacer(1, 24))
    story.append(Paragraph("Generado con TelecomLab · Universidad de Granada", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer