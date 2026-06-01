import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


# USD per 1M tokens as of May 28, 2026
test_models = {
    'ai21/jamba-large-1.7':              {'model_code': 'k7m2xq9p4nb3', 'cost_in_per_million':  2.00, 'cost_out_per_million':  8.00, 'class': 'flagship',    'cost': 'premium', 'country': 'Israel'},
    'anthropic/claude-opus-4.8':         {'model_code': 'r8f5wn2cv6tj', 'cost_in_per_million':  5.00, 'cost_out_per_million': 25.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'anthropic/claude-sonnet-4.6':       {'model_code': 'h3qd9zlb4ymp', 'cost_in_per_million':  3.00, 'cost_out_per_million': 15.00, 'class': 'flagship',    'cost': 'premium', 'country': 'United States'},
    'anthropic/claude-haiku-4.5':        {'model_code': 'x2vp7k8nm4rj', 'cost_in_per_million':  1.00, 'cost_out_per_million':  5.00, 'class': 'midrange',    'cost': 'high',    'country': 'United States'},
    'bytedance-seed/seed-2.0-lite':      {'model_code': 'q5bk8xem5pb6', 'cost_in_per_million':  0.25, 'cost_out_per_million':  2.00, 'class': 'lightweight', 'cost': 'med',     'country': 'China'},
    'cohere/command-a':                  {'model_code': 'b9tw6cf3sql4', 'cost_in_per_million':  2.50, 'cost_out_per_million': 10.00, 'class': 'flagship',    'cost': 'premium', 'country': 'Canada'},
    'deepseek/deepseek-v4-pro':          {'model_code': 'm4n8jp5xq7vh', 'cost_in_per_million':  0.43, 'cost_out_per_million':  0.87, 'class': 'frontier',    'cost': 'med',     'country': 'China'},
    'deepseek/deepseek-v4-flash':        {'model_code': 'c6dy2gr9wkb3', 'cost_in_per_million':  0.14, 'cost_out_per_million':  0.28, 'class': 'midrange',    'cost': 'low',     'country': 'China'},
    'google/gemini-3.1-pro-preview':     {'model_code': 't5pz4nm8vqj7', 'cost_in_per_million':  2.00, 'cost_out_per_million': 12.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'google/gemini-3.5-flash':           {'model_code': 'f9hk3bx7lwn2', 'cost_in_per_million':  1.50, 'cost_out_per_million':  9.00, 'class': 'midrange',    'cost': 'premium', 'country': 'United States'},
    'google/gemini-3.1-flash-lite':      {'model_code': 'p2qm6vw4rzc8', 'cost_in_per_million':  0.25, 'cost_out_per_million':  1.50, 'class': 'lightweight', 'cost': 'med',     'country': 'United States'},
    'google/gemma-4-26b-a4b-it':         {'model_code': 's3lr8jk7nbm5', 'cost_in_per_million':  0.06, 'cost_out_per_million':  0.33, 'class': 'lightweight', 'cost': 'low',     'country': 'United States'},
    'google/gemma-4-31b-it':             {'model_code': 'd4vh9pq2xtw6', 'cost_in_per_million':  0.12, 'cost_out_per_million':  0.37, 'class': 'lightweight', 'cost': 'low',     'country': 'United States'},
    'meta-llama/llama-4-maverick':       {'model_code': 'n7gx4mc8btf3', 'cost_in_per_million':  0.15, 'cost_out_per_million':  0.60, 'class': 'midrange',    'cost': 'low',     'country': 'United States'},
    'minimax/minimax-m2.7':              {'model_code': 'l3hb7nm4tcd8', 'cost_in_per_million':  0.30, 'cost_out_per_million':  1.20, 'class': 'midrange',    'cost': 'med',     'country': 'China'},
    'mistralai/mistral-large':           {'model_code': 'y6fv9wp2knx5', 'cost_in_per_million':  2.00, 'cost_out_per_million':  6.00, 'class': 'flagship',    'cost': 'premium', 'country': 'France'},
    'mistralai/mistral-medium-3.1':      {'model_code': 'r4cm8gd3qjt7', 'cost_in_per_million':  0.40, 'cost_out_per_million':  2.00, 'class': 'midrange',    'cost': 'med',     'country': 'France'},
    'mistralai/mistral-small-2603':      {'model_code': 'k9nw5bp6vzx2', 'cost_in_per_million':  0.15, 'cost_out_per_million':  0.60, 'class': 'lightweight', 'cost': 'low',     'country': 'France'},
    'mistralai/devstral-2512':           {'model_code': 'q5w5k99bpbzx', 'cost_in_per_million':  0.40, 'cost_out_per_million':  2.00, 'class': 'midrange',    'cost': 'med',     'country': 'France'},
    'moonshotai/kimi-k2.6':              {'model_code': 'h7dt4jq8mlc5', 'cost_in_per_million':  0.73, 'cost_out_per_million':  3.49, 'class': 'frontier',    'cost': 'high',    'country': 'China'},
    'microsoft/phi-4-mini-instruct':     {'model_code': 'g8mc5qf7twj4', 'cost_in_per_million':  0.08, 'cost_out_per_million':  0.35, 'class': 'lightweight', 'cost': 'low',     'country': 'United States'},
    'nvidia/nemotron-3-super-120b-a12b': {'model_code': 'x6kp3hr9bln2', 'cost_in_per_million':  0.09, 'cost_out_per_million':  0.45, 'class': 'midrange',    'cost': 'low',     'country': 'United States'},
    'nvidia/nemotron-3-nano-30b-a3b':    {'model_code': 'm5dw8jc4vyq7', 'cost_in_per_million':  0.05, 'cost_out_per_million':  0.20, 'class': 'lightweight', 'cost': 'low',     'country': 'United States'},
    'openai/gpt-5.5':                    {'model_code': 't9bn4kx2lrf6', 'cost_in_per_million':  5.00, 'cost_out_per_million': 30.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'openai/gpt-5.4-mini':               {'model_code': 'p3hg7mw5cdz8', 'cost_in_per_million':  0.75, 'cost_out_per_million':  4.50, 'class': 'midrange',    'cost': 'high',    'country': 'United States'},
    'openai/gpt-5.4-nano':               {'model_code': 'r6jq2vk9btx4', 'cost_in_per_million':  0.20, 'cost_out_per_million':  1.25, 'class': 'lightweight', 'cost': 'med',     'country': 'United States'},
    'openai/gpt-oss-120b':               {'model_code': 'gcwq4ebg96qi', 'cost_in_per_million': 0.039, 'cost_out_per_million':  0.18, 'class': 'midrange',    'cost': 'low',     'country': 'United States'},
    'openai/gpt-oss-20b':                {'model_code': 'b3kp9vwx2mft', 'cost_in_per_million': 0.029, 'cost_out_per_million':  0.14, 'class': 'lightweight',    'cost': 'low',     'country': 'United States'},
    'qwen/qwen3-32b':                    {'model_code': 'd2vt6jb9krx5', 'cost_in_per_million':  0.08, 'cost_out_per_million':  0.24, 'class': 'lightweight', 'cost': 'low',     'country': 'China'},
    'qwen/qwen3.7-max':                  {'model_code': 'l8nf5cm3wph7', 'cost_in_per_million':  1.25, 'cost_out_per_million':  3.75, 'class': 'frontier',    'cost': 'high',    'country': 'China'},
    'qwen/qwen3-coder-30b-a3b-instruct': {'model_code': 'ttf320fjb9kr', 'cost_in_per_million':  0.07, 'cost_out_per_million':  0.27, 'class': 'lightweight', 'cost': 'low',     'country': 'China'},
    'qwen/qwen3-coder':                  {'model_code': 'vw312t6jbr6k', 'cost_in_per_million':  0.22, 'cost_out_per_million':  1.80, 'class': 'midrange',    'cost': 'med',     'country': 'China'},
    'stepfun/step-3.7-flash':            {'model_code': 'rps2b8a4fpay', 'cost_in_per_million':  0.20, 'cost_out_per_million':  1.15, 'class': 'midrange',    'cost': 'med',     'country': 'China'},
    'tencent/hy3-preview':               {'model_code': 'gt4ov003vwua', 'cost_in_per_million': 0.063, 'cost_out_per_million':  0.21, 'class': 'frontier',    'cost': 'low',     'country': 'China'},
    'x-ai/grok-4.3':                     {'model_code': 'w5jp2zk6vqr9', 'cost_in_per_million':  1.25, 'cost_out_per_million':  2.50, 'class': 'frontier',    'cost': 'high',    'country': 'United States'},
    'xiaomi/mimo-v2.5-pro':              {'model_code': 's7hp3qw8nmc4', 'cost_in_per_million':  1.00, 'cost_out_per_million':  3.00, 'class': 'flagship',    'cost': 'high',    'country': 'China'},
    'z-ai/glm-5.1':                      {'model_code': 'c5kw9bt2vrj6', 'cost_in_per_million':  0.98, 'cost_out_per_million':  3.08, 'class': 'frontier',    'cost': 'high',    'country': 'China'},
    }



grader_models = {
    'anthropic/claude-opus-4.8':         {'model_code': 'r8f5wn2cv6tj', 'cost_in_per_million':  5.00, 'cost_out_per_million': 25.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'google/gemini-3.1-pro-preview':     {'model_code': 't5pz4nm8vqj7', 'cost_in_per_million':  2.00, 'cost_out_per_million': 12.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'openai/gpt-5.5':                    {'model_code': 't9bn4kx2lrf6', 'cost_in_per_million':  5.00, 'cost_out_per_million': 30.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
}


zzztest_models = {
    'anthropic/claude-opus-4.8':         {'model_code': 'r8f5wn2cv6tj', 'cost_in_per_million':  5.00, 'cost_out_per_million': 25.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'anthropic/claude-sonnet-4.6':       {'model_code': 'h3qd9zlb4ymp', 'cost_in_per_million':  3.00, 'cost_out_per_million': 15.00, 'class': 'flagship',    'cost': 'premium', 'country': 'United States'},
    'anthropic/claude-haiku-4.5':        {'model_code': 'x2vp7k8nm4rj', 'cost_in_per_million':  1.00, 'cost_out_per_million':  5.00, 'class': 'midrange',    'cost': 'high',    'country': 'United States'},
    'google/gemini-3.1-pro-preview':     {'model_code': 't5pz4nm8vqj7', 'cost_in_per_million':  2.00, 'cost_out_per_million': 12.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'openai/gpt-5.5':                    {'model_code': 't9bn4kx2lrf6', 'cost_in_per_million':  5.00, 'cost_out_per_million': 30.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'x-ai/grok-4.3':                     {'model_code': 'w5jp2zk6vqr9', 'cost_in_per_million':  1.25, 'cost_out_per_million':  2.50, 'class': 'frontier',    'cost': 'high',    'country': 'United States'},
    'openai/gpt-5.4-nano':               {'model_code': 'r6jq2vk9btx4', 'cost_in_per_million':  0.20, 'cost_out_per_million':  1.25, 'class': 'lightweight', 'cost': 'med',     'country': 'United States'},
    'deepseek/deepseek-v4-flash':        {'model_code': 'c6dy2gr9wkb3', 'cost_in_per_million':  0.14, 'cost_out_per_million':  0.28, 'class': 'midrange',    'cost': 'low',     'country': 'China'},
    'qwen/qwen3-32b':                    {'model_code': 'd2vt6jb9krx5', 'cost_in_per_million':  0.08, 'cost_out_per_million':  0.24, 'class': 'lightweight', 'cost': 'low',     'country': 'China'},
    'stepfun/step-3.7-flash':            {'model_code': 'rps2b8a4fpay', 'cost_in_per_million':  0.20, 'cost_out_per_million':  1.15, 'class': 'midrange',    'cost': 'med',     'country': 'China'},
}

zzzgrader_models = {
    'anthropic/claude-opus-4.8':         {'model_code': 'r8f5wn2cv6tj', 'cost_in_per_million':  5.00, 'cost_out_per_million': 25.00, 'class': 'frontier',    'cost': 'premium', 'country': 'United States'},
    'x-ai/grok-4.3':                     {'model_code': 'w5jp2zk6vqr9', 'cost_in_per_million':  1.25, 'cost_out_per_million':  2.50, 'class': 'frontier',    'cost': 'high',    'country': 'United States'},
    'google/gemini-3.5-flash':           {'model_code': 'f9hk3bx7lwn2', 'cost_in_per_million':  1.50, 'cost_out_per_million':  9.00, 'class': 'midrange',    'cost': 'premium', 'country': 'United States'},
    'anthropic/claude-haiku-4.5':        {'model_code': 'x2vp7k8nm4rj', 'cost_in_per_million':  1.00, 'cost_out_per_million':  5.00, 'class': 'midrange',    'cost': 'high',    'country': 'United States'},
}


def call_llm(prompt, model, openrouter_api_key, temperature):

    url = "https://openrouter.ai/api/v1/chat/completions"

    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": 10000, #may be too small for some reasoning models depending on the use case; program will flag and retry if exceeded
    }

    data = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": "https://local.coldbrew.indicators",
        "X-Title": "coldbrew-indicators-refiner",
    }

    req = Request(url, data=data, headers=headers, method="POST")
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        t_start = time.perf_counter()
        try:
            with urlopen(req, timeout=500) as resp: #increase timeout if a larger task
                raw = resp.read().decode("utf-8")
                raw = "\n".join(line for line in raw.splitlines() if not line.startswith(":")) #strip OpenRouter SSE keep-alive comments
                payload = json.loads(raw)
        except Exception as e: #catch-all (HTTPError, TimeoutError, JSONDecodeError, connection resets, etc.)
            if attempt == max_attempts:
                print(f"{type(e).__name__} for model={model} after {max_attempts} attempts: {e}")
                raise
            print(f"{type(e).__name__} for model={model} (attempt {attempt}/{max_attempts}): {e}, retrying...")
            time.sleep(5 * attempt)
            continue

        message = payload["choices"][0]["message"]
        content = (message.get("content") or "").strip()
        if content:
            break

        #--- empty content; if reasoning is present the model burned its token budget on thinking — print a short summary instead of dumping the whole reasoning trace
        reasoning = message.get("reasoning") or ""
        if reasoning:
            detail = f"reasoning model ran out of tokens (reasoning: {len(reasoning)} chars)"
        else:
            detail = f"raw message: {message}"
        if attempt == max_attempts:
            print(f"Empty content for model={model} after {max_attempts} attempts, {detail}")
            raise RuntimeError(f"Empty content from {model}")
        print(f"Empty content for model={model} (attempt {attempt}/{max_attempts}), {detail}, retrying...")
        time.sleep(5 * attempt)

    timer_secs = time.perf_counter() - t_start
    tokens_in = payload["usage"]["prompt_tokens"]
    tokens_out = payload["usage"]["completion_tokens"]

    return content, timer_secs, tokens_in, tokens_out



def make_test_run_info(topic, model, timer_secs, tokens_in, tokens_out):

    cost_tokens_in = tokens_in * test_models[model]['cost_in_per_million'] / 1_000_000
    cost_tokens_out = tokens_out * test_models[model]['cost_out_per_million'] / 1_000_000
    cost_tokens_tot = cost_tokens_in + cost_tokens_out
    model_code = test_models[model]['model_code']

    return (
        '```json\n'
        '{'
        f' "model_code": "{model_code}",'
        f' "topic": "{topic}",'
        f' "timer_secs": {timer_secs:.2f},'
        f' "tokens_in": {tokens_in},'
        f' "tokens_out": {tokens_out},'
        f' "cost_tokens_in": {cost_tokens_in:.8f},'
        f' "cost_tokens_out": {cost_tokens_out:.8f},'
        f' "cost_tokens_tot": {cost_tokens_tot:.8f}'
        ' }\n'
        '```'
    )

