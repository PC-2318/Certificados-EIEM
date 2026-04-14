from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import re

# Configuración de la aplicación Flask=
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participantes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    documento = db.Column(db.String(50), unique=True, nullable=False)

# =========================
# VALIDACIÓN FLEXIBLE
# =========================
def validar_documento(doc):
    patron = r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\-_.]{1,50}$'
    return re.match(patron, doc)

# =========================
# SANITIZAR NOMBRE ARCHIVO
# =========================
def sanitizar_documento(doc):
    return re.sub(r'[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\-_.]', '', doc)

# =========================
# CARGAR PARTICIPANTES
# =========================
def cargar_participantes():
    excel_path = os.path.join(os.path.dirname(__file__), "participantes.xlsx")

    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, dtype={"documento": str})

        # 🔥 Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        print("Columnas detectadas:", df.columns.tolist())

        # Validar que existan las columnas necesarias
        if 'nombre' not in df.columns or 'documento' not in df.columns:
            print("❌ ERROR: El Excel debe tener columnas 'nombre' y 'documento'")
            return

        for _, row in df.iterrows():
            doc = str(row['documento']).strip()

            if not doc:
                continue  # evitar registros vacíos

            if not Participante.query.filter_by(documento=doc).first():
                nuevo = Participante(
                    nombre=str(row['nombre']).strip(),
                    email=str(row['email']).strip() if 'email' in df.columns and pd.notna(row.get('email')) else None,
                    documento=doc
                )
                db.session.add(nuevo)

        db.session.commit()
        print("✅ Participantes cargados correctamente.")
    else:
        print("⚠️ No se encontró el archivo 'participantes.xlsx'.")

# =========================
# INICIALIZACIÓN
# =========================
with app.app_context():
    db.create_all()
    try:
        cargar_participantes()
    except Exception as e:
        print(f"❌ Error al cargar participantes: {e}")

# =========================
# RUTAS
# =========================
@app.route('/')
def home():
    return redirect(url_for('descargar'))

@app.route('/descargar', methods=['GET', 'POST'])
def descargar():
    if request.method == 'POST':
        documento = request.form['documento'].strip()

        # Validación flexible
        if not validar_documento(documento):
            flash("❌ Documento inválido.", "danger")
            return redirect(url_for('descargar'))

        # Búsqueda case-insensitive
        participante = Participante.query.filter(
            db.func.lower(Participante.documento) == documento.lower()
        ).first()

        if not participante:
            flash("❌ No se encontró un participante con ese documento.", "danger")
            return redirect(url_for('descargar'))

        documento_seguro = sanitizar_documento(participante.documento)
        pdf_output = f"certificados/{documento_seguro}.pdf"

        # No regenerar si ya existe
        if not os.path.exists(pdf_output):
            generar_certificado(participante.nombre, pdf_output)

        return send_file(pdf_output, as_attachment=True)

    return render_template('descargar.html')

# =========================
# GENERAR CERTIFICADO
# =========================
def generar_certificado(nombre, pdf_output):
    certificado_base = "static/certificado_base.pdf"

    if not os.path.exists(certificado_base):
        print("⚠️ No se encontró el certificado base.")
        return

    if not os.path.exists("certificados"):
        os.makedirs("certificados")

    reader = PdfReader(certificado_base)
    writer = PdfWriter()

    overlay_path = "certificados/temp_overlay.pdf"
    c = canvas.Canvas(overlay_path, pagesize=letter)

    # Posición del nombre
    x_pos = 340
    y_pos = 143

    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(x_pos, y_pos, nombre)
    c.save()

    overlay_reader = PdfReader(overlay_path)
    page = reader.pages[0]
    page.merge_page(overlay_reader.pages[0])
    writer.add_page(page)

    with open(pdf_output, "wb") as output_pdf:
        writer.write(output_pdf)

    # Limpiar archivo temporal
    if os.path.exists(overlay_path):
        os.remove(overlay_path)

# ====================================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    app.run(debug=True)