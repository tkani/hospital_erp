# SWAMI KARUPPASWAMI THUNNAI
from flask import request, redirect, url_for, session,flash
from flask import render_template
from flask import Blueprint
import json
from database.get_connection import get_connection
from hospital_erp.token_validator import pharmacy_token
from datetime import date, timedelta,datetime

import hashlib


#===============================================================================# Starts #========================================  
pharmacy = Blueprint("pharmacy", __name__, url_prefix="/")

today=date.today()
last_change =datetime.now()

@pharmacy.route("/medicine_add", methods=["POST","GET"])
@pharmacy_token
def medicine_add():
	connection = get_connection()
	cursor = connection.cursor()
	if request.method=="POST":
		medicine_name=request.form['medicine_name']
		medicine_type=request.form['medicine_type']
		manufacturer=request.form['manufacturer']
		description=request.form['description']

		cursor.execute("INSERT into medicine value(null,%s,%s,%s,%s,%s,%s)",(medicine_name,medicine_type,manufacturer,description,session['hospital_id'][0],last_change))
		connection.commit()
		flash("Medicine Added")
		return redirect(url_for("pharmacy.medicine_add"))
	return render_template('hospital_template/medicine_add.html',role=session['hospital_id'][3],last_change=last_change)

@pharmacy.route("/prescription_list", methods=["POST","GET"])
@pharmacy_token
def prescription_list():
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("SELECT * from ticket_counter,patient where ticket_counter.patient_id=patient.id and ticket_counter.consulted=3 and ticket_counter.admission_date>=%s",(today))
	patient_list=cursor.fetchall()
	# print(patient_list)
	return render_template('hospital_template/pharmacy_patient_list.html',role=session['hospital_id'][3],last_change=last_change,patient_list=patient_list)

@pharmacy.route("/prescription/<int:id>/<int:ticket_id>", methods=["POST","GET"])
@pharmacy_token
def prescription(id,ticket_id):
	connection = get_connection()
	cursor = connection.cursor()

	if request.method=="POST":
		cursor.execute("UPDATE ticket_counter set consulted=4 where ticket_counter.id=%s",(ticket_id))
		connection.commit()

		flash("Medicine delivered")
		return redirect(url_for("pharmacy.prescription_list"))
		
	cursor.execute("SELECT * from patient,prescription where patient.id=prescription.patient_id and patient.id=%s",(id))
	patient_data=cursor.fetchone()

	patient_data['info']=json.loads(patient_data['info'])
	return render_template('hospital_template/prescription.html',role=session['hospital_id'][3],last_change=last_change,patient_data=patient_data)
