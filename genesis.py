# SWAMI KARUPPASWAMI THUNNAI

import secrets
from flask import Flask
from flask import redirect
from hospital_erp.hospital_blueprint import hospital, url_for
from hospital_erp.doctor_blueprint import doctor
from hospital_erp.pharmacy_blueprint import pharmacy
from flask_toastr import Toastr

app = Flask(__name__)
toastr = Toastr(app)
app.secret_key = "TEMPKEYFORTESTING"
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 7}

app.register_blueprint(hospital)
app.register_blueprint(doctor)
app.register_blueprint(pharmacy)




if __name__ == "__main__":
    app.run(debug=True)
