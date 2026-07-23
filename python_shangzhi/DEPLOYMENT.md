# 公开部署

项目已经包含 `Dockerfile` 和 `Procfile`，可部署到支持 Docker 或 Python Web
Service 的云平台。

## 必需环境变量

```text
OPENAI_API_KEY=服务器端密钥
OPENAI_MODEL=gpt-5.6-luna
OPENAI_REASONING_EFFORT=low
SHANGZHI_AGENT_MODE=live
SHANGZHI_ALLOWED_ORIGINS=https://shangzhi-ai-advisor.aft15679ty.chatgpt.site
```

生产环境建议再配置：

```text
PORT=8000
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=可选
LANGSMITH_PROJECT=shangzhi-ai-advisor
```

不要上传本地 `.env`、数据库或 `.venv`。它们已经被 `.gitignore` 和
`.dockerignore` 排除。

## Docker

```bash
docker build -t shangzhi-agent .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="你的服务器密钥" \
  -e SHANGZHI_AGENT_MODE=live \
  shangzhi-agent
```

访问：

```text
http://服务器地址:8000
```

部署完成后，把该 HTTPS 地址写入完整前端的服务器环境变量
`AGENT_API_URL`。公开页面通过同源 `/api/agent/*` 路由转发请求，API Key
始终只保留在 Python 服务端。

## 生产注意事项

- 当前 SQLite 适合作品集和单实例部署；多实例生产环境应换成 PostgreSQL。
- 当前内存限流适合单实例；多实例应换成 Redis。
- 建议在反向代理或云平台层启用 HTTPS、访问日志和请求大小限制。
- 不要把 API Key 写进 HTML、JavaScript、Git 或公开 ZIP。
- 高风险动作接口当前只做“模拟执行”，接入真实商家平台前必须增加身份认证、
  权限校验、幂等键、审计日志和回滚能力。
