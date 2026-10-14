const MCP_URL = "https://mcp.soccerverse.com/mcp";

type McpOptions = { timeoutMs?: number; retries?: number };
const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));
const messageOf = (error: unknown) => error instanceof Error ? error.message : String(error);

function parseToolPayload(payload: any, toolName: string): any {
  if (payload?.error) {
    const detail = payload.error.data?.details ?? payload.error.data?.message ?? payload.error.data ?? payload.error.message ?? "JSON-RPC error";
    const code = payload.error.code !== undefined ? ` (code ${payload.error.code})` : "";
    throw new Error(`MCP ${toolName}: ${String(detail)}${code}`);
  }
  const result = payload?.result;
  if (!result) throw new Error(`MCP ${toolName}: missing result`);
  if (result.isError === true) throw new Error(`MCP ${toolName}: tool reported an error`);

  const item = Array.isArray(result.content)
    ? result.content.find((entry: any) => entry?.type === "text")
    : undefined;
  let value: any;
  if (item?.text) {
    try { value = JSON.parse(item.text); }
    catch { throw new Error(`MCP ${toolName}: tool returned invalid JSON text`); }
  } else if (result.structuredContent && typeof result.structuredContent === "object") {
    value = result.structuredContent;
  } else {
    throw new Error(`MCP ${toolName}: missing tool content`);
  }
  if (value?.success === false || value?.error) {
    throw new Error(`MCP ${toolName}: ${String(value.error ?? "success:false")}`);
  }
  return value;
}

function parseBody(body: string, toolName: string): any {
  const trimmed = body.trim();
  if (!trimmed) throw new Error(`MCP ${toolName}: empty response`);

  // SSE may begin with "event:" rather than "data:".
  const lines = trimmed.split(/\r?\n/);
  const isSse = lines.some((line) =>
    /^(event|data|id|retry):/.test(line) || line.startsWith(":"),
  );

  if (!isSse) {
    let payload: any;
    try {
      payload = JSON.parse(trimmed);
    } catch {
      throw new Error(`MCP ${toolName}: invalid JSON response`);
    }
    return parseToolPayload(payload, toolName);
  }

  // Multiple data: lines within one event are joined with a newline.
  // Blank lines delimit events; ignore comments/keepalives and inspect later events.
  const events: string[] = [];
  let dataLines: string[] = [];
  const flushEvent = () => {
    if (dataLines.length > 0) events.push(dataLines.join("\n"));
    dataLines = [];
  };

  for (const line of lines) {
    if (line === "") {
      flushEvent();
      continue;
    }
    if (line.startsWith(":")) continue;
    if (line.startsWith("data:")) {
      let value = line.slice(5);
      if (value.startsWith(" ")) value = value.slice(1);
      dataLines.push(value);
    }
  }
  flushEvent();

  let lastError: unknown;
  for (const data of events) {
    const value = data.trim();
    if (!value || value === "[DONE]") continue;
    try {
      return parseToolPayload(JSON.parse(value), toolName);
    } catch (error) {
      lastError = error;
    }
  }
  if (lastError instanceof Error) throw lastError;
  throw new Error(`MCP ${toolName}: no valid data event in SSE response`);
}

function retryDelay(response: Response | null, attempt: number): number {
  const header = response?.headers.get("retry-after");
  if (header) {
    const seconds = Number(header);
    if (Number.isFinite(seconds) && seconds >= 0) return Math.min(seconds * 1000, 5000);
    const date = Date.parse(header);
    if (Number.isFinite(date)) return Math.max(0, Math.min(date - Date.now(), 5000));
  }
  return Math.min(2000 * 2 ** attempt, 8000);
}
const retryableStatus = (status: number) => status === 429 || status >= 500;
const retryableError = (error: unknown) =>
  /timeout|timed out|network|fetch failed|ECONNRESET|ETIMEDOUT|ECONNREFUSED|EAI_AGAIN|Tool execution error|HTTP\s*429|rate.?limit|too many requests/i.test(messageOf(error));

export async function mcpCall<T = any>(
  toolName: string,
  arguments_: Record<string, unknown>,
  options: McpOptions = {},
): Promise<T> {
  const timeoutMs = options.timeoutMs ?? 15000;
  const retries = options.retries ?? 3;
  const startedAt = Date.now();

  for (let attempt = 0; attempt <= retries; attempt++) {
    let response: Response | null = null;
    try {
      response = await fetch(MCP_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/event-stream",
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: `${Date.now()}-${attempt}`,
          method: "tools/call",
          params: { name: toolName, arguments: arguments_ },
        }),
        cache: "no-store",
        signal: AbortSignal.timeout(timeoutMs),
      });

      if (!response.ok) {
        const error = new Error(`MCP ${toolName}: HTTP ${response.status}`);
        if (!retryableStatus(response.status) || attempt >= retries) throw error;
        console.warn("[MCP retry]", { tool: toolName, status: response.status, attempt: attempt + 1 });
        await sleep(retryDelay(response, attempt));
        continue;
      }

      const value = parseBody(await response.text(), toolName);
      console.info("[MCP]", { tool: toolName, durationMs: Date.now() - startedAt, attempts: attempt + 1, ok: true });
      return value as T;
    } catch (error) {
      const retryable = retryableError(error) || (response !== null && retryableStatus(response.status));
      if (!retryable || attempt >= retries) {
        console.error("[MCP failure]", { tool: toolName, durationMs: Date.now() - startedAt, attempts: attempt + 1, error: messageOf(error) });
        throw error;
      }
      console.warn("[MCP retry]", { tool: toolName, attempt: attempt + 1, error: messageOf(error) });
      await sleep(retryDelay(response, attempt));
    }
  }
  throw new Error(`MCP ${toolName}: retries exhausted`);
}
