type StreamEvent = Record<string, unknown>;

const encoder = new TextEncoder();

function encodeEvent(event: StreamEvent) {
  return encoder.encode(`event: ${String(event.type ?? "message")}\ndata: ${JSON.stringify(event)}\n\n`);
}

function demoResult(message: string, mode: "demo" | "fallback" = "demo") {
  const normalized = message.toLowerCase();
  const isBudget = /预算|推广|投放|活动|券/.test(normalized);
  const isReview = /差评|评价|回复/.test(normalized);
  const threadId = `thread_web_${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`;
  const actionId = `action_web_${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`;

  const evidence = [
    {
      evidence_id: "E1",
      metric: "招牌双人餐曝光",
      observed: "18,420",
      comparison: "近 7 日上涨 12%",
      source: "get_metric_snapshot",
    },
    {
      evidence_id: "E2",
      metric: "套餐支付转化率",
      observed: "7.8%",
      comparison: "环比下降 18%；低于同商圈中位数 9.1%",
      source: "get_metric_snapshot + get_industry_benchmark",
    },
    {
      evidence_id: "E3",
      metric: "负向评价",
      observed: "近 30 日 14 条",
      comparison: "首要主题“分量不足”6 条",
      source: "get_review_topics",
    },
  ];

  const recommendation = isBudget
    ? {
        title: "建立小流量预算实验",
        rationale: "历史活动存在增量信号，但证据不足以支持直接扩大预算，需要先控制流量和预算上限。",
        steps: ["实验组预算只提高 10%", "仅分配 20% 流量并运行 7 天", "同步监控边际 ROI、退款率和获客成本"],
        expected_signal: "边际 ROI 为正且退款率稳定时再申请扩量",
        action_type: "budget",
        risk_level: "high",
        requires_confirmation: true,
      }
    : isReview
      ? {
          title: "先修正套餐表达，再小范围验证评价回复",
          rationale: "负向评价集中在分量和套餐说明，与转化下降同时出现，但尚不能直接证明因果。",
          steps: ["按主题抽查评价原文", "起草三类回复模板", "先由商家审核 10 条再扩大范围"],
          expected_signal: "观察回复率、二次投诉率和套餐页咨询主题",
          action_type: "reply",
          risk_level: "medium",
          requires_confirmation: true,
        }
      : {
          title: "开展 7 天套餐转化实验",
          rationale: "曝光增长但支付转化下降，优先验证价格感知和分量表达比直接降价更稳妥。",
          steps: ["保留原套餐作为对照组", "实验组强化分量和适用人数说明", "每天复盘支付转化、退款率和客诉"],
          expected_signal: "支付转化提升且退款率、客诉率不恶化",
          action_type: "campaign",
          risk_level: "high",
          requires_confirmation: true,
        };

  return {
    thread_id: threadId,
    message_id: `msg_${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`,
    mode,
    model: mode === "fallback" ? "python-agent → offline-rule-engine" : "offline-rule-engine",
    intent: isBudget ? "campaign" : isReview ? "review" : "overview",
    answer: isBudget
      ? "建议先做小流量预算实验，不要直接扩大投放。实验组仅提高 10% 预算，并设置 7 天观察窗口。"
      : isReview
        ? "评价侧最值得优先处理的是“分量不足”和“套餐说明不清”。建议先修正文案并小范围验证回复模板。"
        : "曝光上涨但支付转化下降，建议先开展 7 天对照实验，验证套餐表达和价格感知，不直接承诺确定效果。",
    evidence,
    hypotheses: ["套餐表达造成预期偏差", "近期负向评价影响支付决策"],
    recommendations: [recommendation],
    safety: {
      level: recommendation.risk_level,
      passed: true,
      requires_confirmation: true,
      warnings: ["涉及预算、活动或批量操作，必须由商家确认"],
      blocked_reasons: [],
    },
    actions: [
      {
        action_id: actionId,
        title: recommendation.title,
        action_type: recommendation.action_type,
        status: "pending",
        risk_level: recommendation.risk_level,
        payload: { steps: recommendation.steps, auto_execute: false },
      },
    ],
    confidence: 0.84,
    assumptions: ["演示数据来自内置模拟商家快照"],
    missing_data: ["真实订单明细", "活动边际成本"],
    trace: [
      { node: "retrieve", label: "经营数据检索", status: "completed" },
      { node: "diagnose", label: "离线可审计诊断", status: "completed" },
      { node: "guardrail", label: "证据与风险审核", status: "completed" },
      { node: "persist", label: "行动记录", status: "completed" },
    ],
  };
}

function demoStream(message: string, mode: "demo" | "fallback" = "demo") {
  const result = demoResult(message, mode);
  const events: StreamEvent[] = [
    { type: "start", thread_id: result.thread_id, mode, model: result.model },
    { type: "step", node: "retrieve", label: "检索商家经营数据", status: "completed" },
    { type: "step", node: "diagnose", label: mode === "fallback" ? "服务降级诊断" : "生成可审计经营诊断", status: "completed" },
    { type: "step", node: "guardrail", label: "检查证据、承诺与操作风险", status: "completed" },
    { type: "step", node: "persist", label: "保存待确认行动", status: "completed" },
    { type: "final", data: result },
  ];

  return new ReadableStream({
    async start(controller) {
      for (const event of events) {
        controller.enqueue(encodeEvent(event));
        await new Promise((resolve) => setTimeout(resolve, 140));
      }
      controller.close();
    },
  });
}

export const runtime = "edge";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}));
  const message = typeof payload.message === "string" ? payload.message.trim() : "";
  if (!message || message.length > 1200) {
    return Response.json({ ok: false, error: "请输入 1–1200 个字符" }, { status: 400 });
  }

  const backendUrl = process.env.AGENT_API_URL?.replace(/\/+$/, "");
  if (backendUrl) {
    try {
      const upstream = await fetch(`${backendUrl}/api/agent/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(payload),
      });
      if (upstream.ok && upstream.body) {
        return new Response(upstream.body, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "X-Agent-Backend": "python-langgraph",
          },
        });
      }
    } catch {
      // The public demo remains usable and is explicitly marked FALLBACK.
    }
    return new Response(demoStream(message, "fallback"), {
      headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
    });
  }

  return new Response(demoStream(message), {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
