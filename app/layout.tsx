import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const imageUrl = `${protocol}://${host}/og-v3.png`;

  return {
    title: "商智 · AI 经营顾问",
    description: "从商家经营诊断到 Prompt 实验、A/B 测试、标注评测与任务执行的完整 AI 产品经理作品集。",
    icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
    openGraph: {
      title: "商智 · AI 经营顾问",
      description: "从经营异常到可执行行动：研究、Prompt、实验、评测和安全治理闭环。",
      type: "website",
      locale: "zh_CN",
      images: [{ url: imageUrl, width: 1200, height: 630, alt: "商智 AI 经营顾问" }],
    },
    twitter: {
      card: "summary_large_image",
      title: "商智 · AI 经营顾问",
      description: "从经营异常到可执行行动：研究、Prompt、实验、评测和安全治理闭环。",
      images: [imageUrl],
    },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
