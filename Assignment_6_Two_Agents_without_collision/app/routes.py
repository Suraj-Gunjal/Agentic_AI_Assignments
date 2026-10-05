from flask import Blueprint, jsonify, render_template, request
from .simulation import HospitalEnvironment

api = Blueprint("api", __name__)
environment = HospitalEnvironment()


@api.get("/")
def index():
    return render_template("index.html")


@api.get("/api/state")
def state():
    return jsonify(environment.snapshot())


@api.post("/api/reset")
def reset():
    environment.reset()
    return jsonify(environment.snapshot())


@api.post("/api/step")
def step():
    return jsonify(environment.step())


@api.post("/api/manual")
def manual():
    data = request.get_json(silent=True) or {}

    return jsonify(
        environment.manual(
            data.get("robot", "R1"),
            data.get("action", "WAIT")
        )
    )
