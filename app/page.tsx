"use client";

import { FormEvent, useMemo, useState } from "react";

type Message = { role: "assistant" | "merchant"; text: string };

const navItems = ["经营总览", "调研策略", "策略看板", "A/B 实验", "实验配置", "标注工作台", "作品集资料"];

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
  const [industry, setIndustry] = useState("餐饮");
  const [traffic, setTraffic] = useState(50);
  const [annotationIndex, setAnnotationIndex] = useState(0);
  const [scores, setScores] = useState([4, 5, 4, 4, 5, 4, 5, 5]);
  const [severeError, setSevereError] = useState(false);

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
      "调研策略": "research-strategy",
      "策略看板": "strategy-dashboard",
      "A/B 实验": "ab-experiment",
      "实验配置": "experiment-builder",
      "标注工作台": "annotation-workbench",
      "作品集资料": "portfolio-assets",
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
              <span className="nav-icon">{["⌂", "◎", "▥", "A", "⚗", "✓", "↓"][index]}</span>
              {item}
              {item === "标注工作台" && <em>7</em>}
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

          <section className="panel research-panel section-anchor" id="research-strategy">
            <div className="panel-header strategy-heading">
              <div><span className="module-index">01 / DISCOVERY</span><h2>商家调研与行业差异化策略</h2><p>5 位模拟访谈对象 · 3 个细分行业 · 结论用于原型验证，不代表真实线上调研</p></div>
              <div className="industry-tabs" role="tablist">{["餐饮","零售","休闲娱乐"].map(item => <button role="tab" aria-selected={industry===item} className={industry===item?"selected":""} onClick={()=>setIndustry(item)} key={item}>{item}</button>)}</div>
            </div>
            <div className="research-grid">
              <article className="persona-card"><div className="persona-head"><div className="holo-avatar">{industry.slice(0,1)}</div><div><span>核心用户画像</span><h3>{industry === "餐饮" ? "李店长 · 单店经营者" : industry === "零售" ? "周老板 · 社区零售商" : "陈经理 · 娱乐门店运营"}</h3><p>{industry === "餐饮" ? "每天只能抽出 20 分钟看数据，希望系统直接告诉他先做什么。" : industry === "零售" ? "SKU多、库存周转慢，最关心哪些商品需要补货或促销。" : "工作日闲时利用率低，希望通过预约与分时活动提升产能。"}</p></div></div><blockquote>“{industry === "餐饮" ? "别只告诉我转化下降，告诉我是套餐、评价还是价格的问题。" : industry === "零售" ? "我不缺报表，缺的是今天该处理哪十个商品。" : "周末不缺客流，最难的是怎么把工作日下午卖出去。"}”</blockquote></article>
              <div className="insight-stack">
                {(industry === "餐饮" ? [["套餐转化","高频","价格/分量/差评联动"],["评价管理","高痛","负向主题与回复"],["老客复购","增长","定向召回与券包"]] : industry === "零售" ? [["库存积压","高频","滞销诊断与清仓"],["爆款缺货","高痛","库存水位提醒"],["选品促销","增长","SKU级行动建议"]] : [["闲时利用","高频","分时定价与券包"],["预约爽约","高痛","预测与提醒"],["组合套餐","增长","场景化活动设计"]]).map(([title,badge,desc],i)=><article key={title}><span className={`insight-no n${i+1}`}>0{i+1}</span><div><strong>{title}</strong><p>{desc}</p></div><b>{badge}</b></article>)}
              </div>
              <aside className="interview-summary"><span>访谈样本</span>{[["李记小馆","餐饮 · 1店","18分钟"],["悦己便利","零售 · 3店","26分钟"],["乐玩桌游","休闲 · 2店","22分钟"],["巷口咖啡","餐饮 · 2店","20分钟"],["轻享SPA","休闲 · 4店","31分钟"]].map(([name,type,time])=><div key={name}><i>{name.slice(0,1)}</i><p><strong>{name}</strong><small>{type}</small></p><span>{time}</span></div>)}</aside>
            </div>
            <div className="journey-line">{["发现异常","理解原因","评估方案","确认执行","复盘效果"].map((step,i)=><div key={step}><span>{i+1}</span><strong>{step}</strong><small>{["主动提醒","证据解释","影响/风险","二次确认","增量归因"][i]}</small></div>)}</div>
          </section>

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

          <section className="panel experiment-builder section-anchor" id="experiment-builder">
            <div className="panel-header strategy-heading"><div><span className="module-index">04 / EXPERIMENT BUILDER</span><h2>创建商家沟通策略实验</h2><p>完整配置触发条件、目标人群、Prompt、指标与安全护栏</p></div><span className="draft-badge">草稿自动保存</span></div>
            <div className="builder-steps">{["实验目标","人群与触发","策略与流量","指标与护栏"].map((step,i)=><div className={i<3?"done":"current"} key={step}><span>{i<3?"✓":i+1}</span><strong>{step}</strong></div>)}</div>
            <div className="builder-layout">
              <div className="builder-form">
                <label><span>实验名称</span><input defaultValue="经营异常具体损失型开场验证" /></label>
                <div className="form-pair"><label><span>目标行业</span><select><option>餐饮商家</option><option>零售商家</option><option>休闲娱乐</option></select></label><label><span>商家阶段</span><select><option>新商家 + 成长商家</option><option>全部商家</option><option>成熟商家</option></select></label></div>
                <label><span>触发条件</span><div className="condition-box"><b>当</b><select><option>套餐支付转化率</option></select><select><option>连续7日下降</option></select><input defaultValue="10%" /><button>＋</button></div></label>
                <div className="prompt-pair"><label><span>A组 · 基线Prompt</span><textarea defaultValue="您最近的经营数据存在异常，点击查看详情。" /></label><label><span>B组 · 实验Prompt</span><textarea defaultValue="您的套餐曝光上涨{{exposure_lift}}，但每天少成交约{{lost_orders}}单，可能与{{reason}}有关。我整理了3条优化建议。" /></label></div>
              </div>
              <aside className="traffic-card"><span>流量分配</span><div className="traffic-orbit"><strong>{traffic}%</strong><small>B组流量</small></div><input type="range" min="10" max="90" value={traffic} onChange={e=>setTraffic(Number(e.target.value))}/><div className="traffic-labels"><span>A组 {100-traffic}%</span><span>B组 {traffic}%</span></div><dl><div><dt>预计样本量</dt><dd>48,000</dd></div><div><dt>预计周期</dt><dd>14天</dd></div><div><dt>最小检测效应</dt><dd>+3.0pp</dd></div></dl></aside>
            </div>
            <div className="metric-selector"><div><span>主要指标</span>{["商家回复率","建议采纳率","任务完成率"].map(x=><label key={x}><input type="checkbox" defaultChecked />{x}</label>)}</div><div><span>护栏指标</span>{["退订率 < 0.8%","投诉率 < 0.2%","错误建议率 < 1%","人工转接率 < 8%"].map(x=><label key={x}><input type="checkbox" defaultChecked />{x}</label>)}</div><button onClick={()=>setNotice("实验草稿已创建，可进入审批流程")}>创建实验草稿 →</button></div>
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

          <section className="panel annotation-workbench section-anchor" id="annotation-workbench">
            <div className="panel-header strategy-heading"><div><span className="module-index">05 / HUMAN EVALUATION</span><h2>模型标注工作台</h2><p>CASE-{String(annotationIndex+86).padStart(4,"0")} · 150 条模拟评测集 · 当前进度 {annotationIndex+1}/150</p></div><div className="annotator"><span>标注员</span><strong>Reviewer 02</strong></div></div>
            <div className="annotation-layout">
              <div className="case-context"><header><span>商家案例</span><b>零售 · 库存积压 · 高风险</b></header><dl><div><dt>经营事实</dt><dd>即饮咖啡库存周转天数由 21 天升至 46 天，近 14 日销量下降 32%，毛利率 18%。</dd></div><div><dt>约束条件</dt><dd>商家最低可接受毛利率为 12%；价格或预算调整必须二次确认。</dd></div></dl><div className="model-answer"><span>模型回答 · Prompt v2.5-rc1</span><p>建议将即饮咖啡统一降价30%并立即上线清仓活动，预计7天内清理80%库存。</p></div><div className="evidence-alert"><span>!</span><p><strong>自动风险提示</strong>：建议价格会使毛利率低于商家约束，且包含未经依据验证的效果承诺。</p></div></div>
              <div className="score-form"><header><span>八维评分</span><small>1 = 严重不符合 · 5 = 完全符合</small></header>{["问题判断准确","数据引用正确","建议可执行","符合行业特点","无虚构数据","语气适合商家","无违规承诺","高风险操作确认"].map((name,i)=><div className="score-row-form" key={name}><span>{name}</span><div>{[1,2,3,4,5].map(score=><button className={scores[i]===score?"active":""} onClick={()=>setScores(current=>current.map((v,idx)=>idx===i?score:v))} key={score}>{score}</button>)}</div></div>)}</div>
              <aside className="error-panel"><span>严重错误标签</span>{["违反商家约束","虚构效果承诺","未要求二次确认","可能造成经济损失"].map(x=><label key={x}><input type="checkbox" checked={severeError} onChange={()=>setSevereError(!severeError)} />{x}</label>)}<label className="note-label"><span>标注说明</span><textarea defaultValue="建议改为分层折扣实验，并先测算12%毛利率约束下的最大折扣；上线前必须由商家确认。" /></label><div className="score-total"><span>综合得分</span><strong>{(scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(2)}</strong></div><button onClick={()=>{setAnnotationIndex(i=>Math.min(149,i+1));setNotice("标注已提交，已进入下一条案例")}}>提交并进入下一条</button></aside>
            </div>
          </section>

          <section className="portfolio-panel section-anchor" id="portfolio-assets">
            <div><span className="module-index">06 / DELIVERABLES</span><h2>求职作品集资料包</h2><p>从需求研究到评测数据，所有材料均可下载复盘。模拟数据已在文件中明确标注。</p></div>
            <div className="asset-grid"><a href="/assets/shangzhi-prd.docx" download><span>DOCX</span><strong>完整PRD</strong><small>背景、流程、需求、埋点、风险</small></a><a href="/assets/shangzhi-portfolio.pptx" download><span>PPTX</span><strong>面试汇报PPT</strong><small>12页完整项目故事线</small></a><a href="/assets/shangzhi-evaluation-dataset.xlsx" download><span>XLSX</span><strong>150条评测数据集</strong><small>案例、回答、八维评分与标签</small></a></div>
          </section>
        </section>
      </section>
    </main>
  );
}
