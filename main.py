from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQLdb
from flask import Flask, render_template, send_file
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from datetime import datetime, timedelta
import mysql.connector
import qrcode
import base64
from functools import wraps



app = Flask(__name__)
UPLOAD_FOLDER = 'static/builtin'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
last_scan_time = {}
last_scan_times_out = {}

def connection():
	try:
		conn = MySQLdb.connect(host="localhost",user="root",password="",db="attendance_db")
		return conn
	except Exception as e:
		return str(e)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    usertype = db.Column(db.String(30), nullable=False)
    
    
    


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('', 'error')
            return redirect(url_for('/'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login2')
def login2():
    return render_template('login2.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('', 'success')
    return redirect(url_for('/'))

@app.route('/')
def user():
	return render_template('usertype.html')

@app.route('/osas', methods=['GET', 'POST']) 
def osas():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password and admin.username == username:
            session['username'] = username  # Set the username in the session
            flash('', 'success')
            return redirect(url_for('dash'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/ssg', methods=['GET', 'POST'])
def ssg():
    if request.method == 'POST' :
        insti_email = request.form['insti_email']
        password = request.form['password']
        conn = connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ssg WHERE insti_email = '{}' AND password = '{}'".format(insti_email, password))
        ssg = cur.fetchall()
        
        if ssg and insti_email == insti_email:
            return redirect(url_for('ssgdash'))
        else:
            flash('Invalid password. Please enter a valid password.', 'error')
            return redirect(url_for('login2'))

@app.route('/save_qr_image', methods=['POST'])
def save_qr_image():
    data = request.json
    image_data = data.get("image")
    id = data.get("id")
    if image_data and id:
        image_data = image_data.replace("data:image/png;base64,", "")

        folder_path = "C:/Users/63907/Desktop/attendance system/static/builtin/qr.code/QRcode"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = os.path.join(folder_path, f"{id}.png")

        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        return jsonify({"success": True})

    return jsonify({"success": False})


@app.route('/ssg_process', methods=['GET', 'POST'])
def ssg_process():
	if request.method == "POST":
		id_ssg = request.form['id_ssg']
		insti_email = request.form['insti_email']
		password = request.form['password']
		Position = request.form['Position']
		conn = connection()
		cur = conn.cursor()
		cur.execute("INSERT INTO ssg VALUES('{}', '{}', '{}','{}')".format(id_ssg, insti_email, password, Position))
		conn.commit()
	return redirect(url_for('ssglist'))

@app.route('/addssg')
def addssg():
    return render_template('addssg.html')

@app.route('/ssglist')
def ssglist():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM ssg")
	ssg = cur.fetchall()	
	return render_template('ssglist.html', ssg = ssg)

@app.route('/updatessg')
def updatessg():
    return render_template('updatessg.html')


@app.route('/delete_process_ssg/<string:id_ssg>/')
def delete_process_ssg(id_ssg):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM ssg WHERE id_ssg = '{}'".format(id_ssg))
	conn.commit()
	return redirect(url_for('ssglist'))

@app.route('/update_ssg', methods=['GET', 'POST'])
def update_ssg():
	if request.method == "POST":
		id_ssg = request.form['id_ssg']
	insti_email = request.form['insti_email']
	password = request.form['password']
	Position = request.form['Position']

	conn = connection()
	cur = conn.cursor()
	cur.execute("UPDATE ssg SET insti_email = '{}', password = '{}', Position = '{}' WHERE id_ssg = '{}'".format(insti_email,password, Position,id_ssg))
	conn.commit()
	return redirect(url_for('ssglist'))

@app.route('/update_ssg_1/<string:id_ssg>/')
def update_ssg_1(id_ssg):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM ssg WHERE id_ssg = '{}'".format(id_ssg))
	ssg = cur.fetchone()
	return render_template('updatessg.html', ssg = ssg)


@app.route('/ssglist2')
def ssglist2():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM ssg")
	ssg = cur.fetchall()	
	return render_template('ssglist2.html', ssg = ssg)


@app.route('/dash')
@login_required
def dash():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM event_tbl")
	dash = cur.fetchall()	
	return render_template('maindash.html',  dash= dash)

@app.route('/ssgdash')
@login_required
def ssgdash():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM event_tbl")
	ssgd = cur.fetchall()	
	return render_template('ssgdash.html',  ssgd = ssgd)


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/addvent')
def addvent():
    return render_template('addvent.html')

@app.route('/Scanner2')
def Scanner2():
    return render_template('Scanner2.html')

@app.route('/ssgscanner2')
def ssgscanner2():
    return render_template('ssgscanner2.html')

@app.route('/ssg_logout')
def ssg_logout():
    return render_template('ssg_logout.html')

@app.route('/ssg_op_logout')
def ssg_op_logout():
    return render_template('ssg_op_logout.html')

@app.route('/Scanner')
def Scanner():
    return render_template('Scanner.html')

@app.route('/ssgscanner1')
def ssgscanner1():
    return render_template('ssgscanner1.html')

@app.route('/updatevent')
def updatevent():
    return render_template('update_event.html')
    

@app.route('/Logout')
def Logout():
    return render_template('logout.html')

@app.route('/a_dash')
def a_dash():
    return render_template('attendance_dash.html')

@app.route('/s_dash')
def s_dash():
    return render_template('scanner_dash.html')

@app.route('/ssg_addvent')
def ssg_addvent():
    return render_template('ssg_addvent.html')

@app.route('/ssgscanner_dash')
def ssgscanner_dash():
    return render_template('ssgscanner_dash.html')

@app.route('/op2')
def op2():
    return render_template('op_logout.html')

@app.route('/update_a')
def update_a():
    return render_template('update_att.html')

@app.route('/e_detail')
def e_detail():
    return render_template('event_details.html')

@app.route('/ssg_loginlist')
def ssg_loginlist():
    return render_template('ssg_loginlist.html')

@app.route('/update_ssg_event')
def update_ssg_event():
    return render_template('update_ssg_event.html')



@app.route('/insert_process', methods=['GET', 'POST'])
def insert_process():
	if request.method == "POST":
		id = request.form['id']
		fname = request.form['fname']
		mname = request.form['mname']
		lname = request.form['lname']
		email = request.form['email']
		department = request.form['department']
		conn = connection()
		cur = conn.cursor()
		cur.execute("INSERT INTO student_info VALUES('{}' , '{}' , '{}', '{}', '{}','{}')".format(id, fname, mname,lname,email,department))
		conn.commit()
	return redirect(url_for('insert'))

@app.route('/insert1', methods=['GET', 'POST'])
def insert1():
    if request.method == "POST":
        id = request.form['id']
        event = request.form['event']
        start = request.form['start']
        end = request.form['end']
        status = request.form['status']
        
        timestart = request.form['timestart']
        timeend = request.form['timeend']
        eventinfo = request.form['eventinfo']
        
        conn = connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO event_tbl VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(id, event, start, end, status, timestart, timeend, eventinfo))
        conn.commit()
    return redirect(url_for('addvent'))

@app.route('/insert3', methods=['GET', 'POST'])
def insert3():
    if request.method == "POST":
        id = request.form['id']
        event = request.form['event']
        start = request.form['start']
        end = request.form['end']
        status = request.form['status']
        conn = connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO event_tbl VALUES('{}', '{}', '{}', '{}', '{}')".format(id, event, start, end, status))
        conn.commit()
    return redirect(url_for('ssg_addvent'))

@app.route('/insert_process2', methods=['GET', 'POST'])
def insert_process2():
	if request.method == "POST":
		usn = request.form['usn']
		fullname = request.form['fullname']
		event = request.form['event']
		department = request.form['department']
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M %p')
		conn = connection()
		cur = conn.cursor()
		cur.execute("INSERT INTO attendance_tbl VALUES('{}', '{}', '{}', '{}','{}','{}')".format(id, usn, fullname, event, department, current_time))
		conn.commit()
	return redirect(url_for('Scanner'))

@app.route('/insert2', methods=['GET', 'POST'])
def insert2():
	if request.method == "POST":
		usn = request.form['usn']
		fullname = request.form['fullname']
		event = request.form['event']
		department = request.form['department']
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M %p')
		conn = connection()
		cur = conn.cursor()
		cur.execute("INSERT INTO attendance_tbl_out VALUES('{}', '{}', '{}', '{}', '{}','{}')".format(id, usn, fullname,event,department, current_time))
		conn.commit()
	return redirect(url_for('op2'))

@app.route('/insert_process3', methods=['GET', 'POST'])
def insert_process3():
	if request.method == "POST":
		id = request.form['id']
		username = request.form['username']
		password = request.form['password']
		usertype = request.form['usertype']
		conn = connection()
		cur = conn.cursor()
		cur.execute("INSERT INTO admin VALUES('{}', '{}', '{}','{}')".format(id, username, password, usertype))
		conn.commit()
	return redirect(url_for('adminlist'))

@app.route('/event')
def event():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute('SELECT * FROM event_tbl')
	das = cur.fetchall()
	cur.execute("SELECT * FROM attendance_tbl")
	dis = cur.fetchall()
	return render_template('eventlist.html', das = das, dis=dis)

@app.route('/ssgeventlist')
def ssgeventlist():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute('SELECT * FROM event_tbl')
	dt = cur.fetchall()
	cur.execute("SELECT * FROM attendance_tbl")
	st = cur.fetchall()
	return render_template('ssgeventlist.html', dt = dt, st=st)

@app.route('/logout_list', methods = ['GET'])
def logout_list():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl_out WHERE event = %s", (event,))
	di = cur.fetchall()	
	return render_template('logout_list.html', di = di)

@app.route('/logout3', methods = ['GET'])
def logout3():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl_out WHERE event = %s", (event,))
	log = cur.fetchall()	
	return render_template('logout3.html', log = log)

@app.route('/ssg_logout_list', methods = ['GET'])
def ssg_logout_list():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl_out WHERE event = %s", (event,))
	di = cur.fetchall()	
	return render_template('ssg_logoutlist.html', di = di)

@app.route('/list', methods = ['GET'])
def display_time_in_data():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl WHERE event = %s", (event,))
	dis = cur.fetchall()
	return render_template('list.html', dis = dis)

@app.route('/list3', methods = ['GET'])
def display_time_in_datassg():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl WHERE event = %s", (event,))
	list = cur.fetchall()
	return render_template('list3.html', list = list)

@app.route('/ssg_login_list', methods = ['GET'])
def ssg_login_list():
	event = request.args.get('event')
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM attendance_tbl WHERE event = %s", (event,))
	dis = cur.fetchall()
	return render_template('ssg_loginlist.html', dis = dis)

@app.route('/delete_process1/<string:id>/')
def delete_process1(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM attendance_tbl WHERE id = '{}'".format(id))
	conn.commit()
	return redirect(url_for('event'))

@app.route('/delete_arc/<string:id_arc>/')
def delete_arc(id_arc):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM event_arc WHERE id_arc = '{}'".format(id_arc))
	conn.commit()
	return redirect(url_for('event_archive'))

@app.route('/update3', methods=['GET', 'POST'])
def update3():
	if request.method == "POST":
		id = request.form['id']
		usn = request.form['usn']
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
		conn = connection()
		cur = conn.cursor()
		cur.execute("UPDATE attendance_tbl SET usn = '{}', datetime = '{}' WHERE id = '{}'".format(usn,current_time,id))
		conn.commit()
		return redirect(url_for('list'))

@app.route('/update4/<string:id>/')
def update4(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM attendance_tbl WHERE id = '{}'".format(id))
	dis = cur.fetchone()
	return render_template('update.html', dis = dis)

@app.route('/ADD')
def ADDmin():
     return render_template('ADDmin.html')

@app.route('/insert')
def insert(): 
    return render_template('insert.html')

@app.route('/delete_process/<string:id>/')
def delete_process(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM student_info WHERE ID = '{}'".format(id))
	conn.commit()
	return redirect(url_for('view'))

@app.route('/delete_process9/<string:id>/')
def delete_process9(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM event_tbl WHERE ID = '{}'".format(id))
	conn.commit()
	return redirect(url_for('ssgeventlist'))

@app.route('/delete_process5/<string:id>/')
def delete_process5(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM attendance_tbl_out WHERE ID = '{}'".format(id))
	conn.commit()
	return redirect(url_for('logout_list'))

@app.route('/update1/<string:id>/')
def update1(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM student_info WHERE ID = '{}'".format(id))
	data = cur.fetchone()
	return render_template('display_user.html', data = data)

@app.route('/update2', methods=['GET', 'POST'])
def update2():
	if request.method == "POST":
		id = request.form['id']
		fname = request.form['fname']
		mname = request.form['mname']
		lname = request.form['lname']
		email = request.form['email']
		department = request.form['department']
		conn = connection()
		cur = conn.cursor()
		cur.execute("UPDATE student_info SET fname = '{}', mname = '{}', lname = '{}', email = '{}', department = '{}' WHERE ID ='{}'".format(fname,mname,lname,email,department,id))
		conn.commit()
		return redirect(url_for('view'))

@app.route('/view')
def view():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM student_info")
	dat = cur.fetchall()	
	return render_template('view.html', data = dat)

@app.route('/get_events1')
def get_events1():
    Connect = connection()
    cur = Connect.cursor()
    cur.execute("SELECT id, event FROM event_tbl")
    events = [{'id': row[0], 'event': row[1]} for row in cur.fetchall()]
    cur.close()
    Connect.close()
    return jsonify(events)

@app.route('/get_events')
def get_events():
    Connect = connection()
    cur = Connect.cursor()
    cur.execute("SELECT id, event FROM event_tbl")
    events = [{'id': row[0], 'event': row[1]} for row in cur.fetchall()]
    cur.close()
    Connect.close()
    return jsonify(events)

@app.route('/adminlist')
def adminlist():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute("SELECT * FROM admin")
	yan = cur.fetchall()	
	return render_template('adminlist.html', yan = yan)

@app.route('/update5/<string:id>/')
def update5(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM admin WHERE ID = '{}'".format(id))
	yan = cur.fetchone()
	return render_template('update_admin.html', yan = yan)

@app.route('/delete_process2/<string:id>/')
def delete_process2(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM admin WHERE ID = '{}'".format(id))
	conn.commit()
	return redirect(url_for('adminlist'))

@app.route('/update6', methods=['GET', 'POST'])
def update6():
	if request.method == "POST":
		id = request.form['id']
		username = request.form['username']
		password = request.form['password']
		usertype = request.form['usertype']
		conn = connection()
		cur = conn.cursor()
		cur.execute("UPDATE admin SET username = '{}', password = '{}', usertype = '{}' WHERE ID ='{}'".format(username,password,usertype,id))
		conn.commit()
		return redirect(url_for('adminlist'))

@app.route('/update7/<string:id>/')
def update7(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM event_tbl WHERE ID = '{}'".format(id))
	da = cur.fetchone()
	return render_template('update_event.html', da = da)

@app.route('/update12/<string:id>/')
def update12(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM event_tbl WHERE ID = '{}'".format(id))
	dt = cur.fetchone()
	return render_template('update_ssg_event.html', dt = dt)

@app.route('/update11', methods=['GET', 'POST'])
def update11():
	if request.method == "POST":
		id = request.form['id']
		event = request.form['event']
		date_start = request.form['start']
		date_end = request.form['end']
		status = request.form['status']
		conn = connection()
		cur = conn.cursor()
		cur.execute("UPDATE event_tbl SET event = '{}', date_start = '{}', date_end = '{}', status = '{}' WHERE id ='{}'".format(event,date_start,date_end,status,id))
		conn.commit()
		return redirect(url_for('ssgeventlist'))

@app.route('/update8', methods=['GET', 'POST'])
def update8():
    if request.method == "POST":
        id = request.form['id']
        event = request.form['event']
        date_start = request.form['start']
        date_end = request.form['end']
        status = request.form['status']
        timestart = request.form['timestart']
        timeend = request.form['timeend']
        eventinfo = request.form['eventinfo']
        conn = connection()
        cur = conn.cursor()
        cur.execute("UPDATE event_tbl SET event = '{}', date_start = '{}', date_end = '{}', status = '{}', timestart = '{}', timeend = '{}', eventinfo = '{}' WHERE id ='{}'".format(event, date_start, date_end, status, timestart, timeend, eventinfo, id))
        conn.commit()
        return redirect(url_for('event'))


@app.route('/update9/<string:id>/')
def update9(id):
	conn = connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM attendance_tbl_out WHERE ID = '{}'".format(id))
	di = cur.fetchone()
	return render_template('update_att.html', di = di)

@app.route('/update10', methods=['GET', 'POST'])
def update10():
	if request.method == "POST":
		id = request.form['id']
		usn = request.form['usn']
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M:')
		conn = connection()
		cur = conn.cursor()
		cur.execute("UPDATE attendance_tbl_out SET usn = '{}', datetime = '{}' WHERE id = '{}'".format(usn, current_time, id))
		conn.commit()
		return redirect(url_for('logout_list'))

# Route to save scanned data
@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        data = request.get_json()
        usn = data.get('usn')
        fullname = data.get('fullname')
        event = data.get('event')
        department = data.get('department')
        if usn in last_scan_time and (datetime.now() - last_scan_time[usn]) < timedelta(minutes=30):
            return jsonify({"error": "Cannot scan the same QR code within 30 minutes."})
        conn = MySQLdb.connect(host="localhost", user="root", password="", db="attendance_db")
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %p')
        sql = "INSERT INTO attendance_tbl (usn,fullname,event,department,datetime) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql, (usn, fullname, event, department, current_time))
        conn.commit()
        cursor.close()
        conn.close()
    # Update the last scan time for the QR code
        last_scan_time[usn] = datetime.now()
        return jsonify({"message": "Data saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})@app.route('/save_data_out', methods=['POST'])
@app.route('/save_data_out', methods=['POST'])
def save_data_out():
    try:
        data = request.get_json()
        usn = data.get('usn')
        fullname = data.get('fullname')
        event = data.get('event')
        department = data.get('department')
        # Check if the QR code has been scanned within the last 30 minutes
        if usn in last_scan_time and (datetime.now() - last_scan_time[usn]) < timedelta(minutes=30):
            return jsonify({"error": "Cannot scan the same QR code within 30 minutes."})
        conn = MySQLdb.connect(host="localhost", user="root", password="", db="attendance_db")
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %p')
        sql = "INSERT INTO attendance_tbl_out (usn,fullname,event,department,datetime) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql, (usn, fullname, event, department, current_time))
        conn.commit()
        cursor.close()
        conn.close()
        last_scan_time[usn] = datetime.now()
        return jsonify({"message": "Data saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})@app.route('/save_data_out', methods=['POST'])
    
@app.route('/event_archive')
def event_archive():
	Connect = connection()
	cur = Connect.cursor()
	cur.execute('SELECT * FROM event_arc')
	arc = cur.fetchall()
	return render_template('eventarc.html', arc = arc)

@app.route('/delete_process4/<string:id>/')
def delete_process4(id):
    Connect = connection()
    cur = Connect.cursor()
    cur.execute('SELECT * FROM event_tbl WHERE id = %s', (id,))
    deleted_event = cur.fetchone()
    cur.execute('DELETE FROM event_tbl WHERE id = %s', (id,))
    Connect.commit()
    cur.execute('INSERT INTO event_arc (eventname, eventinfo, datestart, dateend, timestart, timeend, status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (deleted_event[1], deleted_event[7], deleted_event[2], deleted_event[3], deleted_event[5], deleted_event[6], 'Inactive'))
    Connect.commit()
    return redirect(url_for('event_archive'))


if __name__ == '__main__':
	app.run(debug = True)