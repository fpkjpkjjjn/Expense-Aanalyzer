import axios from "axios";
import { API_BASE_URL } from "../config";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

/**
 * Проверяет, доступен ли сервер.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await client.get("/api/health");
    return response.data?.status === "ok";
  } catch (e) {
    return false;
  }
}

/**
 * Отправляет список введённых вручную трат на сервер и возвращает анализ.
 * @param {Array<{date: string, description: string, amount: number}>} transactions
 * @returns {Promise<{total: number, by_category: Array, by_week: Array, top_transactions: Array}>}
 */
export async function analyzeTransactions(transactions) {
  const response = await client.post("/api/analyze-transactions", {
    transactions,
  });
  return response.data;
}

export default client;
