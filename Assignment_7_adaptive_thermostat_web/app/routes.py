from flask import Blueprint, jsonify, render_template, request
from .agent import LearningThermostatAgent
from .environment import RoomEnvironment

api = Blueprint("api", __name__)

agent = LearningThermostatAgent()
environment = RoomEnvironment()


def snapshot():
    return {
        "environment": environment.observe(),
        "agent": {
            "decision": agent.last_decision,
            "stats": agent.stats(),
            "knowledge": agent.knowledge
        },
        "history": agent.history
    }


@api.get("/")
def index():
    return render_template("index.html")


@api.get("/api/state")
def state():
    return jsonify(snapshot())


@api.post("/api/reset")
def reset():
    data = request.get_json(silent=True) or {}
    target = float(data.get("target", 24))
    temperature = float(data.get("temperature", 19))

    target = max(10, min(35, target))
    temperature = max(5, min(45, temperature))

    agent.reset()
    environment.reset(
        temperature=temperature,
        target=target
    )

    return jsonify(snapshot())


@api.post("/api/target")
def target():
    data = request.get_json(silent=True) or {}
    value = float(data.get("target", 24))
    environment.target = max(10, min(35, value))
    return jsonify(snapshot())


@api.post("/api/step")
def step():
    action = agent.choose_action(
        environment.temperature,
        environment.target
    )

    result = environment.tick(action)

    reward = agent.learn(
        action=action,
        before=result["before"],
        after=result["after"],
        energy=result["energy"],
        target=environment.target
    )

    data = snapshot()
    data["last"] = {
        "action": action,
        "reward": reward,
        "before": result["before"],
        "after": result["after"],
        "change": result["change"],
        "disturbance": result["disturbance"]
    }

    return jsonify(data)


@api.post("/api/manual")
def manual():
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "IDLE")).upper()

    if action not in environment.ACTIONS:
        return jsonify({"error": "Invalid action"}), 400

    before = environment.temperature
    result = environment.tick(action)

    reward = agent.learn(
        action=action,
        before=before,
        after=result["after"],
        energy=result["energy"],
        target=environment.target
    )

    return jsonify({
        **snapshot(),
        "last": {
            "action": action,
            "reward": reward,
            "before": result["before"],
            "after": result["after"],
            "change": result["change"],
            "disturbance": result["disturbance"]
        }
    })
