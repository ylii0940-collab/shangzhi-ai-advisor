"use client";

import { FormEvent, useMemo, useState } from "react";

type Message = { role: "assistant" | "merchant"; text: string };

const navItems = ["经营总览", "策略看板", "A/B 实验", "标注评测", "Prompt 管理"];

const funnel = [
  { label: "消息送达", value: "48,260", rate: "100%" },
  { label: "商家阅读", value: "31,849", rate: "66.0%" },
  { label: "商家回复", value: "12,421", rate: "39.0%" },
  { label: "接受建议", value: "6,583", rate: "53.0%" },
  { label: "执行操作", value: "4,147", rate: "63.0%" },
  { label: "经营改善", value: "2,364", rate: "57.0%" },
];

const strategyMetrics = [
  ["消息阅读率", "66.0%", "+5.8pp", "up"], ["商家回复率", "39.0%", "+8.2pp", "up"],
  ["有效会话率", "71.4%", "+3.1pp", "up"], ["建议采纳率", "53.0%", "+12.6pp", "up"],
  ["任务完成率", "63.0%", "+6.7pp", "up"], ["商家 7 日留存", "78.6%", "+2.4pp", "up"],
  ["订单提升", "+9.8%", "+1.7pp", "up"], ["AI 错误建议率", "0.72%", "-0.18pp", "good"],
  ["商家投诉率", "0.09%", "-0.03pp", "good"],
];

const evalDimensions = [
  ["问题判断准确", 4.62], ["数据引用正确", 4.81], ["建议可执行", 4.38], ["符合行业特点", 4.26],
  ["无虚构数据", 4.75], ["语气适合商家", 4.53], ["无违规承诺", 4.89], ["高风险操作确认", 4.94],
];

const alerts = [
  {
    level: "高优先级",
    title: "套餐转化率连续 7 日下降",
    detail: "招牌双人餐曝光上涨 12%，支付转化率下降 18%",
    value: "预计少成交 56 单",
    color: "red",
  },
  {
    level: "可优化",
    title: "晚市仍有空闲产能",
    detail: "20:00 后到店率低于同商圈同品类商家 21%",
    value: "预计可增收 ¥3,200",
    color: "amber",
  },
  {
    level: "新机会",
    title: "老客复购信号增强",
    detail: "近 30 日收藏用户中有 238 人尚未再次到店",
    value: "建议定向召回",
    color: "green",
  },
];

const metrics = [
  { label: "今日实收", value: "¥12,680", trend: "+8.6%", positive: true },
  { label: "支付订单", value: "186", trend: "+12.3%", positive: true },
  { label: "到店转化率", value: "7.8%", trend: "-1.4%", positive: false },
  { label: "店铺评分", value: "4.63", trend: "+0.06", positive: true },
];

const quickPrompts = [
  "为什么本周转化率下降？",
  "帮我优化双人套餐",
  "总结最近的差评",
];

function Sparkline() {
  return (
    <div className="sparkline" aria-label="近七日经营趋势">
      {[42, 48, 45, 58, 54, 64, 72].map((height, index) => (
        <span key={index} style={{ height: `${height}%` }} />
      ))}
    </div>
  );
}

export default function Home() {
  const [activeNav, setActiveNav] = useState("经营总览");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "早上好，李店长。我分析了门店近 7 天的数据，发现招牌双人餐的曝光上涨了 12%，但转化率下降了 18%。主要问题集中在价格感知和近期 6 条关于“分量不足”的评价。",
    },
  ]);
  const [input, setInput] = useState("");
  const [taskCreated, setTaskCreated] = useState(false);
  const [notice, setNotice] = useState("");

  const response = useMemo(
    () =>
      "建议先做一个 7 天小流量实验：保留 ¥168 原价，新增工作日晚市 ¥148 限时价，并将套餐中的小食升级为双份。预计可提升转化率 8%–12%。我可以先为你生成活动方案，确认后再创建。",
    [],
  );

  function sendMessage(text?: string) {
    const content = (text ?? input).trim();
    if (!content) return;
    setMessages((current) => [
      ...current,
      { role: "merchant", text: content },
      { role: "assistant", text: response },
    ]);
    setInput("");
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    sendMessage();
  }

  function createTask() {
    setTaskCreated(true);
    setNotice("优化任务已加入今日待办");
    window.setTimeout(() => setNotice(""), 2600);
  }

  function navigateTo(item: string) {
    setActiveNav(item);
    const sectionId: Record<string, string> = {
      "经营总览": "overview",
      "策略看板": "strategy-dashboard",
      "A/B 实验": "ab-experiment",
      "标注评测": "evaluation",
      "Prompt 管理": "prompt-management",
    };
    window.setTimeout(() => document.getElementById(sectionId[item])?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
  }

  return (
    <main className="app-shell">
      {notice && <div className="toast">✓ {notice}</div>}

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">商</div>
          <div><strong>商智</strong><span>AI 经营顾问</span></div>
        </div>

        <nav aria-label="主导航">
          <p className="nav-label">工作台</p>
          {navItems.map((item, index) => (
            <button
              key={item}
              onClick={() => navigateTo(item)}
              className={activeNav === item ? "nav-item active" : "nav-item"}
            >
              <span className="nav-icon">{["⌂", "▥", "A", "✓", "✦"][index]}</span>
              {item}
              {item === "标注评测" && <em>3</em>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item"><span className="nav-icon">?</span>帮助中心</button>
          <div className="merchant-card">
            <div className="avatar">李</div>
            <div><strong>李记小馆</strong><span>餐饮 · 杭州湖滨店</span></div>
            <button aria-label="商家设置">•••</button>
          </div>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">2026年7月23日 · 星期四</p>
            <h1>早上好，李店长</h1>
          </div>
          <div className="top-actions">
            <button className="icon-button" aria-label="搜索">⌕</button>
            <button className="icon-button has-dot" aria-label="通知">♢</button>
            <button className="primary-button" onClick={() => sendMessage("生成今日经营简报")}>✦ 询问 AI 顾问</button>
          </div>
        </header>

        <div className="dashboard-grid section-anchor" id="overview">
          <section className="overview-column">
            <div className="hero-card">
              <div className="hero-copy">
                <div className="status-pill"><span /> 门店经营健康</div>
                <p className="hero-kicker">今日经营评分</p>
                <div className="score-row"><strong>82</strong><span>/ 100</span><b>↑ 5</b></div>
                <p className="hero-note">超过同商圈 73% 的餐饮门店，复购表现良好，套餐转化仍有提升空间。</p>
                <button onClick={() => sendMessage("给我完整解释今日经营评分")}>查看完整诊断 <span>→</span></button>
              </div>
              <div className="hero-visual">
                <div className="score-ring"><div><strong>82</strong><span>良好</span></div></div>
                <div className="mini-insight"><span>近 7 日趋势</span><Sparkline /></div>
              </div>
            </div>

            <div className="metrics-grid">
              {metrics.map((metric) => (
                <article className="metric-card" key={metric.label}>
                  <span>{metric.label}</span>
                  <div><strong>{metric.value}</strong><b className={metric.positive ? "up" : "down"}>{metric.trend}</b></div>
                  <small>较上周同期</small>
                </article>
              ))}
            </div>

            <section className="panel opportunities">
              <div className="panel-header">
                <div><h2>AI 发现了 3 个经营机会</h2><p>基于实时数据和同商圈基准分析</p></div>
                <button>查看全部</button>
              </div>
              <div className="alert-list">
                {alerts.map((alert) => (
                  <article className="alert-row" key={alert.title}>
                    <div className={`alert-icon ${alert.color}`}>{alert.color === "red" ? "!" : alert.color === "amber" ? "↗" : "✦"}</div>
                    <div className="alert-copy">
                      <span className={`alert-level ${alert.color}`}>{alert.level}</span>
                      <h3>{alert.title}</h3>
                      <p>{alert.detail}</p>
                    </div>
                    <strong>{alert.value}</strong>
                    <button onClick={() => sendMessage(`分析：${alert.title}`)}>去处理 →</button>
                  </article>
                ))}
              </div>
            </section>

            <section className="panel trend-panel">
              <div className="panel-header">
                <div><h2>近 7 日经营趋势</h2><p>实收金额与订单量</p></div>
                <select aria-label="趋势周期"><option>近 7 天</option><option>近 30 天</option></select>
              </div>
              <div className="chart-wrap">
                <div className="chart-y"><span>16k</span><span>12k</span><span>8k</span><span>4k</span><span>0</span></div>
                <div className="chart-area">
                  <div className="grid-lines"><i/><i/><i/><i/><i/></div>
                  <div className="line-chart" aria-hidden="true">
                    <span style={{left:"0%", bottom:"30%"}}/><span style={{left:"16.6%", bottom:"43%"}}/>
                    <span style={{left:"33.2%", bottom:"38%"}}/><span style={{left:"49.8%", bottom:"61%"}}/>
                    <span style={{left:"66.4%", bottom:"56%"}}/><span style={{left:"83%", bottom:"70%"}}/>
                    <span style={{left:"99%", bottom:"79%"}}/>
                  </div>
                  <div className="chart-x"><span>7/17</span><span>7/18</span><span>7/19</span><span>7/20</span><span>7/21</span><span>7/22</span><span>今天</span></div>
                </div>
              </div>
            </section>
          </section>

          <aside className="assistant-column">
            <section className="ai-panel">
              <div className="ai-header">
                <div className="ai-avatar">✦</div>
                <div><h2>AI 经营顾问</h2><p><span /> 正在为你分析经营数据</p></div>
                <button aria-label="更多选项">•••</button>
              </div>
              <div className="chat-log">
                {messages.map((message, index) => (
                  <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
                    {message.role === "assistant" && <div className="tiny-avatar">✦</div>}
                    <p>{message.text}</p>
                  </div>
                ))}
                {messages.length === 1 && (
                  <div className="recommendation">
                    <strong>建议优先处理</strong>
                    <p>用 7 天小流量实验验证工作日晚市优惠，并优化套餐分量表达。</p>
                    <div><button onClick={createTask}>{taskCreated ? "✓ 已加入待办" : "生成优化方案"}</button><button onClick={() => sendMessage("告诉我你的分析依据")}>查看分析依据</button></div>
                  </div>
                )}
              </div>
              <div className="quick-prompts">
                {quickPrompts.map((prompt) => <button key={prompt} onClick={() => sendMessage(prompt)}>{prompt}</button>)}
              </div>
              <form className="chat-form" onSubmit={submit}>
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="问问今日经营情况…" aria-label="向AI顾问提问" />
                <button aria-label="发送消息" type="submit">↑</button>
              </form>
              <p className="ai-disclaimer">AI 建议仅供参考，重要操作需你确认后执行</p>
            </section>

            <section className="panel tasks">
              <div className="panel-header"><div><h2>今日待办</h2><p>完成 2 / 4 项</p></div><button>全部任务</button></div>
              <div className="progress"><span style={{width: taskCreated ? "75%" : "50%"}} /></div>
              <label><input type="checkbox" defaultChecked /><span><strong>回复 3 条最新评价</strong><small>已完成 · 09:20</small></span></label>
              <label><input type="checkbox" defaultChecked /><span><strong>确认周末推广预算</strong><small>已完成 · 10:05</small></span></label>
              <label><input type="checkbox" checked={taskCreated} onChange={createTask} /><span><strong>优化招牌双人餐</strong><small>建议今天 17:00 前完成</small></span></label>
              <label><input type="checkbox" /><span><strong>补充 2 张门店环境图</strong><small>预计提升详情页点击率</small></span></label>
            </section>
          </aside>
        </div>

        <section className="ops-suite" aria-label="AI策略运营后台">
          <div className="suite-intro">
            <div>
              <span className="suite-tag">AI STRATEGY CONSOLE</span>
              <h2>策略运营与模型评测中心</h2>
              <p>从消息触达到经营改善，持续验证沟通策略、Prompt 质量与业务价值。</p>
            </div>
            <div className="suite-status"><span /> 数据更新于 10 分钟前</div>
          </div>

          <section className="panel strategy-panel section-anchor" id="strategy-dashboard">
            <div className="panel-header strategy-heading">
              <div><h2>商家沟通转化漏斗</h2><p>餐饮行业 · 近 30 天 · 已排除无效及测试商家</p></div>
              <div className="filter-row"><select aria-label="选择行业"><option>餐饮行业</option><option>零售行业</option><option>休闲娱乐</option></select><select aria-label="选择周期"><option>近 30 天</option><option>近 7 天</option></select></div>
            </div>
            <div className="funnel-wrap">
              {funnel.map((step, index) => (
                <div className="funnel-step" key={step.label}>
                  <div className="funnel-bar" style={{ width: `${100 - index * 10}%` }}>
                    <span>{step.label}</span><strong>{step.value}</strong>
                  </div>
                  {index > 0 && <small>上一步转化 {step.rate}</small>}
                </div>
              ))}
            </div>
            <div className="funnel-insight"><span>✦</span><div><strong>AI 洞察</strong><p>最大流失发生在“阅读 → 回复”，当前转化率 39.0%。B 组具体损失型开场已验证可将回复率提升 8.2pp，建议扩大至零售行业验证。</p></div><button onClick={() => navigateTo("A/B 实验")}>查看实验 →</button></div>
          </section>

          <div className="strategy-kpis">
            {strategyMetrics.map(([label, value, trend, tone]) => (
              <article key={label}><span>{label}</span><strong>{value}</strong><small className={tone}>{trend} <i>较上期</i></small></article>
            ))}
          </div>

          <section className="panel experiment-panel section-anchor" id="ab-experiment">
            <div className="panel-header strategy-heading">
              <div><div className="live-badge"><span /> 运行中</div><h2>开场策略实验：经营异常触达</h2><p>EXP-2026-0712 · 餐饮商家 · 50/50 随机分流 · 已运行 12 天</p></div>
              <button className="outline-action">查看实验报告</button>
            </div>
            <div className="hypothesis"><span>实验假设</span><p>包含<strong>具体损失、可能原因与行动建议</strong>的开场方式，比模糊异常提醒更能提升商家回复率和建议采纳率。</p></div>
            <div className="variant-grid">
              <article className="variant-card control">
                <header><div><span>A 组 · 对照组</span><strong>24,108 位商家</strong></div><b>基线策略</b></header>
                <blockquote>“您最近的经营数据存在异常，点击查看详情。”</blockquote>
                <div className="variant-results"><div><span>回复率</span><strong>30.8%</strong></div><div><span>采纳率</span><strong>40.4%</strong></div><div><span>完成率</span><strong>54.1%</strong></div></div>
              </article>
              <article className="variant-card winner">
                <header><div><span>B 组 · 实验组</span><strong>24,152 位商家</strong></div><b>当前领先</b></header>
                <blockquote>“您的套餐曝光上涨12%，但每天少成交约8单，可能与近期差评有关。我整理了3条优化建议。”</blockquote>
                <div className="variant-results"><div><span>回复率</span><strong>39.0%</strong><small>+8.2pp</small></div><div><span>采纳率</span><strong>53.0%</strong><small>+12.6pp</small></div><div><span>完成率</span><strong>63.0%</strong><small>+8.9pp</small></div></div>
              </article>
            </div>
            <div className="experiment-footer"><div><span>统计显著性</span><strong>99.2%</strong><small>p = 0.008</small></div><div><span>预计月增量</span><strong>+1,924</strong><small>完成经营任务商家</small></div><div className="decision-box"><span>实验结论</span><strong>B 组显著胜出</strong><small>建议扩大至 80% 流量，保留 20% 长期对照组</small></div><button onClick={() => setNotice("实验扩量申请已创建，等待负责人审批")}>申请扩大流量</button></div>
          </section>

          <section className="panel guardrail-panel">
            <div className="panel-header"><div><h2>实验护栏指标</h2><p>任何一项超过阈值，实验将自动暂停</p></div><span className="safe-state">✓ 全部安全</span></div>
            <div className="guardrail-grid">
              {[["退订率","0.31%","< 0.80%",39],["商家投诉率","0.09%","< 0.20%",45],["错误建议率","0.72%","< 1.00%",72],["人工转接率","4.8%","< 8.00%",60]].map(([name,value,limit,width]) => (
                <article key={name as string}><div><span>{name}</span><strong>{value}</strong></div><div className="guardrail-track"><i style={{width:`${width}%`}} /></div><small>安全阈值 {limit}</small></article>
              ))}
            </div>
          </section>

          <section className="panel evaluation-panel section-anchor" id="evaluation">
            <div className="panel-header strategy-heading">
              <div><h2>模型标注与评测</h2><p>评测集 v2.4 · 236 条商家案例 · 餐饮 / 零售 / 休闲娱乐</p></div>
              <div className="eval-summary"><span>综合得分</span><strong>4.65</strong><small>/ 5.00</small></div>
            </div>
            <div className="eval-layout">
              <div className="dimension-list">
                {evalDimensions.map(([name, score]) => (
                  <div className="dimension-row" key={name as string}><span>{name}</span><div><i style={{width:`${Number(score) / 5 * 100}%`}} /></div><strong>{Number(score).toFixed(2)}</strong></div>
                ))}
              </div>
              <aside className="annotation-card">
                <span>标注质量</span><div className="agreement-ring"><strong>0.86</strong><small>Krippendorff’s α</small></div>
                <p>3 名标注员重复标注 60 条案例，整体一致性达到“高度一致”。</p>
                <dl><div><dt>已完成</dt><dd>236 / 300</dd></div><div><dt>严重错误</dt><dd className="danger-text">3 条</dd></div><div><dt>待仲裁</dt><dd>7 条</dd></div></dl>
              </aside>
            </div>
            <div className="case-table-wrap">
              <table className="case-table"><thead><tr><th>案例</th><th>行业 / 问题</th><th>模型建议摘要</th><th>评分</th><th>风险</th><th>状态</th></tr></thead>
              <tbody>
                <tr><td>#C-0218</td><td><strong>餐饮</strong><span>转化下降</span></td><td>晚市限时价 + 套餐分量优化</td><td><b>4.8</b> / 5</td><td><span className="risk low">低</span></td><td><span className="reviewed">已通过</span></td></tr>
                <tr><td>#R-0086</td><td><strong>零售</strong><span>库存积压</span></td><td>建议直接降价 30% 清仓</td><td><b>3.1</b> / 5</td><td><span className="risk high">高</span></td><td><span className="arbitration">待仲裁</span></td></tr>
                <tr><td>#E-0142</td><td><strong>休闲娱乐</strong><span>闲时低利用</span></td><td>工作日下午定向券包实验</td><td><b>4.6</b> / 5</td><td><span className="risk low">低</span></td><td><span className="reviewed">已通过</span></td></tr>
              </tbody></table>
            </div>
          </section>

          <section className="prompt-grid section-anchor" id="prompt-management">
            <div className="panel prompt-panel">
              <div className="panel-header"><div><h2>Prompt 版本管理</h2><p>商家异常诊断与主动触达策略</p></div><button>查看全部版本</button></div>
              <div className="prompt-version active-version"><div className="version-mark">v2.4</div><div><strong>具体损失 + 原因假设 + 行动建议</strong><p>当前线上版本 · 2026-07-18 发布</p></div><span>100% 流量</span></div>
              <div className="prompt-version"><div className="version-mark">v2.3</div><div><strong>增加行业语气与高风险确认规则</strong><p>历史版本 · 运行 21 天</p></div><span>已归档</span></div>
              <div className="prompt-code"><header><span>核心指令片段</span><button onClick={() => setNotice("Prompt 已复制")}>复制</button></header><pre>{`角色：本地生活商家经营顾问\n目标：基于已提供的数据定位经营问题\n要求：\n1. 先引用事实，再提出原因假设\n2. 建议必须具体、可执行、可验证\n3. 禁止虚构数据或承诺经营效果\n4. 价格、预算等高风险操作必须二次确认`}</pre></div>
            </div>
            <div className="panel release-panel">
              <div className="panel-header"><div><h2>上线准入检查</h2><p>v2.5 候选版本</p></div><span className="pending-state">6 / 8 通过</span></div>
              {[["离线评测 ≥ 4.5",true],["错误建议率 < 1%",true],["高风险确认覆盖率 100%",true],["A/B 实验显著性 > 95%",true],["投诉率无显著上升",true],["人工审核 100 条",true],["零售行业回归测试",false],["负责人最终审批",false]].map(([label,passed]) => <div className="check-row" key={label as string}><span className={passed ? "passed" : "waiting"}>{passed ? "✓" : "○"}</span><strong>{label}</strong><small>{passed ? "通过" : "待完成"}</small></div>)}
              <button className="release-button" disabled>完成检查后发布</button>
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}
