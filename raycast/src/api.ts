import { getPreferenceValues } from "@raycast/api";
import { showFailureToast } from "@raycast/utils";
import { ApiKeyJson, Preferences } from "./types";

// Module-level token cache
let cachedAccessToken: string | null = null;
let tokenFetchedAt: number | null = null;
const TOKEN_TTL_MS = 55 * 60 * 1000; // 55 minutes (token valid 60 min)

async function getAccessToken(): Promise<string> {
  const now = Date.now();
  if (cachedAccessToken && tokenFetchedAt && now - tokenFetchedAt < TOKEN_TTL_MS) {
    return cachedAccessToken;
  }

  const prefs = getPreferenceValues<Preferences>();
  let apiKey: ApiKeyJson;
  try {
    apiKey = JSON.parse(prefs.apiKey) as ApiKeyJson;
  } catch {
    throw new Error("Invalid API key JSON in preferences");
  }

  const { region, client_id, refresh_token } = apiKey;

  const response = await fetch(`https://cognito-idp.${region}.amazonaws.com/`, {
    method: "POST",
    headers: {
      "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
      "Content-Type": "application/x-amz-json-1.1",
    },
    body: JSON.stringify({
      AuthFlow: "REFRESH_TOKEN_AUTH",
      AuthParameters: {
        REFRESH_TOKEN: refresh_token,
      },
      ClientId: client_id,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Cognito auth failed (${response.status}): ${text}`);
  }

  const data = (await response.json()) as { AuthenticationResult: { AccessToken: string } };
  cachedAccessToken = data.AuthenticationResult.AccessToken;
  tokenFetchedAt = Date.now();
  return cachedAccessToken;
}

function getBaseUrl(): string {
  const prefs = getPreferenceValues<Preferences>();
  return prefs.apiUrl.replace(/\/$/, "");
}

async function buildHeaders(auth: boolean): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (auth) {
    const token = await getAccessToken();
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function apiGet<T>(path: string, auth = true): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  try {
    const headers = await buildHeaders(auth);
    const response = await fetch(url, { method: "GET", headers });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`GET ${path} failed (${response.status}): ${text}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    await showFailureToast(error, { title: "API Request Failed" });
    throw error;
  }
}

// Like apiGet but returns null on 404 instead of throwing.
export async function apiGetNullable<T>(path: string, auth = true): Promise<T | null> {
  const url = `${getBaseUrl()}${path}`;
  try {
    const headers = await buildHeaders(auth);
    const response = await fetch(url, { method: "GET", headers });
    if (response.status === 404) return null;
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`GET ${path} failed (${response.status}): ${text}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    await showFailureToast(error, { title: "API Request Failed" });
    throw error;
  }
}

export async function apiPost<T>(path: string, body: unknown, auth = true): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  try {
    const headers = await buildHeaders(auth);
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`POST ${path} failed (${response.status}): ${text}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    await showFailureToast(error, { title: "API Request Failed" });
    throw error;
  }
}

export async function apiPut<T>(path: string, body: unknown, auth = true): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  try {
    const headers = await buildHeaders(auth);
    const response = await fetch(url, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`PUT ${path} failed (${response.status}): ${text}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    await showFailureToast(error, { title: "API Request Failed" });
    throw error;
  }
}

export function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function toISODate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
