from flask import Flask, request, redirect, url_for, flash, send_file, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import zipfile
import tempfile

# ==============================
# CONFIGURACIÓN
# ==============================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'participantes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================
# MODELO
# ==============================
class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120))
    documento = db.Column(db.String(50))
    ponencia = db.Column(db.String(200))

# ==============================
# CARGAR EXCEL
# ==============================
def cargar_participantes():
    excel_path = os.path.join(basedir, "participantes.xlsx")

    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)

        Participante.query.delete()

        for _, row in df.iterrows():
            nuevo = Participante(
                nombre=row['nombre'],
                email=row['email'],
                documento=str(row['documento']),
                ponencia=row['ponencia']
            )
            db.session.add(nuevo)

        db.session.commit()

with app.app_context():
    db.create_all()
    cargar_participantes()

# ==============================
# HTML EMBEBIDO
# ==============================
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Certificados</title>

<style>
body {
    margin: 0;
    font-family: Arial;
    background: linear-gradient(135deg,#1e3c72,#2a5298);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.container {
    background: white;
    padding: 40px;
    border-radius: 12px;
    width: 380px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
h2 {
    margin-bottom: 20px;
}
input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border-radius: 6px;
    border: 1px solid #ccc;
}
button {
    padding: 12px;
    width: 100%;
    background: #2a5298;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
button:hover {
    background: #1e3c72;
}
img {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 10px;
}
.flash {
    color: red;
    margin-bottom: 10px;
}
</style>
</head>

<body>

<div class="container">

<img src="/static/evento1.jpg">
<img src="/static/evento2.jpg">

<h2>Descargar Certificados</h2>

{% with messages = get_flashed_messages() %}
  {% if messages %}
    <div class="flash">{{ messages[0] }}</div>
  {% endif %}
{% endwith %}

<form method="POST">
<input type="text" name="documento" placeholder="Ingrese su documento" required>
<button type="submit">Descargar</button>
</form>

</div>

</body>
</html>
"""

# ==============================
# RUTA
# ==============================
@app.route('/', methods=['GET', 'POST'])
def descargar():
    if request.method == 'POST':
        documento = request.form['documento'].strip()

        participantes = Participante.query.filter_by(documento=documento).all()

        if not participantes:
            flash("Documento no encontrado")
            return redirect(url_for('descargar'))

        temp_dir = tempfile.mkdtemp()
        archivos = []

        for p in participantes:
            pdf_path = os.path.join(temp_dir, f"{p.ponencia}.pdf")
            generar_certificado(p.nombre, p.ponencia, pdf_path)
            archivos.append(pdf_path)

        zip_path = os.path.join(temp_dir, f"{documento}.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for archivo in archivos:
                zipf.write(archivo, os.path.basename(archivo))

        return send_file(zip_path, as_attachment=True)

    return render_template_string(HTML)

# ==============================
# GENERAR CERTIFICADO
# ==============================
def generar_certificado(nombre, ponencia, output):
    base = os.path.join(basedir, "static", "certificado_base.pdf")

    reader = PdfReader(base)
    writer = PdfWriter()

    overlay = os.path.join(basedir, "overlay_temp.pdf")

    c = canvas.Canvas(overlay, pagesize=letter)

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(300, 250, nombre)

    c.setFont("Helvetica", 18)
    c.drawCentredString(300, 200, ponencia)

    c.save()

    overlay_pdf = PdfReader(overlay)
    page = reader.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

    with open(output, "wb") as f:
        writer.write(f)

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
