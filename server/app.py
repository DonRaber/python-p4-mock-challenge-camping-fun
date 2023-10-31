#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def campers():

    if request.method == 'GET':
        campers = Camper.query.all()

        campers_dict = [camper.to_dict(rules = ('-signups', )) for camper in campers]

        resp = make_response(campers_dict, 200)

    elif request.method == 'POST':
        form_data = request.get_json()

        try:
            new_camper = Camper(
                name = form_data['name'],
                age = form_data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            
            resp = make_response(new_camper.to_dict(), 201)

        except ValueError:
            resp = make_response({'errors':['validation errors']}, 400)
            return resp
        
    return resp

@app.route('/campers/<int:id>', methods = ['GET', 'PATCH'])
def campers_by_id(id):
    camper = Camper.query.filter_by(id = id).first()
    
    if camper == None:
        resp = make_response({'error':'Camper not found'}, 404)
        return resp
    
    elif camper:
        
        if request.method == 'GET':
            camper_dict = camper.to_dict()

            resp = make_response(camper_dict, 200)
        
        elif request.method == 'PATCH':
            form_data = request.get_json()

            try:
                for attr in form_data:
                    setattr(camper, attr, form_data.get(attr))

                db.session.commit()

                resp = make_response(camper.to_dict(), 202)
            
            except ValueError:
                resp = make_response({'errors': ['validation errors']}, 400)
                return resp
    return resp

@app.route('/activities', methods = ['GET'])
def activities():
    activities = Activity.query.all()
    activity_dict = [activity.to_dict(rules = ('-signups',)) for activity in activities]
    resp = make_response(activity_dict, 200)
    return resp

@app.route('/activities/<int:id>', methods = ['DELETE'])
def activities_by_id(id):
    activity = Activity.query.filter_by(id = id).first()

    if activity:
        db.session.delete(activity)
        db.session.commit()
        resp = make_response({}, 204)
    
    else:
        resp = make_response({'error': 'Activity not found'}, 404)

    return resp


@app.route('/signups', methods = ['POST'])
def signups():
    signups = Signup.query.all()

    if request.method == 'POST':
        form_data = request.get_json()

        try:
            new_signup = Signup(
                time = form_data['time'],
                camper_id = form_data['camper_id'],
                activity_id = form_data['activity_id']
            )
            db.session.add(new_signup)
            db.session.commit()
            
            resp = make_response(new_signup.to_dict(), 201)

        except ValueError:
            resp = make_response({'errors':['validation errors']}, 400)
            return resp
        
    return resp



if __name__ == '__main__':
    app.run(port=5555, debug=True)
