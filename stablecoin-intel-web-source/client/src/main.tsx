import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// 仅当配置了分析时注入 Umami，避免未设置 env 时产生 Malformed URI 请求
const endpoint = import.meta.env.VITE_ANALYTICS_ENDPOINT;
const websiteId = import.meta.env.VITE_ANALYTICS_WEBSITE_ID;
if (endpoint && websiteId && typeof document !== "undefined") {
  const script = document.createElement("script");
  script.defer = true;
  script.src = `${endpoint.replace(/\/$/, "")}/umami.js`;
  script.setAttribute("data-website-id", websiteId);
  document.body.appendChild(script);
}

createRoot(document.getElementById("root")!).render(<App />);
