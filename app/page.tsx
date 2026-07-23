import Link from "next/link";

const capabilities = [
  ["01", "经营异常诊断", "从订单、曝光、转化、评价和活动数据中定位问题。"],
  ["02", "可解释 Agent", "先引用证据，再提出原因假设和可执行建议。"],
  ["03", "实验验证", "通过 Prompt A/B 测试验证回复、采纳和任务完成。"],
  ["04", "质量治理", "用评测集、Badcase、Trace 和人工标注控制风险。"],
];

export default function ProjectHome() {
  return (
    <main className="case-home">
      <div className="case-ambient" aria-hidden="true"><i /><i /><i /><i /></div>
      <header className="case-nav">
        <Link className="case-brand" href="/">
          <span>商</span><div><strong>商智</strong><small>AI 经营顾问</small></div>
        </Link>
        <nav aria-label="项目页面导航">
          <a href="#project">项目说明</a>
          <a href="#architecture">产品架构</a>
          <a href="#materials">作品集资料</a>
        </nav>
        <Link className="case-nav-cta" href="/merchant">进入产品 Demo →</Link>
      </header>

      <section className="case-hero" id="project">
        <div className="case-hero-copy">
          <span className="case-kicker">AI PRODUCT MANAGER PORTFOLIO · 原型项目</span>
          <h1>让商家从“看见数据”<br />走到“完成行动”</h1>
          <p>商智是一套面向本地生活商家的 AI 经营顾问原型。它使用模拟经营数据，演示 Agent 如何发现异常、检索证据、生成建议、请求人工确认，并通过实验与评测持续迭代。</p>
          <div className="case-disclosure">
            <strong>项目边界</strong>
            <span>未正式上线 · 无真实商家数据 · 所有经营指标、访谈、实验结果与行业基准均为模拟数据</span>
          </div>
          <div className="case-actions">
            <Link href="/merchant"><span>商家视角</span><strong>进入商家经营端</strong><small>我的门店 · AI建议 · 任务 · 商圈竞品</small></Link>
            <Link href="/ops"><span>内部视角</span><strong>进入AI产品运营后台</strong><small>漏斗 · 实验 · 评测 · Badcase · 监控</small></Link>
          </div>
        </div>
        <div className="case-hero-visual">
          <div className="case-orbit"><i /><i /><i /><strong>AI</strong></div>
          <article className="floating-card fc-one"><span>经营异常</span><strong>转化率 -18%</strong><small>曝光上涨但支付下降</small></article>
          <article className="floating-card fc-two"><span>证据检索</span><strong>3 个工具完成</strong><small>指标 · 评价 · 行业基准</small></article>
          <article className="floating-card fc-three"><span>安全确认</span><strong>等待商家操作</strong><small>预算与改价不自动执行</small></article>
        </div>
      </section>

      <section className="case-section" id="architecture">
        <div className="case-section-title"><span>01 / PRODUCT LOGIC</span><h2>同一个产品，两类使用者，两个独立入口</h2><p>商家只看自己的门店；内部团队只看匿名汇总的产品效果和模型质量。</p></div>
        <div className="role-boundary">
          <article>
            <span>MERCHANT WORKSPACE</span><h3>商家经营端</h3>
            <p>回答“我的店出了什么问题，我应该先做什么？”</p>
            <ul><li>门店经营总览</li><li>AI经营诊断与证据</li><li>高风险操作确认</li><li>今日任务与商圈竞品</li></ul>
            <Link href="/merchant">查看商家端 →</Link>
          </article>
          <div className="boundary-line"><span>权限隔离</span><i /><b>merchant_id</b><i /><span>匿名汇总</span></div>
          <article>
            <span>AI OPERATIONS CONSOLE</span><h3>AI产品运营后台</h3>
            <p>回答“这个AI产品效果如何，下一版应该怎么改？”</p>
            <ul><li>沟通转化漏斗</li><li>Prompt与A/B实验</li><li>能力评测与Badcase</li><li>Trace、成本和人工标注</li></ul>
            <Link href="/ops">查看运营后台 →</Link>
          </article>
        </div>
        <div className="capability-strip">
          {capabilities.map(([index, title, detail]) => <article key={index}><span>{index}</span><strong>{title}</strong><p>{detail}</p></article>)}
        </div>
      </section>

      <section className="case-section workflow-section">
        <div className="case-section-title"><span>02 / AGENT LOOP</span><h2>完整经营闭环</h2></div>
        <div className="case-workflow">
          {[
            ["发现异常", "套餐曝光 +12%，支付转化 -18%"],
            ["检索证据", "查询评价、活动、库存和行业基准"],
            ["生成建议", "输出原因假设、行动步骤和验证指标"],
            ["人工确认", "预算、改价、发券等操作必须确认"],
            ["实验复盘", "跟踪采纳、完成和经营改善"],
          ].map(([title, detail], index) => <article key={title}><i>{index + 1}</i><strong>{title}</strong><p>{detail}</p></article>)}
        </div>
      </section>

      <section className="case-section materials-section" id="materials">
        <div className="case-section-title"><span>03 / DELIVERABLES</span><h2>作品集资料</h2><p>所有材料都按照“模拟数据项目”口径编写，用于求职展示与面试复盘。</p></div>
        <div className="case-assets">
          <a href="/assets/shangzhi-prd.docx" download><span>DOCX</span><strong>完整 PRD</strong><small>背景、用户、流程、需求、埋点与风险</small></a>
          <a href="/assets/shangzhi-portfolio.pptx" download><span>PPTX</span><strong>面试汇报 PPT</strong><small>12页项目故事线与产品决策</small></a>
          <a href="/assets/shangzhi-evaluation-dataset.xlsx" download><span>XLSX</span><strong>模拟评测数据集</strong><small>案例、回答、八维评分与错误标签</small></a>
        </div>
      </section>

      <footer className="case-footer"><strong>商智 · AI 经营顾问</strong><span>AI 产品经理原型项目 · 数据均为模拟</span></footer>
    </main>
  );
}
