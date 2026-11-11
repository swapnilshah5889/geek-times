export interface ModelCompletionInput {
  stage: 'convert' | 'fact-check' | 'illustrate';
  system: string;
  user: string;
  maxTokens: number;
}

const REQUEST_TIMEOUT_MS = 240_000;
const MAX_RETRIES = 1;

function requiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`${name} is not set.`);
  return value;
}

function stageSuffix(stage: ModelCompletionInput['stage']): string {
  return stage.replace(/-/g, '_').toUpperCase();
}

function provider(stage: ModelCompletionInput['stage']): 'anthropic' | 'openai-compatible' {
  const value = process.env[`CONVERT_MODEL_PROVIDER_${stageSuffix(stage)}`]?.trim()
    || process.env.CONVERT_MODEL_PROVIDER?.trim()
    || 'anthropic';
  if (value !== 'anthropic' && value !== 'openai-compatible') {
    throw new Error(`CONVERT_MODEL_PROVIDER[_${stageSuffix(stage)}] must be anthropic or openai-compatible.`);
  }
  return value;
}

function modelName(stage: ModelCompletionInput['stage'], fallbackEnv: string): string {
  const override = process.env[`CONVERT_MODEL_${stageSuffix(stage)}`]?.trim();
  return override || requiredEnv(fallbackEnv);
}

function retryableStatus(status: number): boolean {
  return status === 408 || status === 429 || status >= 500;
}

function errorDetail(body: unknown): string {
  if (!body || typeof body !== 'object') return '';
  const record = body as Record<string, unknown>;
  const error = record.error;
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && typeof (error as Record<string, unknown>).message === 'string') {
    return (error as Record<string, unknown>).message as string;
  }
  return '';
}

async function openAiCompatible(input: ModelCompletionInput): Promise<string> {
  const apiKey = requiredEnv('OPENAI_COMPATIBLE_API_KEY');
  const model = modelName(input.stage, 'OPENAI_COMPATIBLE_MODEL');
  const baseUrl = requiredEnv('OPENAI_COMPATIBLE_BASE_URL').replace(/\/+$/, '');
  let endpoint: URL;
  try {
    endpoint = new URL(`${baseUrl}/chat/completions`);
  } catch {
    throw new Error('OPENAI_COMPATIBLE_BASE_URL must be an absolute HTTP(S) URL.');
  }
  if (!['http:', 'https:'].includes(endpoint.protocol)) {
    throw new Error('OPENAI_COMPATIBLE_BASE_URL must use HTTP or HTTPS.');
  }

  for (let attempt = 0; ; attempt++) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
        body: JSON.stringify({
          model,
          max_tokens: input.maxTokens,
          messages: [
            { role: 'system', content: input.system },
            { role: 'user', content: input.user },
          ],
        }),
        signal: controller.signal,
      });
      const body: unknown = await response.json().catch(() => undefined);
      if (!response.ok) {
        if (attempt < MAX_RETRIES && retryableStatus(response.status)) continue;
        const detail = errorDetail(body);
        throw new Error(`${input.stage} model request failed with HTTP ${response.status}${detail ? `: ${detail}` : '.'}`);
      }
      const choices = body && typeof body === 'object' ? (body as Record<string, unknown>).choices : undefined;
      const message = Array.isArray(choices) ? choices[0]?.message : undefined;
      const content = message && typeof message === 'object' ? (message as Record<string, unknown>).content : undefined;
      if (typeof content !== 'string' || !content.trim()) {
        throw new Error(`${input.stage} returned no text output.`);
      }
      return content.trim();
    } catch (error) {
      if (attempt < MAX_RETRIES && (error instanceof TypeError || (error instanceof Error && error.name === 'AbortError'))) continue;
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`${input.stage} model request timed out after ${REQUEST_TIMEOUT_MS} ms.`);
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }
}

async function anthropic(input: ModelCompletionInput): Promise<string> {
  const apiKey = requiredEnv('ANTHROPIC_API_KEY');
  const model = modelName(input.stage, 'ANTHROPIC_MODEL');
  const { default: Anthropic } = await import('@anthropic-ai/sdk');
  const client = new Anthropic({ apiKey, maxRetries: MAX_RETRIES, timeout: REQUEST_TIMEOUT_MS });
  const response = await client.messages.create({
    model,
    max_tokens: input.maxTokens,
    system: input.system,
    messages: [{ role: 'user', content: input.user }],
  });
  const text = response.content
    .filter(block => block.type === 'text')
    .map(block => 'text' in block ? block.text : '')
    .join('\n')
    .trim();
  if (!text) throw new Error(`${input.stage} returned no text output.`);
  return text;
}

export async function completeModel(input: ModelCompletionInput): Promise<string> {
  return provider(input.stage) === 'anthropic' ? anthropic(input) : openAiCompatible(input);
}
