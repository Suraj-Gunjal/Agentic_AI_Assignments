const state = {
    running: false,
    timer: null
};

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    return response.json();
}

function renderMap(data) {
    const map = document.getElementById("map");
    map.innerHTML = "";

    const obstacles = new Set(
        data.obstacles.map(p => `${p.x},${p.y}`)
    );

    const rooms = Object.fromEntries(
        data.rooms.map(r => [`${r.x},${r.y}`, r])
    );

    const robots = Object.fromEntries(
        data.robots.map(r => [`${r.x},${r.y}`, r])
    );

    const pickups = Object.fromEntries(
        data.deliveries
            .filter(d => d.status !== "completed" && d.phase === "pickup")
            .map(d => [`${d.pickup[0]},${d.pickup[1]}`, d])
    );

    for (let y = 0; y < data.height; y++) {
        for (let x = 0; x < data.width; x++) {
            const key = `${x},${y}`;
            const cell = document.createElement("div");
            cell.className = "cell";

            if (obstacles.has(key)) {
                cell.classList.add("obstacle");
            }

            if (rooms[key]) {
                cell.classList.add("room");
                cell.innerHTML = `
                    <span class="label">${rooms[key].name}</span>
                `;
            }

            if (pickups[key] && !rooms[key]) {
                cell.classList.add("pickup");

                const packageBox = document.createElement("div");
                packageBox.className = "package";
                cell.appendChild(packageBox);

                const label = document.createElement("span");
                label.className = "label";
                label.textContent = pickups[key].id;
                cell.appendChild(label);
            }

            if (robots[key]) {
                const robot = robots[key];

                cell.innerHTML = "";

                const icon = document.createElement("div");
                icon.className =
                    `robot ${robot.id === "R1" ? "atlas" : "nova"}`;
                icon.textContent =
                    robot.id === "R1" ? "A" : "N";

                cell.appendChild(icon);

                const label = document.createElement("span");
                label.className = "robot-label";
                label.textContent = robot.name;

                cell.appendChild(label);
            }

            map.appendChild(cell);
        }
    }
}

function renderRobots(data) {
    const container = document.getElementById("robots");

    container.innerHTML = data.robots.map(robot => `
        <div class="robot-card">
            <div class="robot-top">
                <div class="robot-name">
                    <span class="dot ${robot.id === "R1" ? "atlas" : "nova"}"></span>
                    ${robot.name}
                </div>

                <span class="robot-status">${robot.status}</span>
            </div>

            <div class="robot-grid">
                <div class="robot-stat">
                    <span>Delivery</span>
                    <b>${robot.delivery_id || "None"}</b>
                </div>

                <div class="robot-stat">
                    <span>Position</span>
                    <b>(${robot.x}, ${robot.y})</b>
                </div>

                <div class="robot-stat">
                    <span>Completed</span>
                    <b>${robot.completed}</b>
                </div>

                <div class="robot-stat">
                    <span>Safe waits</span>
                    <b>${robot.safe_waits}</b>
                </div>
            </div>

            <div class="reason">
                <b>${robot.action}</b> — ${robot.reason}
            </div>
        </div>
    `).join("");
}

function renderQueue(data) {
    const queue = document.getElementById("queue");

    queue.innerHTML = data.deliveries.map(delivery => `
        <div class="delivery">
            <div class="delivery-id">${delivery.id}</div>
            <div class="delivery-item">${delivery.item}</div>
            <div class="delivery-status ${delivery.status}">
                ${delivery.status}
            </div>
        </div>
    `).join("");
}

function render(data) {
    document.getElementById("deliveries").textContent =
        `${data.completed}/${data.total_deliveries}`;

    document.getElementById("tick").textContent =
        data.tick;

    document.getElementById("waits").textContent =
        data.waits;

    renderMap(data);
    renderRobots(data);
    renderQueue(data);
}

async function step() {
    const data = await api("/api/step", {
        method: "POST"
    });

    render(data);
}

async function reset() {
    stop();

    const data = await api("/api/reset", {
        method: "POST"
    });

    render(data);
}

function start() {
    if (state.running) return;

    state.running = true;
    document.getElementById("autoBtn").textContent = "Ⅱ Pause";

    state.timer = setInterval(step, 700);
}

function stop() {
    state.running = false;

    clearInterval(state.timer);
    state.timer = null;

    document.getElementById("autoBtn").textContent =
        "▶ Start";
}

document.getElementById("autoBtn").addEventListener(
    "click",
    () => state.running ? stop() : start()
);

document.getElementById("stepBtn").addEventListener(
    "click",
    step
);

document.getElementById("resetBtn").addEventListener(
    "click",
    reset
);

document.querySelectorAll(".dpad button").forEach(button => {
    button.addEventListener("click", async () => {
        const data = await api("/api/manual", {
            method: "POST",
            body: JSON.stringify({
                robot: button.dataset.robot,
                action: button.dataset.action
            })
        });

        render(data);
    });
});

api("/api/state").then(render);
