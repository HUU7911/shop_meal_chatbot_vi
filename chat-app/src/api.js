import { API_URL, REQUEST_FIELD, REPLY_FIELDS } from "./config";

function pickReply(data) {
  if (typeof data === "string") return data;
  for (const f of REPLY_FIELDS) {
    if (data && typeof data[f] === "string" && data[f].trim()) return data[f];
  }
  return null;
}

export async function sendMessage(text) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [REQUEST_FIELD]: text }),
  });
  if (!res.ok) throw new Error("HTTP " + res.status);
  const data = await res.json();
  const reply = pickReply(data);
  if (!reply) throw new Error("Phản hồi không có nội dung câu trả lời");
  return {
    reply,
    intent: data.intent,
    confidence: data.confidence != null ? Number(data.confidence).toFixed(2) : "",
  };
}

export async function checkHealth() {
  try {
    const res = await fetch(new URL("/health", new URL(API_URL, location.href)));
    return res.ok;
  } catch {
    return false;
  }
}
