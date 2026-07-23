const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const state = {
  dashboard: null,
  industry: "餐饮",
  caseNumber: 86,
  threadId: localStorage.getItem("shangzhi_thread_id") || null,
  agentMode: "unknown",
};

const industries = {
  餐饮: { icon: "餐", name: "李店长 · 单店经营者", text: "每天只能抽出 20 分钟看数据，希望系统直接告诉他先做什么。", insights: [["套餐转化","价格 / 分量 / 差评联动"],["评价管理","负向主题与回复"],["老客复购","定向召回与券包"]] },
  零售: { icon: "零", name: "周老板 · 社区零售商", text: "SKU 多、库存周转慢，最关心哪些商品需要补货或促销。", insights: [["库存积压","滞销诊断与清仓"],["爆款缺货","库存水位提醒"],["选品促销","SKU 级行动建议"]] },
  休闲娱乐: { icon: "娱", name: "陈经理 · 娱乐门店运营", text: "工作日闲时利用率低，希望用预约和分时活动提升产能。", insights: [["闲时利用","分时定价与券包"],["预约爽约","预测与提醒"],["组合套餐","场景化活动设计"]] },
};

const scoreNames = ["问题判断准确","数据引用正确","建议可执行","符合行业特点","无虚构数据","语气适合商家","无违规承诺","高风险操作确认"];
const scores = Object.fromEntries(scoreNames.map((name) => [name, 4]));

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function toast(text) {
  const el = $("#toast");
  el.textContent = text;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2500);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "";
    throw new Error(data.error || detail || "请求失败");
  }
  return data;
}

function animateNumber(el, target) {
  const started = performance.now();
  const duration = 850;
  function frame(now) {
    const p = Math.min(1, (now - started) / duration);
    const value = target * (1 - Math.pow(1 - p, 3));
    el.textContent = Number.isInteger(target) ? Math.round(value).toLocaleString() : value.toFixed(2);
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function renderDashboard(data) {
  state.dashboard = data;
  $("#metricGrid").innerHTML = data.metrics.map((metric) => `
    <article class="metric">
      <span>${escapeHtml(metric.label)}</span>
      <b>${escapeHtml(metric.display)}</b>
      <small>${escapeHtml(metric.trend)} · 较上周</small>
    </article>`).join("");
  $("#opportunityList").innerHTML = data.opportunities.map((item) => `
    <div class="opportunity">
      <div><h3>${escapeHtml(item.level)} · ${escapeHtml(item.title)}</h3><p>${escapeHtml(item.detail)}</p></div>
      <strong>${escapeHtml(item.impact)}</strong>
      <button data-question="分析：${escapeHtml(item.title)}">去处理 →</button>
    </div>`).join("");
  $("#funnelRows").innerHTML = data.funnel.map((item, index) => `
    <div class="funnel-row">
      <div class="funnel-bar" style="width:${100-index*9}%;animation-delay:${index*.08}s">
        <span>${escapeHtml(item.label)}</span><b>${item.value.toLocaleString()}</b>
      </div>
      <small>${index ? `上一步转化 ${escapeHtml(item.rate)}` : "总触达商家"}</small>
    </div>`).join("");
  $$("[data-count]").forEach((el) => animateNumber(el, Number(el.dataset.count)));
  bindQuestionButtons();
}

function bindQuestionButtons() {
  $$("[data-question]").forEach((button) => {
    button.onclick = () => sendAgentMessage(button.dataset.question);
  });
}

function setAgentStatus(agent) {
  state.agentMode = agent.mode;
  const isLive = agent.mode === "live";
  const modeLabel = isLive ? "LIVE AGENT" : agent.mode === "fallback" ? "FALLBACK" : "DEMO AGENT";
  const status = $("#systemStatus");
  status.className = `live mode-${agent.mode}`;
  status.innerHTML = `<i></i> ${modeLabel} · ${escapeHtml(agent.model)}`;
  $("#agentModeBadge").className = `mode-badge mode-${agent.mode}`;
  $("#agentModeBadge").textContent = isLive
    ? `LIVE · ${agent.model}`
    : agent.mode === "fallback"
      ? `FALLBACK · ${agent.model}`
      : "DEMO · OFFLINE";
  $("#runtimeMode").textContent = modeLabel;
  $("#runtimeModel").textContent = agent.model;
  $("#runtimeMemory").textContent = agent.memory;

  const firstMessage = $(".assistant", $("#messages"));
  if (firstMessage) {
    firstMessage.textContent = isLive
      ? `真实 Agent 已连接 ${agent.model}。每次回答都会调用经营工具、生成证据链并经过风险审核。`
      : agent.mode === "fallback"
        ? `模型调用曾失败，当前已安全降级。请检查后端模型权限或密钥；工具、记忆和风控仍正常运行。`
        : "当前明确运行 DEMO 模式：流程、工具、记忆和风控都是真实的，但诊断内容由离线推理生成。配置 OPENAI_API_KEY 后会自动切换为真实模型。";
  }
}

function traceStep(label, status = "running") {
  const trace = $("#agentTrace");
  if (status === "reset") {
    trace.innerHTML = "";
    trace.classList.add("active");
    return;
  }
  trace.insertAdjacentHTML("beforeend", `
    <span class="trace-step ${status}">
      <i></i>${escapeHtml(label)}
    </span>`);
  trace.scrollLeft = trace.scrollWidth;
}

function completeTraceStep(node, label) {
  const running = $(".trace-step.running", $("#agentTrace"));
  if (running) running.classList.replace("running", "completed");
  traceStep(label, "completed");
  $("#agentTrace").dataset.lastNode = node;
}

function renderAgentAnswer(data) {
  const evidence = data.evidence.map((item) => `
    <article>
      <span>${escapeHtml(item.evidence_id)}</span>
      <b>${escapeHtml(item.metric)}</b>
      <strong>${escapeHtml(item.observed)}</strong>
      <small>${escapeHtml(item.comparison)}</small>
      <em>${escapeHtml(item.source)}</em>
    </article>`).join("");

  const recommendations = data.recommendations.map((item) => {
    const action = data.actions.find((candidate) => candidate.title === item.title);
    const steps = item.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("");
    const controls = action ? `
      <div class="action-controls" data-action-box="${escapeHtml(action.action_id)}">
        <span>需要商家确认 · ${escapeHtml(item.risk_level.toUpperCase())}</span>
        <button data-action-id="${escapeHtml(action.action_id)}" data-approved="false">拒绝</button>
        <button class="approve" data-action-id="${escapeHtml(action.action_id)}" data-approved="true">确认执行</button>
      </div>` : `<span class="safe-action">✓ 低风险分析建议，可直接查看</span>`;
    return `
      <article class="recommendation">
        <div><span>${escapeHtml(item.action_type)}</span><b>${escapeHtml(item.title)}</b></div>
        <p>${escapeHtml(item.rationale)}</p>
        <ol>${steps}</ol>
        <small>验证信号：${escapeHtml(item.expected_signal)}</small>
        ${controls}
      </article>`;
  }).join("");

  const warnings = [...data.safety.warnings, ...data.safety.blocked_reasons];
  const warningHtml = warnings.length
    ? `<div class="safety-warning">⚠ ${warnings.map(escapeHtml).join("；")}</div>`
    : `<div class="safety-pass">✓ 已通过证据引用与风险规则检查</div>`;

  const modeLabel = data.mode === "live" ? "真实模型" : data.mode === "fallback" ? "模型降级" : "离线演示";
  const html = `
    <div class="assistant agent-answer">
      <div class="answer-meta">
        <span>${escapeHtml(modeLabel)} · ${escapeHtml(data.model)}</span>
        <b>置信度 ${Math.round(data.confidence * 100)}%</b>
      </div>
      <h3>${escapeHtml(data.answer)}</h3>
      ${warningHtml}
      <details open>
        <summary>证据链 · ${data.evidence.length} 条</summary>
        <div class="evidence-grid">${evidence}</div>
      </details>
      <details open>
        <summary>行动建议 · ${data.recommendations.length} 条</summary>
        <div class="recommendation-list">${recommendations}</div>
      </details>
      ${data.missing_data.length ? `<p class="missing-data">仍需补充：${data.missing_data.map(escapeHtml).join("、")}</p>` : ""}
    </div>`;
  $("#messages").insertAdjacentHTML("beforeend", html);
}

function parseSseBlock(block) {
  const lines = block.split("\n");
  const dataLines = lines
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim());
  if (!dataLines.length) return null;
  return JSON.parse(dataLines.join("\n"));
}

async function sendAgentMessage(message) {
  if (!message) return;
  const messages = $("#messages");
  $("#chatSubmit").disabled = true;
  messages.insertAdjacentHTML("beforeend", `
    <div class="merchant-message">${escapeHtml(message)}</div>
    <div class="assistant thinking"><i></i><i></i><i></i></div>`);
  messages.scrollTop = messages.scrollHeight;
  traceStep("", "reset");
  traceStep("启动 Agent", "running");

  let streamError = "";
  try {
    const response = await fetch("/api/agent/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        thread_id: state.threadId,
        merchant_id: "merchant_demo",
      }),
    });
    if (!response.ok || !response.body) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || body.error || "Agent 请求失败");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";
      for (const block of blocks) {
        if (!block.trim()) continue;
        const event = parseSseBlock(block);
        if (!event) continue;
        if (event.type === "start") {
          state.threadId = event.thread_id;
          localStorage.setItem("shangzhi_thread_id", state.threadId);
        } else if (event.type === "step") {
          completeTraceStep(event.node, event.label);
        } else if (event.type === "final") {
          $(".thinking", messages)?.remove();
          renderAgentAnswer(event.data);
          $("#agentTrace").classList.remove("active");
        } else if (event.type === "error") {
          streamError = event.error;
        }
      }
      if (done) break;
    }
    if (streamError) throw new Error(streamError);
  } catch (error) {
    $(".thinking", messages)?.remove();
    messages.insertAdjacentHTML("beforeend", `<div class="assistant error-message">${escapeHtml(error.message)}</div>`);
    toast(error.message);
  } finally {
    $("#chatSubmit").disabled = false;
    messages.scrollTop = messages.scrollHeight;
  }
}

async function confirmAction(actionId, approved, button) {
  const box = button.closest("[data-action-box]");
  $$("button", box).forEach((item) => { item.disabled = true; });
  try {
    const data = await api("/api/agent/confirm", {
      method: "POST",
      body: JSON.stringify({ action_id: actionId, approved }),
    });
    box.classList.add(approved ? "approved" : "rejected");
    box.innerHTML = `<strong>${approved ? "✓ 已确认并完成模拟执行" : "✕ 已拒绝，未执行任何变更"}</strong>`;
    toast(data.message);
  } catch (error) {
    $$("button", box).forEach((item) => { item.disabled = false; });
    toast(error.message);
  }
}

function renderIndustry(name) {
  const item = industries[name];
  $("#personaIcon").textContent = item.icon;
  $("#personaName").textContent = item.name;
  $("#personaText").textContent = item.text;
  $("#insights").innerHTML = item.insights.map(([title, desc], index) => `
    <article class="insight"><span>0${index + 1}</span><b>${escapeHtml(title)}</b><small>${escapeHtml(desc)}</small></article>`).join("");
}

async function calculateExperiment() {
  const traffic = Number($("#traffic").value);
  $("#trafficValue").textContent = `${traffic}%`;
  $("#trafficRing").style.setProperty("--traffic", `${traffic}%`);
  try {
    const data = await api("/api/experiment/calculate", {
      method: "POST",
      body: JSON.stringify({ traffic }),
    });
    $("#samples").textContent = `${data.a_samples.toLocaleString()} / ${data.b_samples.toLocaleString()}`;
    $("#days").textContent = `${data.estimated_days} 天`;
    $("#power").textContent = `${data.power}%`;
  } catch (error) {
    toast(error.message);
  }
}

function renderScores() {
  $("#scoreRows").innerHTML = scoreNames.map((name) => `
    <div class="score-row">
      <span>${name}</span>
      ${[1,2,3,4,5].map((value) => `
        <button type="button" data-score-name="${name}" data-score="${value}" class="${scores[name] === value ? "active" : ""}">${value}</button>`).join("")}
    </div>`).join("");
  $$("[data-score-name]").forEach((button) => {
    button.onclick = () => {
      scores[button.dataset.scoreName] = Number(button.dataset.score);
      renderScores();
    };
  });
  $("#totalScore").textContent = (Object.values(scores).reduce((a, b) => a + b, 0) / scoreNames.length).toFixed(2);
}

function updateTasks() {
  const boxes = $$(".tasks input");
  const done = boxes.filter((box) => box.checked).length;
  $("#taskCount").textContent = done;
  $("#taskProgress").style.width = `${done / boxes.length * 100}%`;
}

async function runEvals() {
  const button = $("#runEval");
  button.disabled = true;
  button.textContent = "评测运行中…";
  try {
    const data = await api("/api/evals/run", { method: "POST" });
    const result = data.result;
    const rate = Math.round(result.passed / result.total * 100);
    $("#evalRate").textContent = `${rate}%`;
    $("#evalDetail").textContent = `${result.passed} / ${result.total} 条通过`;
    toast(`评测完成：${result.passed}/${result.total} 通过`);
  } catch (error) {
    toast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "重新运行评测";
  }
}

async function initialize() {
  renderIndustry("餐饮");
  renderScores();
  updateTasks();
  calculateExperiment();
  try {
    const [health, dashboard] = await Promise.all([
      api("/api/health"),
      api("/api/dashboard"),
    ]);
    setAgentStatus(health.agent);
    renderDashboard(dashboard.data);
  } catch (error) {
    $("#systemStatus").innerHTML = "<i></i> AGENT OFFLINE";
    toast(error.message);
  }
  try {
    const evals = await api("/api/evals/summary");
    if (evals.summary.total) {
      $("#evalRate").textContent = `${Math.round(evals.summary.pass_rate * 100)}%`;
      $("#evalDetail").textContent = `${evals.summary.passed} / ${evals.summary.total} 条历史评测通过`;
    }
  } catch (_) {
    // 首次运行没有评测记录时保持默认文案。
  }
}

document.addEventListener("pointermove", (event) => {
  document.documentElement.style.setProperty("--x", `${event.clientX}px`);
  document.documentElement.style.setProperty("--y", `${event.clientY}px`);
});

function updateClock() {
  $("#clock").textContent = new Date().toLocaleString("zh-CN", { hour12: false, weekday: "long" });
}
updateClock();
setInterval(updateClock, 1000);

$$(".sidebar nav button").forEach((button) => {
  button.onclick = () => document.getElementById(button.dataset.target).scrollIntoView({ behavior: "smooth" });
});
$$(".tabs button").forEach((button) => {
  button.onclick = () => {
    $$(".tabs button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderIndustry(button.dataset.industry);
  };
});

$("#chatForm").onsubmit = (event) => {
  event.preventDefault();
  const input = $("#chatInput");
  const message = input.value.trim();
  input.value = "";
  sendAgentMessage(message);
};

$("#messages").addEventListener("click", (event) => {
  const button = event.target.closest("[data-action-id]");
  if (!button) return;
  confirmAction(button.dataset.actionId, button.dataset.approved === "true", button);
});

$("#traffic").oninput = calculateExperiment;
$("#runEval").onclick = runEvals;
$$(".tasks input").forEach((box) => { box.onchange = updateTasks; });

$("#annotationForm").onsubmit = async (event) => {
  event.preventDefault();
  const errors = $$('input[name="error"]:checked').map((input) => input.value);
  try {
    const data = await api("/api/annotations", {
      method: "POST",
      body: JSON.stringify({
        case_id: `CASE-${String(state.caseNumber).padStart(4, "0")}`,
        scores,
        errors,
        note: $("#note").value,
      }),
    });
    state.caseNumber += 1;
    $("#caseTitle").textContent = `${data.next_case} · 零售库存积压 · 高风险`;
    event.target.reset();
    toast("标注已保存到本地 SQLite 同级数据目录");
  } catch (error) {
    toast(error.message);
  }
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add("visible"));
}, { threshold: .08 });
$$(".reveal").forEach((el) => observer.observe(el));

const navObserver = new IntersectionObserver((entries) => {
  const visible = entries
    .filter((entry) => entry.isIntersecting)
    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (visible) {
    $$(".sidebar nav button").forEach((button) => {
      button.classList.toggle("active", button.dataset.target === visible.target.id);
    });
  }
}, { threshold: .35, rootMargin: "-10% 0px -45%" });

$$(".sidebar nav button").forEach((button) => {
  navObserver.observe(document.getElementById(button.dataset.target));
});

initialize();
