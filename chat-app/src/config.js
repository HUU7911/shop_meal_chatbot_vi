export const API_URL = import.meta.env.VITE_API_URL || "/chat";
export const REQUEST_FIELD = "message"; // tên trường gửi đi
export const REPLY_FIELDS = ["reply", "response", "answer", "message"]; // tên trường chứa câu trả lời
export const STORE_KEY = "shopmeal_chat_v1";
export const MAX_STORED = 100;