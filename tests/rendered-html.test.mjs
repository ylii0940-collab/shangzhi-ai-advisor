import assert from "node:assert/strict";
import test from "node:test";

const workerUrl = new URL("../dist/server/index.js", import.meta.url);
workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
const { default: worker } = await import(workerUrl.href);

async function render(pathname) {
  return worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("renders the project introduction with two explicit product entrances", async () => {
  const response = await render("/");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /让商家从“看见数据”/);
  assert.match(html, /进入商家经营端/);
  assert.match(html, /进入AI产品运营后台/);
  assert.match(html, /所有经营指标、访谈、实验结果与行业基准均为模拟数据/);
});

test("renders the merchant workspace with merchant-only positioning", async () => {
  const response = await render("/merchant");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /app-shell merchant-view/);
  assert.match(html, /当前身份：<!-- -->模拟商家/);
  assert.match(html, /商圈套餐竞品分析/);
  assert.match(html, /仅展示“李记小馆”自己的模拟经营数据/);
});

test("renders the internal AI operations console with version benchmarking", async () => {
  const response = await render("/ops");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /app-shell ops-view/);
  assert.match(html, /当前身份：<!-- -->AI 产品内部运营人员/);
  assert.match(html, /Agent 版本基准测试/);
  assert.match(html, /当前版本、历史版本与无工具基线/);
});
