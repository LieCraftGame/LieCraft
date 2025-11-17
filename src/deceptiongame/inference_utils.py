import os, re
import json
import time
from typing import Literal
from typing import Callable
from google.genai import types
from openai import RateLimitError


from functools import lru_cache

@lru_cache(maxsize=None)
def get_bad_words(N: int = 12, T: int = 20, K: int = 1) -> list[str]:
    """
    Generate all combinations of runs of newlines or tabs padded on the left and/or right by up to K spaces.
    Runs go from length 1 to N for newlines and 1 to T for tabs.
    """
    return [
        " " * p_left + ch * run_len + " " * p_right
        for ch, max_len in [("\n", N), ("\t", T)]
        for run_len in range(1, max_len + 1)
        for p_left in range(K + 1)
        for p_right in range(K + 1)
    ] + ["\"" +"\n" * i for i in range(N)]

def call_chat_completion_vllm(client, model_id, msg, temperature, action_json=None, max_retries = 10, extra=None) -> str:
    extra_body = {}
    if action_json:
        extra_body["guided_json"] = action_json.model_json_schema() if action_json else None
        extra_body["max_tokens"]= 512
    else:
        extra_body = None
        
        
    if False:
        from collections import defaultdict
        role_count_dict = defaultdict(int)
        extra_body["max_tokens"]= 256
        extra_body['n'] = 120
        completion = client.chat.completions.create(
            model=model_id,
            messages=msg,
            temperature=temperature,
            extra_body=extra_body,
        )
        for item in completion.choices:
            try:
                role_count_dict[json.loads(item.message.content)['choice']] +=1
            except Exception as e:
                pass

        print(f"role counts: {dict(role_count_dict)}")
        exit()
        
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=msg,
                temperature=temperature,
                extra_body=extra_body,
            )
            if action_json:
                output = json.loads(completion.choices[0].message.content)
            else:
                output = completion.choices[0].message.content
            
            return output
            
        except Exception as e:
            last_exc = e
            print(f"[Error] attempt {attempt}/{max_retries} Error: {str(e)}")

    # All retries failed
    raise last_exc


def call_chat_completion_azure(client, model_id, msg, temperature, action_json=None, max_retries=10, extra=None) -> str:
    response_format = None
    client_fn = client.chat.completions.create
    if action_json:
        response_format = action_json if action_json else None
        client_fn = client.chat.completions.parse
    reasoning = False
    if model_id == 'o4-mini' or model_id == 'o3-mini':
        reasoning = True
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            if reasoning:
                completion = client_fn(model=model_id, messages=msg, response_format=response_format)
            else:
                completion = client_fn(
                    model=model_id,
                    messages=msg,
                    temperature=temperature,
                    response_format=response_format
                )
            break
        except Exception as e:
            last_exc = e
            text = str(e)
            # extract “retry after XX seconds” from Azure’s message
            wait = 5
            if 'content' in text:
                wait = 2
                print ('is_json: ', action_json)
                attempt -= 1 
                reason = 'Content Filter'
            elif 'retry' in text:
                m = re.search(r'retry after (\d+) seconds', text)
                wait = int(m.group(1)) if m else 2 ** attempt
                wait = min(wait, 60)
                reason = 'Rate Limit'

            
            print(f"[{reason}] Attempt {attempt}/{max_retries}, sleeping {wait}s... {text}")
            time.sleep(wait)
    else:
        # all retries failed
        raise last_exc

    if response_format:
        output = json.loads(completion.choices[0].message.content)
    else:
        output = completion.choices[0].message.content
    return output


def call_chat_completion_anthropic(client, model_id, msg, temperature, action_json=None, max_retries=5, extra=None) -> str:
    extra_body = {}
    if action_json:
        extra_body["guided_json"] = action_json if action_json else None
    else:
        extra_body = None
    # breakpoint()
    if msg[0]['role'] == 'system':
        system_msg = msg.pop(0)['content']        
    else:
        system_msg = ''
    if extra and extra['claude']:
        msg[0]['content'] = msg[0]['content'] + extra['claude']
        
    body = json.dumps({
        "max_tokens": 1600,
        "messages": msg,
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": temperature,
        'system': system_msg
    })
    inference_profile_arn = 'arn:aws:bedrock:us-west-2:457878818681:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0' # <-- (Claude 3.7)
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.invoke_model(
                body=body, 
                modelId=inference_profile_arn,
            )
            output = json.loads(completion.get("body").read())['content'][0]['text']
            if action_json:
                output = output[output.index('{') : output.index('}')+1]
                output = json.loads(output)
                if 'choice' in output:
                    if isinstance(output['choice'], list):
                        output['choice'] = output['choice'][0]
                action_json.parse_obj(output)
            return output
        except Exception as e:
            last_exc = e
            print(f"[Error] attempt {attempt}/{max_retries} Error: {str(e)}")
            # breakpoint()
    raise last_exc


def call_chat_completion_gemini(client, model_id, msg, temperature, action_json=None, max_retries=5, extra=None) -> str:
    if action_json:
        response_schema = action_json if action_json else None
    else:
        response_schema = None
    if msg[0]['role'] == 'system':
        system_msg = msg.pop(0)['content']        
    else:
        system_msg = ''
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.models.generate_content(
                model=model_id,
                contents=msg[0]['content'],
                config={ # configtypes.GenerateContentConfig(
                    # 'thinking_config': types.ThinkingConfig(thinking_budget=128),
                    "response_mime_type": "application/json",
                    'response_schema': response_schema,
                    'system_instruction': system_msg
                },#),
            )
            if action_json:
                output = completion.parsed.__dict__
            else:
                output = completion.text
            return output
        except Exception as e:
            last_exc = e
            print(f"[Error] attempt {attempt}/{max_retries} Error: {str(e)}")
            breakpoint()    
    return last_exc


def call_chat_completion_xai(client, model_id, msg, temperature, action_json=None, extra=None) -> str:
    extra_body = {}
    if action_json:
        extra_body["guided_json"] = action_json if action_json else None
    else:
        extra_body = None
    raise NotImplementedError
    completion = client.chat.completions.create(
        model=model_id,
        messages=msg,
        temperature=temperature,
    )
    if action_json:
        output = list(json.loads(completion.choices[0].message.content).values())[0]
    else:
        output = completion.choices[0].message.content
    return output


