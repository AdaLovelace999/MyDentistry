from flask import render_template, Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.card_number'))
    date = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<appointments {self.id}>"


class Doctors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialties.id'))
    cabinet = db.Column(db.String(8), nullable=False)
    phone = db.Column(db.String(12), unique=True)
    d = db.relationship('Appointments', backref='doctors', uselist=False)

    def __repr__(self):
        return f"<doctors {self.id}>"


class Patients(db.Model):
    card_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(12), unique=True)
    p = db.relationship('Appointments', backref='patients', uselist=False)

    def __repr__(self):
        return f"<patients {self.id}>"


class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    serv = db.relationship('Appointments', backref='services', uselist=False)

    def __repr__(self):
        return f"<services {self.id}>"


class Specialties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    spec = db.relationship('Doctors', backref='specialties', uselist=False)

    def __repr__(self):
        return f"<specialties {self.id}>"


@app.route('/')
def index():
    now = datetime.utcnow()
    appointments = Appointments.query.where(Appointments.date >= now).limit(5)
    pat = Patients.query.all()
    return render_template("index.html", title="Главная", appointments=appointments, pat=pat, now=now)


@app.route("/appointments")
def show_appointments():
    appointments = Appointments.query.order_by(Appointments.date.desc()).all()
    pat = Patients.query.all()
    return render_template('appointments.html', title="Прием", appointments=appointments, pat=pat)


@app.route("/appointments/<int:id>")
def show_appointments_detail(id):
    doc = Doctors.query.all()
    pat = Patients.query.all()
    serv = Services.query.all()
    ap = Appointments.query.get(id)
    return render_template('appointments-detail.html', ap=ap, doc=doc, pat=pat, serv=serv)


@app.route("/appointments/<int:id>/delete")
def delete_appointment(id):
    appointment = Appointments.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        return redirect(url_for('show_appointments'))
    except:
        db.session.rollback()
        print("Ошибка удаления записи из БД")


@app.route("/appointments/<int:id>/update", methods=("POST", "GET"))
def update_appointment(id):
    appointment = Appointments.query.get(id)
    doc = Doctors.query.all()
    pat = Patients.query.all()
    serv = Services.query.all()
    if request.method == "POST":
        try:
            appointment.doctor_id = request.form['doctor_id']
            appointment.patient_id = request.form['patient_id']
            appointment.date = request.form['date']
            appointment.time = request.form['time']
            appointment.service_id = request.form['service_id']
            appointment.quantity = request.form['quantity']
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка редактирования записи в БД")

        return redirect(url_for('show_appointments'))

    return render_template('update-appointment.html', title="Редактировать прием", doc=doc, pat=pat,
                           appointment=appointment, serv=serv)


@app.route("/create-appointment", methods=("POST", "GET"))
def create_appointment():
    doc = Doctors.query.all()
    pat = Patients.query.all()
    serv = Services.query.all()
    if request.method == "POST":
        try:
            appointment = Appointments(doctor_id=request.form['doctor_id'], patient_id=request.form['patient_id'],
                                       date=request.form['date'], time=request.form['time'],
                                       service_id=request.form['service_id'], quantity=request.form['quantity'])
            db.session.add(appointment)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('show_appointments'))

    return render_template('create-appointment.html', title="Добавить запись", doc=doc, pat=pat, serv=serv)


@app.route("/doctors")
def show_doctors():
    doctors = Doctors.query.order_by(Doctors.id).all()
    return render_template('doctors.html', title="Врачи", doctors=doctors)


@app.route("/doctors/<int:id>")
def show_doctors_detail(id):
    spec = Specialties.query.all()
    doctor = Doctors.query.get(id)
    return render_template('doctors-detail.html', doctor=doctor, spec=spec)


@app.route("/doctors/<int:id>/delete")
def delete_doctor(id):
    doctor = Doctors.query.get_or_404(id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        return redirect(url_for('show_doctors'))
    except:
        db.session.rollback()
        print("Ошибка удаления записи из БД")


@app.route("/doctors/<int:id>/update", methods=("POST", "GET"))
def update_doctor(id):
    spec = Specialties.query.all()
    doctor = Doctors.query.get(id)
    if request.method == "POST":
        try:
            doctor.name = request.form['name']
            doctor.speciality_id = request.form['speciality_id']
            doctor.cabinet = request.form['cabinet']
            doctor.phone = request.form['phone']
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка редактирования записи в БД")

        return redirect(url_for('show_doctors'))

    return render_template('update-doctor.html', title="Редактировать врача", doctor=doctor, spec=spec)


@app.route("/create-doctor", methods=("POST", "GET"))
def create_doctor():
    spec = Specialties.query.all()
    if request.method == "POST":
        try:
            doc = Doctors(name=request.form['name'], speciality_id=request.form['speciality_id'],
                          cabinet=request.form['cabinet'], phone=request.form['phone'])
            db.session.add(doc)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('show_doctors'))

    return render_template('create-doctor.html', title="Добавить врача", spec=spec)


@app.route("/patients")
def show_patients():
    patients = Patients.query.order_by(Patients.card_number).all()
    return render_template('patients.html', title="Пациенты", patients=patients)


@app.route("/patients/<int:card_number>")
def show_patients_detail(card_number):
    patient = Patients.query.get(card_number)
    return render_template('patients-detail.html', patient=patient)


@app.route("/patients/<int:card_number>/delete")
def delete_patient(card_number):
    patient = Patients.query.get_or_404(card_number)
    try:
        db.session.delete(patient)
        db.session.commit()
        return redirect(url_for('show_patients'))
    except:
        db.session.rollback()
        print("Ошибка удаления записи из БД")


@app.route("/patients/<int:card_number>/update", methods=("POST", "GET"))
def update_patient(card_number):
    patient = Patients.query.get(card_number)
    if request.method == "POST":
        try:
            patient.name = request.form['name']
            patient.birthday = request.form['birthday']
            patient.sex = request.form['sex']
            patient.address = request.form['address']
            patient.email = request.form['email']
            patient.phone = request.form['phone']
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка редактирования записи в БД")

        return redirect(url_for('show_patients'))

    return render_template('update-patient.html', title="Редактировать пациента", patient=patient)


@app.route("/create-patient", methods=("POST", "GET"))
def create_patient():
    if request.method == "POST":
        try:
            patient = Patients(name=request.form['name'],  birthday=request.form['birthday'], sex=request.form['sex'],
                               address=request.form['address'], email=request.form['email'], phone=request.form['phone'])
            db.session.add(patient)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('show_patients'))

    return render_template('create-patient.html', title="Добавить пациента")


@app.route("/specialties")
def show_specialties():
    specialties = Specialties.query.order_by(Specialties.id).all()
    return render_template('specialties.html', title="Специальности", specialties=specialties)


@app.route("/specialties/<int:id>")
def show_specialties_detail(id):
    speciality = Specialties.query.get(id)
    return render_template('specialties-detail.html', speciality=speciality)


@app.route("/specialties/<int:id>/delete")
def delete_speciality(id):
    speciality = Specialties.query.get_or_404(id)
    try:
        db.session.delete(speciality)
        db.session.commit()
        return redirect(url_for('show_specialties'))
    except:
        db.session.rollback()
        print("Ошибка удаления записи из БД")


@app.route("/specialties/<int:id>/update", methods=("POST", "GET"))
def update_speciality(id):
    speciality = Specialties.query.get(id)
    if request.method == "POST":
        try:
            speciality.name = request.form['name']
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка редактирования записи в БД")

        return redirect(url_for('show_specialties'))

    return render_template('update-speciality.html', title="Редактировать специальность", speciality=speciality)


@app.route("/create-speciality", methods=("POST", "GET"))
def create_speciality():
    if request.method == "POST":
        try:
            speciality = Specialties(name=request.form['name'])
            db.session.add(speciality)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('show_specialties'))

    return render_template('create-speciality.html', title="Добавить специальность")


@app.route("/services")
def show_services():
    services = Services.query.order_by(Services.id).all()
    return render_template('services.html', title="Услуги", services=services)


@app.route("/services/<int:id>")
def show_services_detail(id):
    service = Services.query.get(id)
    return render_template('services-detail.html', service=service)


@app.route("/services/<int:id>/delete")
def delete_service(id):
    service = Services.query.get_or_404(id)
    try:
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('show_services'))
    except:
        db.session.rollback()
        print("Ошибка удаления записи из БД")


@app.route("/create-service", methods=("POST", "GET"))
def create_service():
    if request.method == "POST":
        try:
            service = Services(name=request.form['name'], description=request.form['description'],
                               price=request.form['price'])
            db.session.add(service)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('show_services'))

    return render_template('create-service.html', title="Добавить услугу")


@app.route("/services/<int:id>/update", methods=("POST", "GET"))
def update_service(id):
    service = Services.query.get(id)
    if request.method == "POST":
        try:
            service.name = request.form['name']
            service.description = request.form['description']
            service.price = request.form['price']
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка редактирования записи в БД")

        return redirect(url_for('show_services'))

    return render_template('update-service.html', title="Редактировать услугу", service=service)


if __name__ == "__main__":
    app.run(debug=True)
