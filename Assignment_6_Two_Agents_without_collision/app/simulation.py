from collections import deque


class Delivery:
    def __init__(self, delivery_id, pickup, destination, priority, item):
        self.id = delivery_id
        self.pickup = pickup
        self.destination = destination
        self.priority = priority
        self.item = item
        self.status = "pending"
        self.assigned_to = None
        self.phase = "pickup"

    def as_dict(self):
        return {
            "id": self.id,
            "pickup": self.pickup,
            "destination": self.destination,
            "priority": self.priority,
            "item": self.item,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "phase": self.phase
        }


class Robot:
    def __init__(self, robot_id, name, x, y):
        self.id = robot_id
        self.name = name
        self.x = x
        self.y = y
        self.delivery_id = None
        self.status = "idle"
        self.action = "WAIT"
        self.reason = "Waiting for a delivery."
        self.completed = 0
        self.moves = 0
        self.safe_waits = 0

    def position(self):
        return self.x, self.y

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "delivery_id": self.delivery_id,
            "status": self.status,
            "action": self.action,
            "reason": self.reason,
            "completed": self.completed,
            "moves": self.moves,
            "safe_waits": self.safe_waits
        }


class HospitalEnvironment:
    def __init__(self):
        self.width = 13
        self.height = 9
        self.reset()

    def reset(self):
        self.tick = 0
        self.completed = 0
        self.waits = 0

        self.rooms = {
            (0, 4): "Pharmacy",
            (12, 2): "ICU",
            (11, 7): "Lab",
            (1, 1): "Ward A",
            (8, 1): "Ward B",
            (5, 7): "Emergency"
        }

        self.obstacles = {
            (3, 0), (3, 1), (3, 2),
            (3, 6), (3, 7), (3, 8),
            (7, 0), (7, 1), (7, 2),
            (7, 6), (7, 7), (7, 8),
            (9, 4), (10, 4), (11, 4)
        }

        self.robots = [
            Robot("R1", "Atlas", 0, 8),
            Robot("R2", "Nova", 12, 8)
        ]

        self.deliveries = [
            Delivery("D-101", (0, 4), (12, 2), 3, "Urgent medicine"),
            Delivery("D-102", (0, 4), (1, 1), 2, "Patient medication"),
            Delivery("D-103", (0, 4), (11, 7), 3, "Blood sample"),
            Delivery("D-104", (0, 4), (8, 1), 2, "Medical supplies"),
            Delivery("D-105", (0, 4), (5, 7), 1, "Routine supplies"),
            Delivery("D-106", (0, 4), (12, 2), 2, "Lab report")
        ]

    def valid(self, x, y):
        return (
            0 <= x < self.width
            and 0 <= y < self.height
            and (x, y) not in self.obstacles
        )

    def neighbors(self, position):
        x, y = position
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.valid(nx, ny):
                yield nx, ny

    def shortest_path(self, start, goal, blocked):
        if start == goal:
            return []

        queue = deque([start])
        previous = {start: None}

        while queue:
            current = queue.popleft()

            for nxt in self.neighbors(current):
                if nxt in previous:
                    continue
                if nxt in blocked and nxt != goal:
                    continue

                previous[nxt] = current

                if nxt == goal:
                    path = []
                    node = nxt

                    while node != start:
                        path.append(node)
                        node = previous[node]

                    path.reverse()
                    return path

                queue.append(nxt)

        return []

    def delivery_for(self, robot):
        return next(
            (d for d in self.deliveries if d.id == robot.delivery_id),
            None
        )

    def assign_deliveries(self):
        pending = [
            d for d in self.deliveries
            if d.status == "pending"
        ]

        idle = [
            r for r in self.robots
            if r.delivery_id is None
        ]

        for robot in idle:
            if not pending:
                return

            ranked = []

            for delivery in pending:
                distance = (
                    abs(robot.x - delivery.pickup[0])
                    + abs(robot.y - delivery.pickup[1])
                )

                score = distance - delivery.priority * 3
                ranked.append((score, distance, delivery))

            ranked.sort(key=lambda item: (item[0], item[1]))

            delivery = ranked[0][2]
            delivery.status = "assigned"
            delivery.assigned_to = robot.id
            delivery.phase = "pickup"

            robot.delivery_id = delivery.id
            robot.status = "moving"
            robot.action = "ASSIGNED"
            robot.reason = (
                f"Assigned {delivery.id}: "
                f"{delivery.item}."
            )

            pending.remove(delivery)

    def step(self):
        self.tick += 1
        self.assign_deliveries()

        proposals = {}
        reserved = set()

        for index, robot in enumerate(self.robots):
            other = self.robots[1 - index]
            delivery = self.delivery_for(robot)

            if not delivery:
                robot.status = "idle"
                robot.action = "WAIT"
                robot.reason = "Waiting for the next delivery."
                proposals[robot.id] = robot.position()
                continue

            goal = (
                delivery.pickup
                if delivery.phase == "pickup"
                else delivery.destination
            )

            path = self.shortest_path(
                robot.position(),
                goal,
                {other.position(), *reserved}
            )

            if not path:
                proposals[robot.id] = robot.position()
                robot.status = "waiting"
                robot.action = "WAIT"
                robot.safe_waits += 1
                self.waits += 1
                robot.reason = (
                    "Route blocked. Waiting to avoid a collision."
                )
                continue

            next_cell = path[0]

            if next_cell == other.position() or next_cell in reserved:
                proposals[robot.id] = robot.position()
                robot.status = "waiting"
                robot.action = "WAIT"
                robot.safe_waits += 1
                self.waits += 1
                robot.reason = (
                    "Another robot has priority for this cell. "
                    "Yielding safely."
                )
                continue

            proposals[robot.id] = next_cell

            dx = next_cell[0] - robot.x
            dy = next_cell[1] - robot.y

            if dx > 0:
                robot.action = "RIGHT"
            elif dx < 0:
                robot.action = "LEFT"
            elif dy > 0:
                robot.action = "DOWN"
            else:
                robot.action = "UP"

            robot.status = "moving"
            robot.reason = (
                f"Moving to {delivery.phase} point for {delivery.id}."
            )
            reserved.add(next_cell)

        current_positions = {
            robot.id: robot.position()
            for robot in self.robots
        }

        for robot in self.robots:
            target = proposals[robot.id]
            other_id = "R2" if robot.id == "R1" else "R1"

            if target == current_positions[other_id]:
                target = robot.position()
                robot.action = "WAIT"
                robot.status = "waiting"
                robot.safe_waits += 1
                self.waits += 1
                robot.reason = "Collision prevented by safety rule."

            if target != robot.position():
                robot.x, robot.y = target
                robot.moves += 1

            delivery = self.delivery_for(robot)

            if not delivery:
                continue

            goal = (
                delivery.pickup
                if delivery.phase == "pickup"
                else delivery.destination
            )

            if robot.position() == goal:
                if delivery.phase == "pickup":
                    delivery.phase = "delivery"
                    robot.action = "PICKED"
                    robot.reason = (
                        f"Picked up {delivery.item}. "
                        "Heading to destination."
                    )
                else:
                    delivery.status = "completed"
                    robot.completed += 1
                    self.completed += 1
                    robot.delivery_id = None
                    robot.status = "idle"
                    robot.action = "DELIVERED"
                    robot.reason = (
                        f"{delivery.id} delivered successfully."
                    )

        if self.completed == len(self.deliveries):
            for robot in self.robots:
                robot.status = "complete"
                robot.action = "DONE"
                robot.reason = "All hospital deliveries completed."

        return self.snapshot()

    def manual(self, robot_id, action):
        robot = next(
            (r for r in self.robots if r.id == robot_id),
            None
        )

        if not robot:
            return self.snapshot()

        moves = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0)
        }

        if action == "WAIT":
            robot.action = "WAIT"
            robot.safe_waits += 1
            robot.reason = "Manual wait selected."
            return self.snapshot()

        dx, dy = moves.get(action, (0, 0))
        target = (robot.x + dx, robot.y + dy)

        other = self.robots[1] if robot.id == "R1" else self.robots[0]

        if not self.valid(*target) or target == other.position():
            robot.action = "WAIT"
            robot.safe_waits += 1
            self.waits += 1
            robot.reason = (
                "Move rejected by collision-safety rule."
            )
            return self.snapshot()

        robot.x, robot.y = target
        robot.moves += 1
        robot.action = action
        robot.reason = "Manual movement accepted."
        self.tick += 1

        return self.snapshot()

    def snapshot(self):
        return {
            "width": self.width,
            "height": self.height,
            "tick": self.tick,
            "completed": self.completed,
            "total_deliveries": len(self.deliveries),
            "waits": self.waits,
            "rooms": [
                {"x": x, "y": y, "name": name}
                for (x, y), name in self.rooms.items()
            ],
            "obstacles": [
                {"x": x, "y": y}
                for x, y in self.obstacles
            ],
            "robots": [
                robot.as_dict()
                for robot in self.robots
            ],
            "deliveries": [
                delivery.as_dict()
                for delivery in self.deliveries
            ]
        }
