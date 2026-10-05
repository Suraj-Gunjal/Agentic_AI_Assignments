const state = {
    running: false,
    timer: null,
    data: null
};

const $ = (id) => document.getElementById(id);

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {"Content-Type": "application/json"},
        ...options
    });

    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error || "Request failed");
    }

    return response.json();
}

function format(value, digits = 1) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(digits) : "0.0";
}

function update(data) {
    state.data = data;

    const env = data.environment;
    const decision = data.agent.decision;
    const stats = data.agent.stats;

    $("temperature").innerHTML =
        `${format(env.temperature)}<span>°C</span>`;

    $("target").innerHTML =
        `${format(env.target)}<span>°C</span>`;

    $("energy").innerHTML =
        `${format(env.energy)}<span> units</span>`;

    $("successRate").innerHTML =
        `${format(stats.success_rate)}<span>%</span>`;

    $("stepCount").textContent = stats.steps;

    $("roomDisplay").textContent =
        `${format(env.temperature)}°`;

    $("deviceTarget").textContent =
        `${format(env.target)}°`;

    $("roomTempLarge").textContent =
        `${format(env.temperature)}°C`;

    const error = env.target - env.temperature;

    $("tempDelta").textContent =
        `${error >= 0 ? "+" : ""}${format(error)}°C to target`;

    if (Math.abs(error) <= .5) {
        $("tempStatus").textContent = "Comfort zone";
    } else if (error > 0) {
        $("tempStatus").textContent = "Below comfort";
    } else {
        $("tempStatus").textContent = "Above comfort";
    }

    const marker = Math.max(
        0,
        Math.min(100, ((env.temperature - 10) / 25) * 100)
    );

    $("tempMarker").style.left = `${marker}%`;

    $("actionName").textContent = decision.action;
    $("confidence").textContent = `${decision.confidence}%`;
    $("reason").textContent = decision.reason;

    $("error").textContent =
        `${decision.error >= 0 ? "+" : ""}${format(decision.error, 2)}°C`;

    const latest = data.last;
    $("reward").textContent = latest
        ? `${latest.reward >= 0 ? "+" : ""}${format(latest.reward, 2)}`
        : "—";

    const icons = {
        HEAT: "🔥",
        COOL: "❄",
        FAN: "◌",
        IDLE: "○"
    };

    $("actionIcon").textContent = icons[decision.action] || "—";

    const hvac = $("hvac");
    hvac.className = `hvac ${decision.action.toLowerCase()}`;
    $("hvacLabel").textContent = decision.action;

    $("disturbance").textContent =
        env.disturbance === "Stable"
            ? "Stable environment"
            : env.disturbance;

    renderKnowledge(data.agent.knowledge);
    drawChart(data.history, env.target);
}

function renderKnowledge(knowledge) {
    const container = $("knowledgeList");

    const colors = {
        HEAT: "#ef7e7e",
        COOL: "#78a9ef",
        FAN: "#6dc7e8",
        IDLE: "#77e0b5"
    };

    const rows = Object.entries(knowledge).map(([action, data]) => {
        const samples = Number(data.samples) || 0;
        const width = Math.min(100, samples * 7);

        return `
            <div class="knowledge-row">
                <div class="knowledge-name">${action}</div>
                <div class="knowledge-bar">
                    <div
                        class="knowledge-fill"
                        style="width:${width}%;background:${colors[action]}"
                    ></div>
                </div>
                <div class="knowledge-value">
                    ${samples} samples
                </div>
            </div>
        `;
    }).join("");

    container.innerHTML = rows;
}

function drawChart(history, target) {
    const canvas = $("chart");
    const rect = canvas.getBoundingClientRect();

    const dpr = window.devicePixelRatio || 1;
    const width = Math.max(400, Math.floor(rect.width));
    const height = 310;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);

    const values = history.length
        ? history.map(item => Number(item.temperature))
        : [19];

    const min = Math.min(...values, target) - 1.5;
    const max = Math.max(...values, target) + 1.5;

    const pad = {
        left: 45,
        right: 20,
        top: 18,
        bottom: 32
    };

    const chartW = width - pad.left - pad.right;
    const chartH = height - pad.top - pad.bottom;

    const x = i =>
        pad.left + (i / Math.max(1, values.length - 1)) * chartW;

    const y = value =>
        pad.top + ((max - value) / (max - min)) * chartH;

    ctx.strokeStyle = "#202a34";
    ctx.lineWidth = 1;

    for (let i = 0; i <= 4; i++) {
        const yy = pad.top + (chartH / 4) * i;

        ctx.beginPath();
        ctx.moveTo(pad.left, yy);
        ctx.lineTo(width - pad.right, yy);
        ctx.stroke();

        const value = max - ((max - min) / 4) * i;
        ctx.fillStyle = "#63717e";
        ctx.font = "10px DM Mono";
        ctx.fillText(`${value.toFixed(1)}°`, 5, yy + 3);
    }

    ctx.setLineDash([5, 5]);
    ctx.strokeStyle = "#f3c969";
    ctx.beginPath();
    ctx.moveTo(pad.left, y(target));
    ctx.lineTo(width - pad.right, y(target));
    ctx.stroke();
    ctx.setLineDash([]);

    if (values.length > 1) {
        ctx.beginPath();

        values.forEach((value, i) => {
            const px = x(i);
            const py = y(value);

            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });

        ctx.strokeStyle = "#77e0b5";
        ctx.lineWidth = 2.5;
        ctx.stroke();

        values.forEach((value, i) => {
            ctx.beginPath();
            ctx.arc(x(i), y(value), 3.5, 0, Math.PI * 2);
            ctx.fillStyle = "#77e0b5";
            ctx.fill();
        });
    }

    ctx.fillStyle = "#63717e";
    ctx.font = "10px DM Mono";
    ctx.fillText("time →", width - 55, height - 8);
}

async function refresh() {
    try {
        const data = await api("/api/state");
        update(data);
    } catch (error) {
        console.error(error);
    }
}

async function step() {
    try {
        const data = await api("/api/step", {method: "POST"});
        update(data);
    } catch (error) {
        alert(error.message);
    }
}

function startAuto() {
    if (state.running) return;

    state.running = true;
    $("autoBtn").textContent = "Ⅱ Pause agent";

    const run = async () => {
        if (!state.running) return;

        await step();

        if (state.running) {
            const speed = Number($("speed").value) || 500;
            state.timer = setTimeout(run, speed);
        }
    };

    run();
}

function stopAuto() {
    state.running = false;

    if (state.timer) {
        clearTimeout(state.timer);
        state.timer = null;
    }

    $("autoBtn").textContent = "▶ Run agent";
}

$("autoBtn").addEventListener("click", () => {
    if (state.running) stopAuto();
    else startAuto();
});

$("stepBtn").addEventListener("click", step);

$("resetBtn").addEventListener("click", async () => {
    stopAuto();

    const target = Number($("targetInput").value) || 24;

    const data = await api("/api/reset", {
        method: "POST",
        body: JSON.stringify({
            target,
            temperature: 19
        })
    });

    update(data);
});

$("setTarget").addEventListener("click", async () => {
    const target = Number($("targetInput").value);

    if (!Number.isFinite(target) || target < 10 || target > 35) {
        alert("Choose a target between 10°C and 35°C.");
        return;
    }

    const data = await api("/api/target", {
        method: "POST",
        body: JSON.stringify({target})
    });

    update(data);
});

document.querySelectorAll(".manual-btn").forEach(button => {
    button.addEventListener("click", async () => {
        stopAuto();

        const action = button.dataset.action;

        const data = await api("/api/manual", {
            method: "POST",
            body: JSON.stringify({action})
        });

        update(data);
    });
});

window.addEventListener("resize", () => {
    if (state.data) {
        drawChart(
            state.data.history,
            state.data.environment.target
        );
    }
});

refresh();
