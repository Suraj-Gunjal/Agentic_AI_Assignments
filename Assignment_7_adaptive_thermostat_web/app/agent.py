class LearningThermostatAgent:
    ACTIONS = ["HEAT", "COOL", "FAN", "IDLE"]

    def __init__(self):
        self.reset()

    def reset(self):
        self.knowledge = {
            action: {
                "samples": 0,
                "avg_change": 0.0,
                "avg_energy": 0.0
            }
            for action in self.ACTIONS
        }
        self.steps = 0
        self.total_reward = 0.0
        self.successes = 0
        self.history = []
        self.last_decision = {
            "action": "IDLE",
            "confidence": 0,
            "reason": "Waiting for an observation.",
            "error": 0
        }

    def choose_action(self, current, target):
        error = target - current

        if abs(error) <= 0.35:
            preferred = ["IDLE", "FAN", "HEAT", "COOL"]
        elif error > 0:
            preferred = ["HEAT", "FAN", "IDLE", "COOL"]
        else:
            preferred = ["COOL", "FAN", "IDLE", "HEAT"]

        unexplored = [
            a for a in preferred
            if self.knowledge[a]["samples"] < 3
        ]

        if unexplored:
            action = unexplored[0]
            reason = "Exploring an action so the agent can learn its effect."
            confidence = 42
        else:
            desired = max(-1.0, min(1.0, error))
            scores = {}

            for action in preferred:
                data = self.knowledge[action]
                change_error = abs(desired - data["avg_change"])
                energy_penalty = data["avg_energy"] * 0.07

                # Small preference for the direction that closes the error.
                direction_penalty = 0
                if error > 0 and action == "COOL":
                    direction_penalty = 1.5
                if error < 0 and action == "HEAT":
                    direction_penalty = 1.5

                scores[action] = (
                    change_error
                    + energy_penalty
                    + direction_penalty
                )

            action = min(scores, key=scores.get)

            if abs(error) <= 0.35:
                reason = "Temperature is inside the comfort band, so the agent saves energy."
            elif error > 0:
                reason = "Room is below target, so the learned model prefers heating."
            else:
                reason = "Room is above target, so the learned model prefers cooling."

            confidence = min(
                96,
                58 + self.knowledge[action]["samples"] * 2
            )

        self.last_decision = {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "error": round(error, 2)
        }
        return action

    def learn(self, action, before, after, energy, target):
        change = after - before
        distance = abs(target - after)

        if distance <= 0.35:
            reward = 10.0
            self.successes += 1
        elif distance <= 1.0:
            reward = 5.0
        elif distance <= 2.0:
            reward = 1.0
        else:
            reward = -distance

        reward -= energy * 0.08

        data = self.knowledge[action]
        n = data["samples"] + 1

        data["avg_change"] = (
            (data["avg_change"] * data["samples"]) + change
        ) / n

        data["avg_energy"] = (
            (data["avg_energy"] * data["samples"]) + energy
        ) / n

        data["samples"] = n

        self.steps += 1
        self.total_reward += reward

        self.history.append({
            "step": self.steps,
            "temperature": round(after, 2),
            "action": action,
            "reward": round(reward, 2)
        })

        self.history = self.history[-80:]

        return round(reward, 2)

    def stats(self):
        return {
            "steps": self.steps,
            "reward": round(self.total_reward, 2),
            "successes": self.successes,
            "success_rate": round(
                self.successes / self.steps * 100, 1
            ) if self.steps else 0
        }
