import random


class RoomEnvironment:
    ACTIONS = ["HEAT", "COOL", "FAN", "IDLE"]

    def __init__(self):
        self.reset()

    def reset(self, temperature=19.0, target=24.0):
        self.temperature = float(temperature)
        self.target = float(target)
        self.energy = 0.0
        self.step = 0
        self.outside = 29.0
        self.disturbance = "Stable"

    def observe(self):
        return {
            "temperature": round(self.temperature, 2),
            "target": round(self.target, 2),
            "outside": round(self.outside, 2),
            "energy": round(self.energy, 2),
            "step": self.step,
            "disturbance": self.disturbance
        }

    def tick(self, action):
        effects = {
            "HEAT": 0.95,
            "COOL": -0.95,
            "FAN": -0.20,
            "IDLE": 0.0
        }

        costs = {
            "HEAT": 4.0,
            "COOL": 4.0,
            "FAN": 1.0,
            "IDLE": 0.0
        }

        action = action if action in effects else "IDLE"
        before = self.temperature

        # The outside environment slowly pulls the room temperature.
        outside_effect = (self.outside - self.temperature) * 0.018

        # Occasional disturbances make the environment less predictable.
        if self.step > 0 and self.step % 13 == 0:
            disturbance = random.choice([
                ("Door opened", 0.65),
                ("Sunlight increased", 0.45),
                ("Window opened", -0.55),
                ("Stable", 0.0)
            ])
            self.disturbance = disturbance[0]
            disturbance_value = disturbance[1]
        else:
            self.disturbance = "Stable"
            disturbance_value = 0.0

        noise = random.uniform(-0.045, 0.045)

        self.temperature += (
            effects[action]
            + outside_effect
            + disturbance_value
            + noise
        )

        self.energy += costs[action]
        self.step += 1

        return {
            "before": round(before, 2),
            "after": round(self.temperature, 2),
            "change": round(self.temperature - before, 2),
            "energy": costs[action],
            "action": action,
            "disturbance": self.disturbance,
            "state": self.observe()
        }
