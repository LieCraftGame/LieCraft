import os
from typing import Callable

_PROPRIETARY_MODELS = [
    #"o1": "o1-2024-12-17", "o3-mini","o4-mini","gpt-4.1","gpt-4.5","gpt-4o",
    #"claude-3.7","claude-3.5",
    "gemini-2.5-pro","gemini-2.5-flash",
    # "grok-2","grok-3",
    #"mistral-large",
]

_OPENAI_MODELS      = {"o1": "o1-2024-12-17",
                       "o3-mini": "o3-mini-2025-01-31",
                       "o4-mini": "o4-mini-2025-04-16",
                       "gpt-4.1": "gpt-4.1",
                       "gpt-4.5": "gpt-4.5-preview-2025-02-27",
                       "gpt-4o": "gpt-4o"
                       }
_ANTHROPIC_MODELS   = {"claude-3.7": "claude-3-7-sonnet-20250219",
                       "claude-3.5": "claude-3-5-sonnet-20241022"}
_GOOGLE_MODELS      = {"gemini-2.5-pro": "gemini-2.5-pro",
                       "gemini-2.5-flash": "gemini-2.5-flash",
                       }
_XAI_MODELS         = {"grok-2","grok-3"}
_MISTRAL_MODELS     = {"mistral-large"}
_AZURE_API_VERSION  = "2024-08-01-preview"


def load_proprietary_model(
    model_id: str,
    api_key: str,
    reasoning: bool = False,
    azure: bool = False,
    azure_endpoint: str = None,
    azure_api_version: str = None
) -> Callable[[str], str]:
    """
    Returns a `generate(prompt:str)->str` function for the given model_id.
    """
    # ── OpenAI / AzureOpenAI ──────────────────────────────────────────────
    if model_id in _OPENAI_MODELS.keys():
        model_id = _OPENAI_MODELS[model_id]
        if azure:
            from openai import AzureOpenAI
            import httpx
            client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=azure_api_version or _AZURE_API_VERSION,
                http_client=httpx.Client(verify=False),
            )
        else:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

        def generate(prompt: str, max_tokens: int = 256) -> str:
            if 'o1' in model_id or 'o3' in model_id or 'o4' in model_id:
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role":"user","content": prompt}],
                    max_completion_tokens=max_tokens,
                )
            else:
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role":"user","content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
            return resp, resp.choices[0].message.content

        return generate

    # ── Anthropic ─────────────────────────────────────────────────
    elif model_id in _ANTHROPIC_MODELS.keys():
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        model_id = _ANTHROPIC_MODELS[model_id]
        def generate(prompt: str, max_tokens: int = 100) -> str:
            resp = client.messages.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp, resp.content[0].text

        return generate

    # ── Google / Gemini ─────────────────────────────────────────────
    elif model_id in _GOOGLE_MODELS.keys():
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        model_id = _GOOGLE_MODELS[model_id]
        def generate(prompt: str, max_tokens: int = 100) -> str:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=128) # Disables thinking
                ),
            )
            return response, response.text
        return generate

    # ── xAI / Grok ──────────────────────────────────────────────────────────
    elif model_id in _XAI_MODELS:
        import xai
        client = xai.Client(api_key=api_key)

        def generate(prompt: str, max_tokens: int = 100) -> str:
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role":"user","content":prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content

        return generate

    # ── Mistral-Large ─────────────────────────
    elif model_id in _MISTRAL_MODELS:
        from huggingface_hub import InferenceApi
        # on HF, the repo is “mistralai/mistral-large”
        client = InferenceApi(repo_id="mistralai/mistral-large", token=api_key)

        def generate(prompt: str, max_tokens: int = 100) -> str:
            out = client(inputs=prompt, parameters={"max_new_tokens": max_tokens})
            # HF InferenceApi returns a string or dict depending on pipeline
            if isinstance(out, str):
                return out
            elif isinstance(out, dict) and "generated_text" in out:
                return out["generated_text"]
            else:
                # sometimes returns list of dicts
                return out[0].get("generated_text", str(out))

        return generate

    else:
        raise NotImplementedError(f"{model_id} is not supported by load_proprietary_model")


if __name__ == "__main__":
    # 1) Collect your API keys from env vars:
    keys = {
        "openai":      os.getenv("OPENAI_API_KEY", ""),
        "anthropic":   os.getenv("ANTHROPIC_API_KEY", ""),
        "google":      os.getenv("GOOGLE_API_KEY", ""),
        "xai":         os.getenv("XAI_API_KEY", ""),
        "huggingface": os.getenv("HUGGINGFACE_API_KEY", ""),
        "azure":       os.getenv("AZURE_API_KEY", ""),
        "azure_endpoint": os.getenv("AZURE_ENDPOINT", ""),
    }

    prompt = "How do you feel?"
    for model_id in _PROPRIETARY_MODELS:
        # pick right key + azure flag
        if model_id in _OPENAI_MODELS:
            api_key = keys["openai"]
            azure   = False
            endpoint = None
        elif model_id in _ANTHROPIC_MODELS:
            api_key, azure = keys["anthropic"], False
            endpoint = None
        elif model_id in _GOOGLE_MODELS:
            api_key, azure = keys["google"], False
            endpoint = None
        elif model_id in _XAI_MODELS:
            api_key, azure = keys["xai"], False
            endpoint = None
        elif model_id in _MISTRAL_MODELS:
            api_key, azure = keys["huggingface"], False
            endpoint = None
        else:
            print(f"[SKIP] {model_id} not configured")
            continue

        try:
            generate = load_proprietary_model(
                model_id=model_id,
                api_key=api_key,
                azure=azure,
                azure_endpoint=keys["azure_endpoint"],
                azure_api_version=_AZURE_API_VERSION,
            )
        except NotImplementedError as e:
            print(e)
            continue

        try:
            full, resp = generate(prompt)
            print(f"\n=== {model_id} ===\n{resp}\n")
            #print ('Full: ', full)
            #breakpoint()

        except Exception as e:
            print(f"[ERROR] {model_id}: {e}")