# 商智 AI 经营顾问

面向本地生活商家的完整 AI 产品经理作品集。公开前端包含经营总览、调研策略、
完整转化漏斗、A/B 实验、Prompt 版本、模型评测与人工标注工作台；Python
后端位于 `python_shangzhi/`，使用 FastAPI、LangChain、LangGraph、OpenAI
Responses API、SQLite 记忆和人工确认门。

## Prerequisites

- Node.js `>=22.13.0`

## 启动完整前后端

macOS 可直接双击根目录的 `启动完整项目.command`，它会安装缺少的依赖、
同时启动完整前端和 Python Agent，并打开 `http://127.0.0.1:3000`。
需要启用真实模型时，先双击 `配置大模型.command` 写入后端密钥。

也可以分别手动启动：

```bash
npm install
npm run dev
```

另开终端启动 Python Agent：

```bash
cd python_shangzhi
./启动商智.command
```

在前端根目录创建本地 `.env.local`：

```dotenv
AGENT_API_URL=http://127.0.0.1:8000
```

然后访问 `http://localhost:3000`。浏览器只请求同源 `/api/agent/*`，Vinext
服务端再转发给 Python，因此 OpenAI Key 不会进入前端。

如果没有配置 `AGENT_API_URL`，完整页面仍会以明确标识的 `DEMO` 模式运行；
如果 Python 服务暂时不可用，会显示 `FALLBACK`，不会伪装成真实模型。

## 构建

```bash
npm run dev
npm run build
```

This starter does not use `wrangler.jsonc`.

## Included Shape

- edit site code under `app/`
- `.openai/hosting.json` declares optional Sites D1 and R2 bindings
- `vite.config.ts` simulates declared bindings for local development
- `db/schema.ts` starts intentionally empty
- `examples/d1/` contains an optional D1 example surface
- `drizzle.config.ts` supports local migration generation when needed

## Workspace Auth Headers

OpenAI workspace sites can read the current user's email from
`oai-authenticated-user-email`.

SIWC-authenticated workspace sites may also receive
`oai-authenticated-user-full-name` when the user's SIWC profile has a non-empty
`name` claim. The full-name value is percent-encoded UTF-8 and is accompanied by
`oai-authenticated-user-full-name-encoding: percent-encoded-utf-8`.

Treat the full name as optional and fall back to email when it is absent:

```tsx
import { headers } from "next/headers";

export default async function Home() {
  const requestHeaders = await headers();
  const email = requestHeaders.get("oai-authenticated-user-email");
  const encodedFullName = requestHeaders.get("oai-authenticated-user-full-name");
  const fullName =
    encodedFullName &&
    requestHeaders.get("oai-authenticated-user-full-name-encoding") ===
      "percent-encoded-utf-8"
      ? decodeURIComponent(encodedFullName)
      : null;

  const displayName = fullName ?? email;
  // ...
}
```

## Optional Dispatch-Owned ChatGPT Sign-In

Import the ready-to-use helpers from `app/chatgpt-auth.ts` when the site needs
optional or required ChatGPT sign-in:

- Use `getChatGPTUser()` for optional signed-in UI.
- Use `requireChatGPTUser(returnTo)` for server-rendered pages that should send
  anonymous visitors through Sign in with ChatGPT.
- Use `chatGPTSignInPath(returnTo)` and `chatGPTSignOutPath(returnTo)` for
  browser links or actions.
- Pass a same-origin relative `returnTo` path for the destination after sign-in
  or sign-out. The helper validates and safely encodes it.
- Mark protected pages with `export const dynamic = "force-dynamic"` because
  they depend on per-request identity headers.

Dispatch owns `/signin-with-chatgpt`, `/signout-with-chatgpt`, `/callback`, the
OAuth cookies, and identity header injection. Do not implement app routes for
those reserved paths. Routes that do not import and call the helper remain
anonymous-compatible.

SIWC establishes identity only; it does not prove workspace membership. Use the
Sites hosting platform's access policy controls for workspace-wide restrictions,
or enforce explicit server-side membership or allowlist checks.

Use SIWC for account pages, user-specific dashboards, saved records, and write
actions tied to the current ChatGPT user. Leave public content anonymous.

## Useful Commands

- `npm run dev`: start local development
- `npm run build`: verify the vinext build output
- `npm test`: build the starter and verify its rendered loading skeleton
- `npm run db:generate`: generate Drizzle migrations after schema changes

## Learn More

- [vinext Documentation](https://github.com/cloudflare/vinext)
- [Drizzle D1 Guide](https://orm.drizzle.team/docs/get-started/d1-new)
