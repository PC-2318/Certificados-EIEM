from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from reportlab.pdfgen import canvas

# 🔹 Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participantes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔹 Modelo de la base de datos
class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    documento = db.Column(db.String(50), unique=True, nullable=False)

# 🔹 Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# 🔹 Ruta principal (redirige a la página de registro)
@app.route('/')
def home():
    return redirect(url_for('registro'))

# 🔹 Ruta de Registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        documento = request.form['documento']

        if Participante.query.filter_by(documento=documento).first():
            flash("Este documento ya está registrado.", "danger")
            return redirect(url_for('registro'))

        nuevo_participante = Participante(nombre=nombre, email=email, documento=documento)
        db.session.add(nuevo_participante)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes descargar tu certificado.", "success")
        return redirect(url_for('descargar'))

    return render_template('registro.html')

# 🔹 Ruta de Descarga del Certificado
@app.route('/descargar', methods=['GET', 'POST'])
def descargar():
    if request.method == 'POST':
        documento = request.form['documento']
        participante = Participante.query.filter_by(documento=documento).first()

        if not participante:
            flash("No se encontró un participante con ese documento.", "danger")
            return redirect(url_for('descargar'))

        # Ruta donde se guardará el certificado personalizado
        pdf_output = f"certificados/{participante.documento}.pdf"
        generar_certificado(participante.nombre, pdf_output)

        return send_file(pdf_output, as_attachment=True)

    return render_template('descargar.html')

# 🔹 Función para Generar Certificado en PDF
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generar_certificado(nombre, pdf_output):
    certificado_base = "static/certificado_base.pdf"  # Asegúrate de que el archivo esté aquí

    if not os.path.exists("certificados"):
        os.makedirs("certificados")

    # Leer el PDF base
    reader = PdfReader(certificado_base)
    writer = PdfWriter()

    # Crear un PDF en blanco para superponer el texto
    overlay_path = "certificados/temp_overlay.pdf"
    c = canvas.Canvas(overlay_path, pagesize=letter)

    # Ajustar la posición del nombre en el certificado
    x_pos = 350  # Cambia este valor para mover el nombre a la derecha o izquierda
    y_pos = 215  # Cambia este valor para subir o bajar el nombre

    c.setFont("Helvetica-Bold", 30)  # Tamaño y tipo de letra
    c.drawCentredString(x_pos, y_pos, nombre)  # Ubicación del nombre en el certificado
    c.save()

    # Combinar el PDF base con el texto agregado
    overlay_reader = PdfReader(overlay_path)
    page = reader.pages[0]
    page.merge_page(overlay_reader.pages[0])
    writer.add_page(page)

    # Guardar el certificado final con el nombre del participante
    with open(pdf_output, "wb") as output_pdf:
        writer.write(output_pdf)

if __name__ == "__main__":
    app.run(debug=True)
