# Ruta principal (Redirige a la página de registro)
@app.route('/')
def home():
    return redirect(url_for('registro'))

# Ruta de Registro
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

