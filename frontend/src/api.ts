import type { ApiEnvelope, QuoteData, TariffBoard } from "./types";

async function readEnvelope<T>(response: Response): Promise<ApiEnvelope<T>> {
  const body = (await response.json()) as ApiEnvelope<T>;
  return body;
}

export async function fetchHealth(): Promise<boolean> {
  const response = await fetch("/api/v1/health");
  if (!response.ok) {
    return false;
  }
  const body = await readEnvelope<{ status: string }>(response);
  return body.success && body.data?.status === "up";
}

export async function fetchTariffs(): Promise<TariffBoard> {
  const response = await fetch("/api/v1/tariffs");
  const body = await readEnvelope<TariffBoard>(response);
  if (!body.success || !body.data) {
    throw new Error(body.message);
  }
  return body.data;
}

export function requestQuote(payload: {
  weight_kg: string;
  client_type: string;
  shipping_type: string;
}): Promise<ApiEnvelope<QuoteData>> {
  return fetch("/api/v1/quotes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((response) => readEnvelope<QuoteData>(response));
}
