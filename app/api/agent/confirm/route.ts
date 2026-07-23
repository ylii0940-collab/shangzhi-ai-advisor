export const runtime = "edge";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}));
  if (typeof payload.action_id !== "string" || typeof payload.approved !== "boolean") {
    return Response.json({ ok: false, error: "行动确认参数不完整" }, { status: 400 });
  }

  const backendUrl = process.env.AGENT_API_URL?.replace(/\/+$/, "");
  if (backendUrl && !payload.action_id.startsWith("action_web_")) {
    try {
      const upstream = await fetch(`${backendUrl}/api/agent/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (upstream.ok) {
        return new Response(upstream.body, {
          status: upstream.status,
          headers: { "Content-Type": "application/json", "X-Agent-Backend": "python-langgraph" },
        });
      }
    } catch {
      return Response.json({ ok: false, error: "Python Agent 确认服务暂时不可用" }, { status: 502 });
    }
  }

  return Response.json({
    ok: true,
    mode: "demo",
    action: {
      id: payload.action_id,
      status: payload.approved ? "executed" : "rejected",
    },
    message: payload.approved ? "已确认并完成模拟执行" : "已拒绝，不会执行任何变更",
  });
}
