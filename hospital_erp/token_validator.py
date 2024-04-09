# SWAMI KARUPPASWAMI THUNNAI

from functools import wraps
from flask import session, redirect
from database.get_connection import get_connection


def reception_token(_function):

    @wraps(_function)
    def wrapper_function(*args, **kwargs):
        if "hospital_id" in session:
            if "hospital_id" in session:
                if session['hospital_id'][3]=='receptionist':
                    return _function(*args, **kwargs)
                else:
                    return redirect("/error_page")

        else:
            return redirect("/")
    return wrapper_function

def doctor_token(_function):

    @wraps(_function)
    def wrapper_function(*args, **kwargs):
        if "hospital_id" in session:
            if session['hospital_id'][3]=='doctor':
                    return _function(*args, **kwargs)
            else:
                    return redirect("/error_page")
        else:
            return redirect("/")
    return wrapper_function

def pharmacy_token(_function):

    @wraps(_function)
    def wrapper_function(*args, **kwargs):
        if "hospital_id" in session:
            if session['hospital_id'][3]=='pharmacy':
                    return _function(*args, **kwargs)
            else:
                    return redirect("/error_page")
        else:
            return redirect("/")
    return wrapper_function