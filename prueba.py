from flask import Flask, request, redirect, url_for, flash, send_file, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participantes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# MODELO
# =========================
class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    documento = db.Column(db.String(50), unique=True, nullable=False)

# =========================
# HTML + CSS EMBEBIDO
# =========================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

<title>Descargar Certificado</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}

body {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.imagen-circular {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
}

.container {
    background: white;
    padding: 40px;
    border-radius: 12px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    text-align: center;
}

h2 {
    margin-bottom: 25px;
    color: #333;
}

label {
    display: block;
    text-align: left;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
}

input {
    width: 100%;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #ccc;
    margin-bottom: 20px;
}

button {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: #4facfe;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #3a8ee6;
}

.flash {
    margin-bottom: 15px;
    color: red;
}
</style>
</head>

<body>

<div class="container">
    <img src="https://www.uniatlantico.edu.co/wp-content/uploads/2022/04/cropped-favicon-32x32.png" class="imagen-circular">
    <h2>Descargar Certificado</h2>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">
            {% for message in messages %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <form method="post">
        <label>Documento de Identidad</label>
        <input type="text" name="documento" required>
        <button type="submit">Descargar</button>
    </form>
</div>

</body>
</html>
"""

# =========================
# CARGAR EXCEL
# =========================
def cargar_participantes():
    excel_path = "participantes.xlsx"
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, dtype={"documento": str})

        for _, row in df.iterrows():
            if not Participante.query.filter_by(documento=row['documento']).first():
                nuevo = Participante(
                    nombre=row['nombre'],
                    email=row.get('email', ''),
                    documento=row['documento']
                )
                db.session.add(nuevo)

        db.session.commit()
        print("✅ Participantes cargados")
    else:
        print("⚠️ No se encontró participantes.xlsx")

# =========================
# INICIALIZACIÓN
# =========================
with app.app_context():
    db.create_all()
    try:
        cargar_participantes()
    except Exception as e:
        print("Error:", e)

# =========================
# RUTAS
# =========================
@app.route('/', methods=['GET', 'POST'])
def descargar():
    if request.method == 'POST':
        documento = request.form['documento'].strip()
        participante = Participante.query.filter_by(documento=documento).first()

        if not participante:
            flash("❌ Documento no encontrado")
            return redirect(url_for('descargar'))

        pdf_output = f"certificados/{participante.documento}.pdf"
        generar_certificado(participante.nombre, pdf_output)

        return send_file(pdf_output, as_attachment=True)

    return render_template_string(HTML_TEMPLATE)

# =========================
# GENERAR PDF
# =========================
def generar_certificado(nombre, pdf_output):
    certificado_base = "certificado_base.pdf"

    if not os.path.exists(certificado_base):
        print("⚠️ Falta certificado_base.pdf")
        return

    if not os.path.exists("certificados"):
        os.makedirs("certificados")

    reader = PdfReader(certificado_base)
    writer = PdfWriter()

    overlay_path = "certificados/temp_overlay.pdf"
    c = canvas.Canvas(overlay_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(350, 215, nombre)
    c.save()

    overlay_reader = PdfReader(overlay_path)
    page = reader.pages[0]
    page.merge_page(overlay_reader.pages[0])
    writer.add_page(page)

    with open(pdf_output, "wb") as output_pdf:
        writer.write(output_pdf)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)