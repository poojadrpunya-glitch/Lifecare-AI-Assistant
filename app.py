from flask import Flask, render_template, request, redirect, session
import sqlite3
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "lifecare"

# ✅ 1. DEFINE NUMBERS FIRST
HOSPITAL_NUMBER = "+916362641597"
DOCTOR_NUMBER = "+919483081597"

# Twilio credentials
account_sid = "YOUR_SID"
auth_token = "YOUR_TOKEN"

client = Client(account_sid, auth_token)

TWILIO_NUMBER = "+1234567890"

def send_sms(to, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=to
        )

        print("SMS Sent Successfully", message.sid)

    except Exception as e:
        print("SMS Error:", e)
# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        gender TEXT,
        pregnant TEXT,
        password TEXT
    )
    """)

    # tokens
    c.execute("""
    CREATE TABLE IF NOT EXISTS tokens(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        hospital TEXT,
        appointment_date TEXT,
        status TEXT DEFAULT 'Waiting'
    )
    """)

    # emergency
    c.execute("""
    CREATE TABLE IF NOT EXISTS emergency_alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        phone TEXT,
        location TEXT,
        emergency_type TEXT,
        status TEXT DEFAULT 'Pending',
        alert_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------

@app.route('/')
def home():
    return redirect('/register')

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        pregnant = request.form['pregnant']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO users
        (name,email,phone,gender,pregnant,password)
        VALUES (?,?,?,?,?,?)
        """,(name,email,phone,gender,pregnant,password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
        SELECT * FROM users
        WHERE email=? AND password=?
        """, (email, password))

        user = c.fetchone()

        conn.close()

        if user:

            session['user'] = user[1]

            return redirect('/welcome')

    return render_template("login.html")

# ---------------- WELCOME ----------------

@app.route('/welcome')
def welcome():
    return render_template("welcome.html")

# -----------Admin-----------
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "hospitaladmin" and password == "Lifecare@2026":

            session['admin'] = username
            return redirect('/admin_dashboard')

    return render_template("admin_login.html")

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT COUNT(*)
    FROM emergency_alerts
    WHERE status='Pending'
    """)

    alerts_count = c.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        alerts_count=alerts_count
    )
#---------admin dashboard-------------

@app.route('/admin_dashboard')
def admin_dashboard():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    patients = c.fetchall()

    c.execute("SELECT * FROM emergency_alerts ORDER BY id DESC")
    alerts = c.fetchall()

    c.execute("SELECT * FROM tokens")
    tokens = c.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        patients=patients,
        alerts=alerts,
        tokens=tokens
    )
# ---------------- PREDICTION PAGE ----------------

@app.route('/prediction')
def prediction():
    return render_template("prediction.html")

from datetime import datetime, timedelta

# ---------------- WOMEN CARE ----------------

@app.route('/women', methods=['GET','POST'])
def women():

    next_period = ""
    fertility = ""

    if request.method == 'POST':

        last_period = request.form['last_period']

        cycle = int(request.form['cycle'])

        last_date = datetime.strptime(
            last_period,
            "%Y-%m-%d"
        )

        next_period_date = last_date + timedelta(days=cycle)

        fertility_date = last_date + timedelta(days=14)

        next_period = next_period_date.strftime("%d-%m-%Y")

        fertility = fertility_date.strftime("%d-%m-%Y")

    return render_template(
        "women.html",
        next_period=next_period,
        fertility=fertility
    )

# ---------------- CREATE REMINDER TABLE ----------------

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS reminders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()

# ---------------- REMINDER PAGE ----------------

@app.route('/reminders', methods=['GET','POST'])
def reminders():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == 'POST':

        reminder_type = request.form['type']
        reminder_time = request.form['time']

        c.execute("""
        INSERT INTO reminders(type,time)
        VALUES (?,?)
        """,(reminder_type, reminder_time))

        conn.commit()

    c.execute("SELECT type,time FROM reminders")

    reminders = c.fetchall()

    conn.close()

    return render_template(
        "reminders.html",
        reminders=reminders
    )

# ---------------- ADVANCED DISEASE PREDICTION ----------------

@app.route('/predict', methods=['POST'])
def predict():

    fever = request.form['fever']
    cough = request.form['cough']
    headache = request.form['headache']
    sugar = request.form['sugar']
    bp = request.form['bp']
    heart = request.form['heart']
    fatigue = request.form['fatigue']
    breathing = request.form['breathing']

    disease = ""
    medicine = ""
    food = ""
    advice = ""
    probability = ""

    # ---------------- COVID ----------------

    if (
        fever == "Yes" and
        cough == "Yes" and
        breathing == "Yes"
    ):

        disease = "COVID-19"

        medicine = """
Paracetamol,
Vitamin C,
Steam inhalation
"""

        food = """
Warm water,
Soup,
Fruits,
Protein foods
"""

        advice = """
Wear mask,
Take rest,
Monitor oxygen level
"""

        probability = "88%"

    # ---------------- DENGUE ----------------

    elif (
        fever == "Yes" and
        headache == "Yes" and
        fatigue == "Yes"
    ):

        disease = "Dengue Fever"

        medicine = """
Paracetamol,
Doctor consultation,
Hydration therapy
"""

        food = """
Papaya leaf juice,
Kiwi,
Coconut water,
Soup
"""

        advice = """
Drink more fluids
and monitor platelets
"""

        probability = "84%"

    # ---------------- CHIKUNGUNYA ----------------

    elif (
        fever == "Yes" and
        headache == "Yes" and
        fatigue == "Yes" and
        bp == "Yes"
    ):

        disease = "Chikungunya"

        medicine = """
Pain relief medicines,
Paracetamol
"""

        food = """
Water,
Juices,
Protein-rich foods
"""

        advice = """
Take complete rest
and avoid dehydration
"""

        probability = "80%"

    # ---------------- FLU ----------------

    elif (
        fever == "Yes" and
        cough == "Yes"
    ):

        disease = "Flu / Viral Fever"

        medicine = """
Paracetamol,
Cold tablets
"""

        food = """
Soup,
Warm water,
Fruits
"""

        advice = """
Take rest and avoid cold foods
"""

        probability = "78%"

    # ---------------- ASTHMA ----------------

    elif (
        breathing == "Yes" and
        cough == "Yes"
    ):

        disease = "Asthma Probability"

        medicine = """
Inhaler,
Doctor consultation
"""

        food = """
Warm foods,
Avoid cold drinks
"""

        advice = """
Avoid dust and smoking
"""

        probability = "74%"

    # ---------------- DIABETES ----------------

    elif (
        sugar == "Yes" and
        fatigue == "Yes"
    ):

        disease = "Diabetes"

        medicine = """
Sugar testing required,
Doctor consultation
"""

        food = """
Low sugar diet,
Vegetables,
Protein foods
"""

        advice = """
Exercise daily and avoid sweets
"""

        probability = "72%"

    # ---------------- HIGH BP ----------------

    elif (
        bp == "Yes" and
        headache == "Yes"
    ):

        disease = "High Blood Pressure"

        medicine = """
BP monitoring tablets,
Doctor consultation
"""

        food = """
Low salt foods,
Vegetables,
Fruits
"""

        advice = """
Reduce stress and monitor BP
"""

        probability = "69%"

    # ---------------- HEART DISEASE ----------------

    elif (
        heart == "Yes" and
        breathing == "Yes"
    ):

        disease = "Heart Disease Probability"

        medicine = """
Cardiology consultation immediately
"""

        food = """
Low oil foods,
Heart healthy diet
"""

        advice = """
Avoid smoking and stress
"""

        probability = "85%"

    # ---------------- MIGRAINE ----------------

    elif (
        headache == "Yes" and
        fever == "No"
    ):

        disease = "Migraine"

        medicine = """
Pain relief tablets
"""

        food = """
Hydration,
Healthy diet
"""

        advice = """
Avoid stress and loud noise
"""

        probability = "65%"

    # ---------------- NORMAL ----------------

    else:

        disease = "General Weakness"

        medicine = """
Vitamin supplements
"""

        food = """
Balanced healthy diet
"""

        advice = """
Exercise and sleep properly
"""

        probability = "40%"

    return render_template(
        "prediction.html",
        disease=disease,
        medicine=medicine,
        food=food,
        advice=advice,
        probability=probability
    )

# ---------------- EMERGENCY PAGE ----------------

@app.route('/emergency', methods=['GET', 'POST'])
def emergency():

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        phone = request.form.get('phone')
        location = request.form.get('location')
        emergency_type = request.form.get('emergency_type')

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO emergency_alerts
        (patient_name, phone, location, emergency_type)
        VALUES (?,?,?,?)
        """, (patient_name, phone, location, emergency_type))

        conn.commit()
        conn.close()

        message = f"""
🚨 EMERGENCY ALERT 🚨

Patient: {patient_name}
Phone: {phone}
Location: {location}
Type: {emergency_type}
"""

        send_sms(phone, "🚨 Emergency received. Help is coming.")
        send_sms(HOSPITAL_NUMBER, message)
        send_sms(DOCTOR_NUMBER, message)

        return redirect('/admin_dashboard')   # ✅ IMPORTANT FIX

    return render_template("emergency.html")

# ---------------- CHATBOT PAGE ----------------

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

# ---------------- HEALTH HISTORY ----------------

@app.route('/history')
def history():
    return render_template("history.html")

#------------book token------------

@app.route('/book_token', methods=['GET','POST'])
def book_token():

    if request.method == 'POST':

        patient = request.form['patient']
        doctor = request.form['doctor']
        hospital = request.form['hospital']
        date = request.form['date']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO tokens
        (patient_name,doctor_name,hospital,appointment_date)
        VALUES (?,?,?,?)
        """,
        (
            patient,
            doctor,
            hospital,
            date,
        ))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template(
    "book_token.html",
    success="Token Booked Successfully"
)
# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)