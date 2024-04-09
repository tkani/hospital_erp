# SWAMI KARUPPASWAMI THUNNAI
from flask import request, redirect, url_for, session,flash
from flask import render_template
from flask import Blueprint
import json
from database.get_connection import get_connection
from hospital_erp.token_validator import reception_token,doctor_token
from datetime import date, timedelta,datetime

import hashlib


#===============================================================================# Starts #========================================  
doctor = Blueprint("doctor", __name__, url_prefix="/")

today=date.today()
last_change =datetime.now()

# #===============================================================================# patient view #========================================  

@doctor.route("/patient_info", methods=["POST","GET"])
@doctor_token
def patient_info():
	connection = get_connection()
	cursor = connection.cursor()

	cursor.execute("SELECT * from ticket_counter,patient where patient.id = ticket_counter.patient_id and ticket_counter.admission_date>=%s and ticket_counter.consulted=0 ORDER BY ticket_counter.admission_date ASC",(today))
	patient_data=cursor.fetchall()

	cursor.execute("SELECT * from ticket_counter,patient where patient.id = ticket_counter.patient_id and ticket_counter.admission_date>=%s and ticket_counter.consulted=1 ORDER BY ticket_counter.admission_date ASC",(today))
	next_patient_data=cursor.fetchall()

	return render_template('hospital_template/patient_list.html',role=session['hospital_id'][3],patient_data=patient_data,next_patient_data=next_patient_data,last_change=last_change)

# #===============================================================================# patient view #========================================  

@doctor.route("/patient_id/<int:id>", methods=["POST","GET"])
@doctor_token
def patient_id(id):
	try:
		connection = get_connection()
		cursor = connection.cursor()

		if request.method=="POST":
			cursor.execute("SELECT * from patient,ticket_counter where patient.id = ticket_counter.patient_id and ticket_counter.admission_date>=%s and ticket_counter.consulted=0 ORDER BY ticket_counter.admission_date ASC",(today))
			next_patient_data=cursor.fetchone()

			cursor.execute("SELECT * from ticket_counter where ticket_counter.patient_id=%s and ticket_counter.admission_date>=%s and ticket_counter.consulted=1",(id,today))
			ticket_data=cursor.fetchone()

			rowcount = request.form["rowcount"]
			weight = request.form["weight"]
			height = request.form["height"]
			spo2 = request.form["spo2"]
			nadi = request.form["Nadi"]
			temperature = request.form["temperature"]
			bp = request.form["bp"]
			description = request.form["description"]
			food_restrictions = request.form["food_restrictions"]
			drug_allergy = request.form["drug_allergy"]
			family_history = request.form["family_history"]
			present_complaint = request.form["present_complaint"]
			diagnosis = request.form["diagnosis"]
			therapy = request.form["therapy"]
			medicines = request.form["medicines"]
			if weight=="":
				weight=None
			if height=="":
				height=None
			if spo2=="":
				spo2=None
			if nadi=="":
				nadi=None
			if temperature=="":
				temperature=None
			if bp=="":
				bp=None
			if description=="":
				description=None
			if food_restrictions=="":
				food_restrictions=None
			if drug_allergy=="":
				drug_allergy=None
			if family_history=="":
				family_history=None
			if present_complaint=="":
				present_complaint=None
			if diagnosis=="":
				diagnosis=None
			if therapy=="":
				therapy=None
			if medicines=="":
				medicines=None
			medicine_data=[]
			
			for i in range(0, int(rowcount)):
				try:
					medicinename = request.form["medicinename_"+str(i)]
					morning = request.form["morning_" + str(i)]
					evening = request.form["evening_" + str(i)]
					night = request.form["night_" + str(i)]
					medicine_data.append({"medicinename":medicinename,"morning":morning,"evening":evening,"night":night})
				except Exception as e:
					# print("******************",e)
					i+=1

			info_data = json.dumps({"medicine_data": medicine_data})

			cursor.execute("INSERT into prescription value(null,%s,%s,%s,%s,%s)",(id,info_data,description,session['hospital_id'][0],last_change))
			connection.commit()
			
			cursor.execute("UPDATE patient set drug_allergy=%s, family_history=%s where id=%s",(drug_allergy,family_history,id))
			connection.commit()

			cursor.execute("UPDATE ticket_counter set nadi=%s, patient_height=%s, patient_weight=%s, patient_temperature=%s, spo2=%s, bp=%s, consulted=3, food_restrictions=%s, present_complaint=%s, diagnosis=%s, therapy=%s, medicines=%s  where id=%s",(nadi,height,weight,temperature,spo2,bp,food_restrictions,present_complaint,diagnosis,therapy,medicines,ticket_data['id']))
			connection.commit()

			flash("Medicine details moved to pharmacy")
			if next_patient_data!=None:
				return redirect(url_for("doctor.patient_id",id=next_patient_data["id"]))
			else:
				return redirect(url_for("doctor.patient_info"))

		cursor.execute("SELECT * from patient where patient.id = %s",(id))
		patient_data=cursor.fetchone()

		cursor.execute("SELECT * from patient,ticket_counter where patient.id = ticket_counter.patient_id and ticket_counter.admission_date>=%s and ticket_counter.consulted=0 ORDER BY ticket_counter.admission_date ASC",(today))
		next_patient_data=cursor.fetchone()

		cursor.execute("UPDATE ticket_counter set consulted=1 where consulted=0 and patient_id=%s and admission_date>=%s",(id,today))
		connection.commit()

		cursor.execute("UPDATE ticket_counter set consulted=0 where patient_id!=%s and consulted=1",(id))
		connection.commit()

		cursor.execute("SELECT * from ticket_counter where ticket_counter.patient_id=%s ORDER BY ticket_counter.id desc",(id))
		ticket_data=cursor.fetchall()

		cursor.execute("SELECT * from prescription where patient_id=%s ORDER BY created_on DESC",(id))
		prescription_data=cursor.fetchall()
		parsed_data = []

		for i in prescription_data:
			# Use json.loads() to parse the string into a dictionary
			data_dict = json.loads(i['info'])
			# Append the parsed dictionary to the list
			i['info']=data_dict

		cursor.execute("SELECT * from medicine")
		medicine_list=cursor.fetchall()
		print(patient_data)
		age_=calculate_age(patient_data['dob'],today)
		# print(age_)
		# return render_template('hospital_template/pages-error-404.html')
		return render_template('hospital_template/doctor_patient.html',prescription_data=prescription_data,medicine_list=medicine_list,role=session['hospital_id'][3],patient_data=patient_data,ticket_data=ticket_data,next_patient_data=next_patient_data,last_change=last_change,age_=age_)
	except Exception as e:
		print(e)
		cursor.close()
		connection.close()
	
def calculate_age(birthdate, current_date):
	birthdate = datetime.strptime(str(birthdate), "%Y-%m-%d")
	current_date = datetime.strptime(str(current_date), "%Y-%m-%d")
	age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
	return age
