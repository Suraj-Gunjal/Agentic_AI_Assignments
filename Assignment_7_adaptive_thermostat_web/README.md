# ThermoMind — Adaptive Smart Thermostat Learning Agent

A browser-based Agentic AI assignment demonstrating a simple **Learning Agent**
that maintains a target temperature while learning from environmental feedback
and considering energy consumption.

## Why this is Agentic AI

The system follows:

```text
PERCEIVE
   ↓
OBSERVE CURRENT TEMPERATURE
   ↓
DECIDE ACTION
   ↓
HEAT / COOL / FAN / IDLE
   ↓
ENVIRONMENT CHANGES
   ↓
MEASURE RESULT + ENERGY
   ↓
CALCULATE REWARD
   ↓
UPDATE LEARNED KNOWLEDGE
   ↓
NEXT DECISION
```

The agent does not permanently assume the effect of an action. It estimates
the average temperature change and energy cost from actual simulation results.

## Features

- Modern responsive browser UI
- Flask backend
- Learning thermostat agent
- Simulated room environment
- Heater / cooler / fan / idle actions
- Target temperature control
- Live automatic simulation
- Step-by-step simulation
- Manual experiment mode
- Temperature trajectory chart
- Agent decision panel
- Confidence score
- Explainable decision reason
- Reward tracking
- Success rate
- Energy usage
- Learned action knowledge
- Environmental disturbances
- Reset and target controls

## Run on Windows

Open PowerShell inside the project folder.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Recommended demo

1. Open the browser dashboard.
2. Set target to 24°C.
3. Click **Run agent**.
4. Watch the room temperature approach the target.
5. Observe the agent decision panel.
6. Observe the learned action knowledge increasing.
7. Use manual Heat/Cool/Fan controls.
8. Let the agent continue and observe how it uses the new experience.
9. Change target to 26°C.
10. Demonstrate adaptation.

## Viva explanation

"This project implements a learning agent for temperature control. The agent
perceives the current room temperature and compares it with the target. It
selects an action such as heating, cooling, fan or idle. After the environment
changes, it receives feedback in the form of temperature change, energy usage
and reward. It updates its learned model using that experience and uses the
updated model for future decisions."

## Difference from a simple thermostat

A simple thermostat might always use a fixed rule:

```python
if temperature < target:
    heat()
```

ThermoMind instead learns:

```text
Observation
    ↓
Action selection
    ↓
Environment response
    ↓
Feedback
    ↓
Knowledge update
    ↓
Improved action selection
```

That learning feedback loop is the main Agentic AI concept demonstrated here.

## Project structure

```text
adaptive_thermostat_web/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── environment.py
│   └── routes.py
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
├── requirements.txt
├── run.py
└── README.md
```
