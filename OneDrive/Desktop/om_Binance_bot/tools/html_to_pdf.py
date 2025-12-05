from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import html2text

IN = 'report.html'
OUT = 'report.pdf'

with open(IN, 'r', encoding='utf-8') as f:
    html = f.read()

text = html2text.html2text(html)

c = canvas.Canvas(OUT, pagesize=A4)
width, height = A4
margin = 40
x = margin
y = height - margin

c.setFont('Helvetica', 10)
line_height = 12

for line in text.splitlines():
    if y < margin:
        c.showPage()
        c.setFont('Helvetica', 10)
        y = height - margin
    # truncate long lines to page width
    max_chars = 110
    while len(line) > 0:
        chunk = line[:max_chars]
        c.drawString(x, y, chunk)
        line = line[max_chars:]
        y -= line_height
        if y < margin and len(line) > 0:
            c.showPage()
            c.setFont('Helvetica', 10)
            y = height - margin

c.save()
print('Created report.pdf')
