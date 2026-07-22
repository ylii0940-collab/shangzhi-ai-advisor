"use client";

import { FormEvent, useMemo, useState } from "react";

type Message = { role: "assistant" | "merchant"; text: string };

const navItems = ["经营总览", "AI 顾问", "数据分析", "营销中心", "评价管理"];

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
              onClick={() => setActiveNav(item)}
              className={activeNav === item ? "nav-item active" : "nav-item"}
            >
              <span className="nav-icon">{["⌂", "✦", "⌁", "◎", "◇"][index]}</span>
              {item}
              {item === "AI 顾问" && <em>3</em>}
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

        <div className="dashboard-grid">
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
      </section>
    </main>
  );
}
