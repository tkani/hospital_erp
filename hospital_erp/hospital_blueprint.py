# SWAMI KARUPPASWAMI THUNNAI
from flask import request, redirect, url_for, session,flash
from flask import render_template
from flask import Blueprint
import json
from database.get_connection import get_connection
from hospital_erp.token_validator import reception_token,doctor_token
from datetime import date, timedelta,datetime
from hospital_erp.doctor_blueprint import doctor
from hospital_erp.pharmacy_blueprint import pharmacy

import hashlib


#===============================================================================# Starts #========================================  
hospital = Blueprint("hospital", __name__, url_prefix="/")

today=date.today()
last_change =datetime.now()

#===============================================================================# login  #========================================  
@hospital.route("/<string:role>", methods=["POST","GET"])
def render_login(role):

	connection = get_connection()
	cursor = connection.cursor()

	if request.method=="POST":
		try:		
			email = request.form["email"]
			password = request.form["password"]
			password_hash=password_encryption(password)
			# print(password_hash)
			cursor.execute("SELECT * from hospital_employee where username=%s and password=%s and role=%s ",(email, password_hash, role))
			result = cursor.fetchone()
			
			if result==None:
				flash("Incorrect username and password")
				return redirect(url_for("hospital.render_login"))

			session["hospital_id"] = (result["id"], email, password, role)
			if role=='receptionist':
				return redirect(url_for("hospital.patient"))
			elif role=='doctor':
				return redirect(url_for("doctor.patient_info"))
			elif role=='pharmacy':
				return redirect(url_for("pharmacy.prescription_list"))

		except Exception as e:
			print(e)
			return redirect(url_for("hospital.render_login",role=role))
		finally:
			cursor.close()
			connection.close()
	return render_template("hospital_template/login.html",role=role)


def password_encryption(password):
	salt='hospital$ceo*founder&1337'
	salt=hashlib.sha512(salt.encode("utf-8")).hexdigest()
	# print(password)
	password=password+salt
	password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
	password_hash=salt+password_hash+salt
	password_hash=  hashlib.sha512(password_hash.encode("utf-8")).hexdigest()
	# print(password_hash)
	return password_hash

# #===============================================================================# New patient #========================================  

@hospital.route("/patient", methods=["POST","GET"])
@reception_token
def patient():
	connection = get_connection()
	cursor = connection.cursor()

	data={"patient_details":''}
	if request.method=="POST":
		name = request.form["name"]
		father_name = request.form["father_name"]
		address = request.form["address"]
		phone_number = request.form["phone_number"]
		dob = request.form["dob"]
		gender = request.form["gender"]

		if phone_number=="":
			flash("Enter the mobile number")
			return redirect(url_for('hospital.patient'))
		try:		
			cursor.execute("SELECT * from patient where phone=%s",(phone_number))
			mobile_info = cursor.fetchone()
			if mobile_info!=None:
				flash("Mobile Number Already Registered!!")
			else:
				cursor.execute("INSERT into patient value(null,%s,%s,%s,%s,%s,%s,null,null,%s,%s)",(phone_number,name,father_name,dob,gender,address,session['hospital_id'][0],last_change))
				connection.commit()
				patient_id=cursor.lastrowid
				flash("New Patient ID: " + str(patient_id))
				return redirect(url_for('hospital.patient'))
		except Exception as e:
			print(e)
			flash(str(e))
			return redirect(url_for("hospital.render_login"))
		finally:
			cursor.close()
			connection.close()
	return render_template('hospital_template/patient.html',role=session['hospital_id'][3],data=data,last_change=last_change)

# #===============================================================================# patient Check #========================================  
@hospital.route("/patient_check", methods=["POST","GET"])
@reception_token
def patient_check():
	connection = get_connection()
	cursor = connection.cursor()

	data={"patient_details":''}
	if request.method=="POST":
		patient_id = request.form["name"]
		phone_number = request.form["phone_number"]
		patient_details=None

		if patient_id!="":
			cursor.execute("SELECT * from patient where id=%s",(patient_id))
			patient_details = cursor.fetchone()
			data={"patient_details":patient_details}
			
		if phone_number!="":
			cursor.execute("SELECT * from patient where phone=%s",(phone_number))
			patient_details = cursor.fetchone()
			data={"patient_details":patient_details}

		if patient_details==None:
			flash("Patient Not Registered !!")
		cursor.close()
		connection.close()
	return render_template('hospital_template/patient.html',role=session['hospital_id'][3],data=data,last_change=last_change)

# #===============================================================================# patient appointment booking #========================================  
@hospital.route("/appointment", methods=["POST","GET"])
@reception_token
def appointment():
	connection = get_connection()
	cursor = connection.cursor()

	data={"patient_details":''}
	if request.method=="POST":
		patient_ids = request.form["patient_ids"]
		# print(patient_ids)
		# print(request.form)
		appointment_time = request.form["appointment"]
		weight = request.form["weight"]
		temperature = request.form["temperature"]
		sp02 = request.form["spo2"]
		bp = request.form["bp"]
		height=None
		nadi=None

		if weight == "":
			weight = None
		if sp02 == "":
			sp02 = None
		if temperature == "":
			temperature = None
		if bp == "":
			bp = None
		if patient_ids!="":
			cursor.execute("SELECT * from ticket_counter where patient_id=%s and consulted=0 and admission_date>=%s",(patient_ids,today))
			patient_data=cursor.fetchone()
			if patient_data!=None:
				flash("Already appointment Booked")
				return redirect(url_for('hospital.patient'))

			cursor.execute("INSERT into ticket_counter value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,null,null,null,null,null,%s,%s)",(patient_ids,height,nadi,weight,temperature,sp02,bp,appointment_time,0,session['hospital_id'][0],last_change))
			connection.commit()
			flash("Appointment Booked")
			return redirect(url_for('hospital.patient'))
		else:
			return redirect(url_for('hospital.patient'))

		cursor.close()
		connection.close()
	else:
		return redirect(url_for('hospital.patient'))

# #===============================================================================# patient appointment booking #========================================  
@hospital.route("/livetv", methods=["POST","GET"])
def livetv():
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("SELECT * from ticket_counter,patient where ticket_counter.admission_date>=%s and ticket_counter.consulted=0 and ticket_counter.patient_id=patient.id ORDER BY ticket_counter.admission_date ASC",(today))
	waiting_patiend_list=cursor.fetchall()

	cursor.execute("SELECT * from ticket_counter where admission_date=%s and consulted=1",(today))
	doctor_patient_list=cursor.fetchone()

	# print(waiting_patiend_list)
	# print(doctor_patient_list)
	return render_template('hospital_template/livetv.html',waiting_patiend_list=waiting_patiend_list)
#===============================================================================# error_page #========================================  
@hospital.route("/error_page", methods=["POST","GET"])
def error_page():
	return render_template('hospital_template/pages-error-404.html')

#===============================================================================# logout #========================================  
@hospital.route("/logout", methods=["POST","GET"])
# @reception_token
def logout():
	session.clear()
	return redirect(url_for('hospital.render_login',role="receptionist"))



