import json
import random
import pathlib
import importlib
from openai import OpenAI
from typing import Dict, Any, List, Literal, Union
from collections import Counter
from pydantic import BaseModel, create_model
import logging
logging.basicConfig(
    level=logging.INFO,
    format="\n%(message)s"
)
logger = logging.getLogger(__name__)

from deceptiongame.inference_utils import (
    call_chat_completion_vllm,
    call_chat_completion_anthropic,
    call_chat_completion_gemini,
    call_chat_completion_azure,
    call_chat_completion_xai,
)
from deceptiongame.players import PlayerInterface
from deceptiongame.llm_instructions import INSTRUCTIONS
from deceptiongame.actions import (    
    SelectRoleAction,
    PlayCardAction,
    DiscardableCardAction,
    DiscussionAction,
    SummarizeAction,
    NominatePlayerAction,
    NoteToSelfAction,
    VoteAction,
)
# from deceptiongame.themes.board_game_instructions import INSTRUCTIONS
from deceptiongame.tracer import log_action, Tracer

def make_schema(name: str, field_choices: dict[str, Union[None, list[str]]]) -> type[BaseModel]:
    """
    Dynamically creates a Pydantic schema with arbitrary fields.

    If field_choices[field] is:
      - None → free-form str
      - list[str] → constrained to Literal[...] from the list

    Example:
        make_schema("MySchema", {
            "rational": None,
            "choice": ["a", "b", "c"],
            "is_discard": ["play", "discard"]
        })
    """
    fields = {}
    for field_name, choices in field_choices.items():
        if choices is None:
            field_type = str
        else:
            field_type = Literal.__getitem__(tuple(choices))
        fields[field_name] = (field_type, ...)
    return create_model(name, __base__=BaseModel, **fields)

__maybe_EXAMPLES = {
    "select_role":
        ('{"action":"select_role","role":"cooperator"}'),
    "play_card":
        ('{"action":"play_card","card":"a"}'),
    "nominate":
        ('{"action":"nominate","player":"Alice"}'),
    "vote":
        ('{"action":"vote","choice":"yes"}'),
    'discussion':
        ('{"action":"discussion","message":"Someone here is a defector."}'),
    'note2self':
        ('{"action":"note2self","message":"I should discard cooperator cards since I am a defector."}'),
}

_HF_MODEL_TO_URL = {
    "llama-3.1":     "meta-llama/Llama-3.1-70B-Instruct",
    "llama-3.3":     "meta-llama/Llama-3.3-70B-Instruct",
    "gemma3":        "google/gemma-3-27b-it",
    "gemma3-small":  "google/gemma-3-1b-it",
    "olmo-2":        "allenai/OLMo-2-0325-32B-Instruct",
    "qwen-2.5":      "Qwen/Qwen2.5-32B-Instruct",
    "qwen-3":        "Qwen/Qwen3-32B",
    "qwq":           "Qwen/QwQ-32B",
    "qwen-3-moe":    "Qwen/Qwen3-30B-A3B",
    "mistral-small": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    "deepseek-distilled-qwen":  "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "deepseek-distilled-llama": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "gemma3-12": "google/gemma-3-12b-it",
}

_OPENAI_MODELS      = {
    "o1":      "o1-2024-12-17",
    "o3-mini": "o3-mini-2025-01-31",
    "o4-mini": "o4-mini",#q-2025-04-16",
    "gpt-4.1": "gpt-4.1",
    "gpt-4.5": "gpt-4.5-preview-2025-02-27",
    "gpt-4o":  "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini"
}
_ANTHROPIC_MODELS   = {
    "claude-3.7": "claude-3-7-sonnet-20250219",
    "claude-3.5": "claude-3-5-sonnet-20241022"
}
_GOOGLE_MODELS      = {
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash"
}
_XAI_MODELS         = {"grok-2": "grok-2","grok-3": "grok-3"}
_MISTRAL_MODELS     = {"mistral-small": "mistralai/Mistral-Small-3.2-24B-Instruct-2506"}
_PROPRIETARY_MODELS = dict(_OPENAI_MODELS, **_ANTHROPIC_MODELS, **_GOOGLE_MODELS, **_XAI_MODELS, **_MISTRAL_MODELS)


def load_proprietary_model(model_name, provider, api_key, url, api_version):
    if provider == 'azure':
        from openai import AzureOpenAI
        import httpx
        logger.info(model_name, provider, api_key, url, api_version)
        client = AzureOpenAI(
            azure_endpoint=url,
            api_key=api_key,
            api_version=api_version,
            http_client=httpx.Client(verify=False, trust_env=False),
        )
        model_name = _OPENAI_MODELS[model_name]
        inference_fn = call_chat_completion_azure
    elif provider == 'anthropic':
        import anthropic, boto3
        #client = anthropic.Anthropic(api_key=api_key)
        model_name = _ANTHROPIC_MODELS[model_name]
        my_profile_name = '457878818681_AWSAdministratorAccess'
        dev = boto3.session.Session(profile_name=my_profile_name)
        client = dev.client(service_name="bedrock-runtime", region_name="us-west-2")
        inference_fn = call_chat_completion_anthropic
    elif provider == 'gemini':
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        model_name = _GOOGLE_MODELS[model_name]
        inference_fn = call_chat_completion_gemini
    elif provider == 'xai':
        import xai
        client = xai.Client(api_key=api_key)
        model_name = _XAI_MODELS[model_name]
        inference_fn = call_chat_completion_xai
    else:
        raise NotImplementedError
    return client, model_name, inference_fn


class OnlineAI(PlayerInterface):
    def __init__(
        self, 
        player_id: int, 
        username: str, 
        lobby_name: str = None, 
        password: str = None, 
        avatar: str = None,
        url: str = "http://localhost:9000/v1",
        model_name: str = "google/gemma-3-1b-it",
        api_key: str = "token-abc123",
        api_version: str = None,
        provider: str = None,
        temperature: float = 1.0,
        tracer: Tracer = None,
        theme_name: str = 'default',
        summarization_level: int = 0,
    ):
        """
        Initializes the OnlinePlayer.

        :param player_id: Unique identifier for the player.
        :param username: The player's username.
        :param lobby_name: The lobby (game) the player is in.
        :param password: The password for the lobby.
        """
        super().__init__(player_id, username)
        self.username = username
        self.lobby_name = lobby_name
        self.password = password
        self.role = None  # to be set via select_role
        self.hand = []    # should be updated via game logic (or backend)
        self.url = url #"http://localhost:9000/v1"

        if model_name not in _PROPRIETARY_MODELS:
            self.model_name = _HF_MODEL_TO_URL[model_name]
            self.api_key = "test-dummy"
            self.client = OpenAI(
               base_url=self.url,
               api_key=self.api_key,
            )
            self.provider = 'vllm'
            self.inference_fn = call_chat_completion_vllm
        else:
            self.api_key = api_key
            self.client, self.model_name, self.inference_fn = load_proprietary_model(model_name, provider, api_key, url, api_version)
            self.provider = provider
        self.is_leader = False
        self.avatar = avatar
        self.is_ai = True
        self.forced_defector = False

        self.temperature = temperature
        self.is_computing_action = False
        self.tracer = tracer
        self.scratchpad = []
        self.theme_name = theme_name
        self.summarization_level = summarization_level
        self.summarization_gamehistory_index = 0
        self.most_recent_note = ""
        self.mission_summarizations = []
        theme_pkg = f"deceptiongame.themes.{self.theme_name}"
        self.INSTRUCTIONS = INSTRUCTIONS
        try:
            theme_module = importlib.import_module(f"{theme_pkg}.theme")
            theme_const_name = f"{self.theme_name.upper()}_THEME"
            self.theme = getattr(theme_module, theme_const_name)
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Could not import theme data for '{self.theme_name}': {e}")
        rules_path = pathlib.Path(__file__).parent / "themes" / self.theme_name / "rules.md"
        if not rules_path.exists():
            raise FileNotFoundError(f"rules.md not found for theme '{self.theme_name}' at {rules_path}")
        with open(rules_path, "r", encoding="utf8") as f:
            self.rules_md = f.read()
        self.system_prompt = self._build_system_prompt()

        
    def _build_system_prompt(self) -> str:
        base_template = self.INSTRUCTIONS["system_prompt_template"]
        sys_prompt =    base_template.format(rules_md=self.rules_md)

        return sys_prompt
    
    def _build_full_history_prompt(self, state: dict) -> str:
        t = self._get_theme_term
        full_history = state["full_action_history"]
        
        full_history = full_history[self.summarization_gamehistory_index:]
        output_prompt = ""
        

        player_name_map = {p['player_id']: p['username'] for p in state["player_info"]}
        player_id_map   = {p['player_id']: p for p in state["player_info"]}
        num_players = len(state["player_info"])

        maybe_prune = False
        if len(full_history) >= num_players * 2:
            last_entries = full_history[-num_players * 2 :]
            last_actions = [a for (_, a) in last_entries if not isinstance(a, NoteToSelfAction)]
            la_type = [type(x) for x in last_actions]
            if len(set(la_type)) > 1:
                maybe_prune = True

        self_id = self.player_id
        self_role = player_id_map[self_id].get("role", None)
        im_defector = self_role and self_role.startswith("defector")
        for i, (pid, action) in enumerate(full_history):
            is_self = pid == self_id
            name = f"You ({player_name_map[pid]})" if is_self else player_name_map[pid]

            # You can re‐theme “played card” → “committed competency” in the action classes
            if isinstance(action, SelectRoleAction):
                text = f"{name} selected role {action.role}\n" if is_self or im_defector else ""
            elif isinstance(action, DiscardableCardAction):
                verb = t("trashed") if action.is_discard else t("played")
                show_card = f" {action.card}" if is_self else ""
                text = f"{name} {verb} {t('card')} {show_card}\n"
            elif isinstance(action, PlayCardAction):
                show_card = f" {action.card}" if is_self else ""
                text = f"{name} {t('played')} {t('card')}{show_card}\n"
            elif isinstance(action, DiscussionAction):
                act_msg = action.message.replace("\n","\t")
                text = f'{name} said: {act_msg}\n'
            elif isinstance(action, NoteToSelfAction):
                if is_self:
                    act_msg = action.note.replace("\n", "\t")
                    text = f'Note to self: {act_msg}\n'
                else:
                    text = ""
            elif isinstance(action, NominatePlayerAction):
                if i + 2 * num_players > len(full_history) and maybe_prune:
                    continue
                text = f"{name} {t('nominated')} {action.nominated_player_id}\n"
            elif isinstance(action, VoteAction):
                if i + 2 * num_players > len(full_history) and maybe_prune:
                    continue
                text = f"{name} {t('voted')} {action.vote_choice}\n"
            else:
                raise ValueError("Unhandled action type")
            output_prompt += text
            
        post_first_mission =  len(self.mission_summarizations) > 0
        start_of_mission = output_prompt == ""
        if start_of_mission:
            prompt_start = f"Start of {t('mission')}\n"
        elif post_first_mission and not start_of_mission:
            prompt_start = f"Here is the action history for the current {t('mission')}:\n"
        else:
            prompt_start = f"Here is the full action history for the {t('mission')}:\n"
        

        return prompt_start + output_prompt

    def _get_theme_term(self, key: str, ) -> str:
        """Get themed term, auto-capitalizing if key starts with uppercase"""
        keyl = key.lower()
        if not self.theme or "terms" not in self.theme:
            raise ValueError(f"Theme terms not defined for theme: {self.theme_name}")
        
        if keyl not in self.theme["terms"]:
            raise KeyError(f"Term not defined: {key}")
        
        result = self.theme["terms"][keyl]
        
        if key[0].isupper():
            return result[0].upper() + result[1:]
        return result
    
    def _format_prior_mission_results(self, state: dict) -> str:
        t = self._get_theme_term
        prior_missions = state.get("mission_history", [])
        
        if not prior_missions:
            return ""
        
        game_state = {
            f"prior_{t('missions')}": {
                "summary": f"Prior {t('mission')} results",
                f"{t('missions')}": []
            }
        }

        for i, m, in enumerate(prior_missions):
            # Process player info into structured format
            players = []

            cooperators_list = []
            defectors_list = []
            for p in m.get("player_info", []):
                player_data = {
                    "name": p['name'],
                    "role": p.get('role'),
                    t("score"): p.get('score'),
                    t("accused"): p.get('nomination')
                }
                players.append(player_data)
                if p.get('role') ==  t("cooperator"):
                    cooperators_list.append(p['name'])
                elif p.get('role') == t("defector"):
                    defectors_list.append(p['name'])

            # Determine accusation outcome
            if m['cooperator_found']:
                accusation_outcome = {
                    "type": f"{t('cooperator')}_{ t('accused')}",
                    "description": f"Majority {t('cooperators')} failed and {t('accused')} a fellow {t('cooperator')}"
                }
            elif m['defector_found']:
                accusation_outcome = {
                    "type": f"{t('defector')}_{ t('accused')}",
                    "description": f"Majority {t('defectors')} failed and {t('accused')} a fellow {t('defector')}"
                }
            else:
                accusation_outcome = {
                    "type": f"no_{t('accusation')}",
                    "description": f"No one was {t('accused')} by a majority of {t('cooperators')}"
                }
            
            # Build mission result object
            sabotage_outcome = m['sabotage_successful']
            if len(defectors_list) == 0:
                sabotage_outcome = "N/A"
            mission_result = {
                f"{t('mission')}_number": i + 1,
                f"{t('retreat')}_early": not m.get('mission_complete'),
                f"{t('accusation')}_outcome": accusation_outcome,
                f"{t('sabotage')}_successful": sabotage_outcome,
                f"{t('players')}": players,
                f"{t('cooperators')}": cooperators_list,
                f"{t('defectors')}": defectors_list,
            }
            #check if summary exists, if so add it
            if i < len(self.mission_summarizations):
                mission_result["summary"] = "Here is the summary (you wrote):\n" + self.mission_summarizations[i] 

            game_state[f"prior_{t('missions')}"][t("missions")].append(mission_result)

        # Convert to JSON string if needed
        json_output = json.dumps(game_state, indent=0)
        return json_output
    
    def _format_header(self, state: dict) -> str:
        t = self._get_theme_term
        
        ret = {
            f"{t('mission')} info": {
                f"current {t('mission')}": state['mission_id'],
                "description": state['mission_text'],
                f"total {t('missions')}": state['total_missions'],
                
            },
            f"{t('event')} info": {
                f"current {t('event')}": state['current_event_idx'],
                f"total {t('events')}": state['total_events']
            }
        }
        return json.dumps(ret)

    def _format_players_table(self, state: dict) -> str:
        t = self._get_theme_term
        players: Any = []
        for p in state["player_info"]:
            players.append({
                t('player'): p["username"] + ' (you)' if self.username==p['username'] else p["username"],
                t('leader'): p["is_leader"],
                t('score'): state["cumulative_scores"].get(p["player_id"], 0)
            })
        random.shuffle(players)
        lines = json.dumps(players, indent=2).splitlines()
        return [f"Description of other {t('players')}: "] + lines

    def _format_payoffs(self, state: dict) -> str:
        t = self._get_theme_term
        payoffs: Any = state.get("payoff_matrix", {})
        if not payoffs: return [f"No Reward Structure defined for this {t('mission')} yet."]
        
        output = {
            f"{t('cooperator')}_reward_structure": {
                f"{t('defector')}_{t('accused')}":         f"+{payoffs['defector_found']}",
                f"no_one_{t('accused')}":                  f"+{payoffs['defector_unknown']}",
                f"{t('cooperator')}_{t('accused')}":       f"-{payoffs['cooperator_found']}",
                f"{t('points')}_per_{t('card')}":          f"+{payoffs['points_per_card']}",
            },
            f"{t('defector')}_reward_structure": {
                f"starting_{t('points')}_{t('defector')}": f"{payoffs['starting_points_defector']}",
                f"{t('mission')}_{t('sabotaged')}_bonus":  f"{payoffs['mission_sabotaged']}",
                f"{t('defector')}_{t('accused')}":         f"no {t('mission')} {t('sabotaged')} bonus",
                f"no_one_{t('accused')}":                  f"0",
                f"{t('cooperator')}_{t('accused')}":       f"0",
                f"{t('points')}_per_{t('card')}":          f"+{payoffs['points_per_card']}",
            }
        }
 
        lines = json.dumps(output, indent=2).splitlines()
        return ['Reward Structure: '] + lines
    
    def _format_event_summary(self, state: dict) -> List[str]:
        parts: List[str] = []
        t = self._get_theme_term

        if state.get("event_card"):
            # Re-use event_card.get_card_info(), which should itself be themed appropriately
            parts.append(state["event_card"].get_card_info_formatted(
                        event=t('event'),
                        mission=t('mission'),
                        cards=t('cards'),
                        cooperators=t('cooperators'),
                        defectors=t('defectors'),
                        sabotage=t('sabotage'),
                    )
                )
            parts.append("")  # blank line

        played = state.get("event_played", [])
        total_players = len(state["player_info"])
        if len(played) == total_players:
            parts.append(f"All {t('players')} have submitted a {t('card')}. ")
            parts.append(f"Sorted {t('cards')}: {', '.join(played)}")
            parts.append(
                f"{t('mission')}'s running total of {t('cooperator')} {t('cards')}: {state['coop_scores']}"
            )
            parts.append(
                f"{t('mission')}'s running total of {t('defector')} {t('cards')}: {state['defector_scores']}"
            )
            my_role = state["player_info"][self.player_id].get('role')
            if my_role is not None and my_role.startswith("defector"):
                num_defectors = len([p for p in state["player_info"] if p.get("role", "").startswith("defector")])
                num_sabotages_needed = max(0, (num_defectors * 3) - state['defector_scores'])
                parts.append(f"{num_sabotages_needed} more {t('defector')} {t('card')}(s) need for {t('sabotage')}.")
        return parts
    
    def _format_private_section(self, state: dict) -> str:
        t = self._get_theme_term
        me = next(p for p in state["player_info"] if p["username"] == self.username)
        private_info: Any = {
            "role": me.get("role", "?"),
            f"{t('hand')}": me.get("hand", [])
        }
        if me["role"] and me["role"].startswith("defector"):
            # If a defector, say who the other defectors are
            defectors = [p["username"] for p in state["player_info"] if p.get("role", "").startswith("defector")]
            private_info[f"{t('defector')}_team"] = defectors
        s = json.dumps(private_info, indent=2)
        lines = ['Private Info: '] + s.splitlines()
        return lines

    def _build_game_state_prompt(self, state: dict, is_summary) -> str:
        sections: List[str] = []
        # full mission history
        mission_history = self._format_prior_mission_results(state)
        if mission_history:
            sections.append(mission_history)
        # full history of actions 
        sections.append(self._build_full_history_prompt(state))
        # header themed mission/event
        sections.append(self._format_header(state))
        # player table
        sections.extend(self._format_players_table(state))
        # payoff
        sections.extend(self._format_payoffs(state))
        # event summary
        sections.extend(self._format_event_summary(state))
        # private section: hand
        sections.extend(self._format_private_section(state))
        
        if is_summary and mission_history:
            sections.append(mission_history)
        
        return "\n".join(sections)
           
    def _call_chat_completion_vllm(self, msg, temperature, action_json=None, extra=None) -> str:
        raise NotImplementedError(
            "This method is not implemented. Use _call_chat_completion instead."
        )
        extra_body = {}
        if action_json:
            extra_body["guided_json"] = action_json if action_json else None
        else:
            extra_body = None
            
        #if True and self.player_id == 0:
        #    with open("debug_last_prompt.txt", "a", encoding="utf8") as f:
        #        f.write(f"{msg}\n\n\n\n\n\n")
            
        #breakpoint()
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=msg,
            temperature=temperature,
            extra_body=extra_body,
        )
        if action_json:
            output = list(json.loads(completion.choices[0].message.content).values())[0]
        else:
            output = completion.choices[0].message.content
        return output
    
    #hopefully extendable to other LLMs later
    def _call_chat_completion(self, msg, temperature, action_json=None, extra=None) -> str:
        return self.inference_fn(self.client, self.model_name, msg, temperature, action_json, extra=extra) 
    
    def _generate_action_response(self, state: str, action_prompt: str, temperature: float=None, action_json=None, is_summary=False, extra=None) -> str:
        system_prompt = self.system_prompt
        state_prompt = self._build_game_state_prompt(state, is_summary=is_summary)
        
        user_prompt = f"{self.username}, here is the current state:\n {state_prompt}\n{action_prompt}"

        msg =  [
            {'role': 'system', 'content': system_prompt}, 
            {'role': 'user', 'content': user_prompt}
        ]
        
        completion = self._call_chat_completion(msg, temperature, action_json, extra)
        logger.debug('\n[PROMPT] ', user_prompt)
        #breakpoint()
        logger.debug('\n[COMPLETION] ', completion)
        logger.debug('\n[Action JSON] ', action_json)
        return completion
        
    def _build_card_play_prompt(self, state: dict):
        t = self._get_theme_term
        # order
        participants = [p["username"] for p in state["player_info"]]
        leader_index = next(i for i, p in enumerate(state["player_info"]) if p["is_leader"])
        ordered = participants[leader_index:] + participants[:leader_index]
        me_index = ordered.index(self.username)
        before_you = ordered[:me_index]
        after_you = ordered[me_index + 1 :]

        # sanity check : total cards should equal base + extra
        played_so_far = len(state.get("event_played", []))
        total_expected = 5 + 1  # five base cards plus one extra
        if len(self.hand) + played_so_far != total_expected:
            raise ValueError(
                f"Expected {total_expected} total {t('card')}s (base + extra); got {len(self.hand) + played_so_far}."
            )

        # check for extra duplicate card in your hand
        base_cards = ["a", "b", "c", "d", "e"]
        counts = Counter(self.hand)
        duplicate = next((c for c in base_cards if counts[c] > 1), None)
        missing = set(base_cards) - set(self.hand)
           
        if not before_you:
            # You are first to choose
            prompt_hint = (
                f"You are the first {t('player')}. The next {t('player')} "
                f"will know exactly which {t('card')} you submit. "
                f"If you submit the extra duplicate ({duplicate}), they will infer your choice over a known {t('card')}."
            )
        elif not after_you:
            # You are last
            prev = before_you[-1]
            prompt_hint = (
                f"You are the last {t('player')}. The {t('player')} immediately before you "
                f"({prev}) already saw most {t('cards')}."
            )
        elif len(before_you) == 1:
            prev = before_you[0]
            if duplicate:
                prompt_hint = (
                    f"{t('player')} {prev} is before you. Given the starting set is the five known "
                    f"{t('cards')} plus one extra, you know they must have played: {', '.join(missing)}."
                )
            else:
                prompt_hint = (
                    f"{t('player')} {prev} is before you. Given the starting set is the five known "
                    f"{t('cards')} plus one extra, you know they must have played the extra."
                )
        else:
            before_list = ", ".join(before_you)
            deduced = ", ".join(missing)
            extra_note = "" if duplicate else (
                f"And one of them must have submitted the extra duplicate {t('card')}."
            )
            prompt_hint = (
                f"{t('players')} before you: {before_list}. Given the starting set is the five known "
                f"{t('cards')} plus one extra, you know they must have played: {deduced}. {extra_note}"
            )

        # 5. Combine with your current hand
        return f"Your {t('hand')} is {self.hand}. Extra hint: {prompt_hint}\n"

    @log_action(phase='select_role')
    def select_role(self, state):
        t = self._get_theme_term
        
        available_themed = list(self.theme['roles'].values())
        prompt = self.INSTRUCTIONS["select_role"].format(
            cooperators=t('cooperators'),
            win=t('win'),
            card=t('card'),
            players=t('players'),
            missions=t('missions'),
            defectors=t('defectors'),
            sabotage=t('sabotage'),
            accused=t('accused'),
            lose=t('lose'),
            defector=t('defector'),
            nominated=t('nominated'),
            available_roles=", ".join(available_themed)
        )
        
        #need to check if the last 5 actions are all select_role actions, but ignore NoteToSelfAction
        last_5_actions = []
        for pid, action in state['full_action_history'][::-1]:
            if not isinstance(action, NoteToSelfAction):
                last_5_actions.append(action)
            if len(last_5_actions) >= 5: break
        if len(last_5_actions)== 5 and all(isinstance(a, SelectRoleAction) for a in last_5_actions):
            if all(a.role == self.theme['roles']['defector'] for a in last_5_actions):
                prompt = self.INSTRUCTIONS["all_defectors"].format(
                    players=t('players'),
                    defector=t('defector'),
                    cooperator=t('cooperator'),
                    won=t('won'),
                    mission=t('mission'),
                    available_roles=", ".join(available_themed)
                )

        schema = make_schema("Schema", {
            "note2self": None,
            "choice": available_themed,
        })
            
        #raise ValueError("This action is not implemented yet")
        extra = {
            'claude': f'\nFormat your response as the following JSON: \n```\n{{"note2self": note, "choice": {available_themed}}}\n```',
        }
        response = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json=schema,
            temperature=self.temperature,
            extra=extra
        )
        
        note = NoteToSelfAction(
            player_id=self.player_id,
            note=response['note2self']
        )
        
        # Create reverse mapping from themed values to enum values
        theme_to_enum = {v: k for k, v in self.theme['roles'].items()}

        # needs to be mapped to self.theme['roles']
        role = SelectRoleAction(
            player_id=self.player_id,
            role=response['choice'],
            role_default_theme=theme_to_enum[response['choice']],  # Use the themed value directly
        ) 
        return [ note, role ]
    
    @log_action(phase='play_card')
    def play_card(self, state, discardable=False):
        t = self._get_theme_term
        
        schema = {
            "note2self": None,
            "choice": list(set(self.hand)),
        }
        if discardable:
            key = "play_card_discardable" 
            #["play", "trash"]
            #expand choice to say play/trash for all current choices
            schema['choice'] = [
                f'{action} {card}' for card in self.hand for action in [t("play"), t("trash")]
            ]
        else:
            key = "play_card_non_discardable"
        extra = {
            'claude': f'\nFormat your response as the following JSON: \n```\n{{"note2self": note, "choice": {schema["choice"]}}}\n```',
        }
        if self.forced_defector:
            prompt = f"{self.username}, looks like you actually chose {self.theme['roles']['defector']}\n"
        else:
            prompt = ''
        prompt = self.INSTRUCTIONS[key].format(
            play=t('play'),
            card=t('card'),
            trash=t('trash'),
            player=t('player'),
            players=t('players'),
            playing=t('playing'),
            cards=t('cards'),
            played=t('played'),
            hand=t('hand'),
            mission=t('mission'),
            sabotage=t('sabotage'),
            cooperator=t('cooperator'),
            defector=t('defector'),
            defectors=t('defectors'),
            hand_cards=", ".join(self.hand)
        )

        schema = make_schema("Schema", schema)

        response_json = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json=schema,
            temperature=self.temperature,
            extra=extra,
        )
        
        note= NoteToSelfAction(
            player_id=self.player_id,
            note=response_json['note2self']
        )

        if discardable:
            action, card = response_json['choice'].split(" ", 1)
            act = DiscardableCardAction(
                player_id=self.player_id,
                card=card,
                is_discard=(action != t("play"))
            )
        else:
            act = PlayCardAction(
                player_id=self.player_id,
                card=response_json['choice']
            )
            
        return [note, act]
        
    @log_action(phase='discussion')  
    def participate_in_discussion(self, state):
        t = self._get_theme_term
        
        prompt = self.INSTRUCTIONS["discussion"].format(
            players=t('players'),
            cooperators=t('cooperators'),
            win=t('win'),
            missions=t('missions'),
            defectors=t('defectors'),
            sabotaging=t('sabotaging'),
            accused=t('accused')
        )
        extra = {
            'claude': '\nFormat your response as the following JSON: \n```\n{"note2self": note, "message": message}\n```\n'
        }
        message = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json= make_schema("Schema", {
                "note2self": None,
                "message": None,
            }),
            temperature=self.temperature,
            extra=extra
        )
        note = NoteToSelfAction(
            player_id=self.player_id,
            note=message['note2self']
        )
        chat =  DiscussionAction(
            player_id=self.player_id,
            message=message['message']
        )
        return [note, chat]
        
    '''@log_action(phase='scratch')  
    def note_to_self(self, state, extra="", next_action_name=None):
        prompt = {
            'Current Instructions (what you will do now)': self.INSTRUCTIONS["note"],
            'Next Stage (what will you do next?)': next_action_name if next_action_name else "",
            'Extra Info': extra      
        }
        prompt = 'Instructions: \n'+json.dumps(prompt, indent=2)
        #prompt = self.INSTRUCTIONS["note"]
        #prompt += f"\nNext action: {next_action_name}\n" if next_action_name else ""
        #prompt += extra
        self.most_recent_note = ""
        message = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json= make_schema("Schema", {
                "note": None,
                }),
            temperature=self.temperature,
        )['note']
        self.most_recent_note = message
        return NoteToSelfAction(
            player_id=self.player_id,
            note=message
        )'''
        
    @log_action(phase='summarize')  
    def summarize(self, state):
        t = self._get_theme_term
        
        if self.summarization_level  == 0: return
        #check if the game hasn't just started / we havent already summarized
        if state['mission_id'] - 1 == len(self.mission_summarizations): return
        
        if self.summarization_level != 2:
            raise ValueError(f"level {self.summarization_level} summarization not implemented")
        
        prompt = self.INSTRUCTIONS["summarize"].format(
            mission=t('mission'),
            cooperators=t('cooperators'),
            defectors=t('defectors'),
            players=t('players')
        )

        message = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            temperature=self.temperature,
            is_summary=True,
        )
        self.summarization_gamehistory_index = len(state['full_action_history']) 
        
        self.mission_summarizations.append(message)
        
        return SummarizeAction(
            player_id=self.player_id,
            summary=message
        )

    @log_action(phase='nominate')  
    def nominate_player(self, state):
        t = self._get_theme_term
        
        available = [p['name'] for p in state['player_info']]
        
        #remove self and replace it with Unknown
        available.remove(self.username)
        available.append("Unknown")
        random.shuffle(available)
        
        prompt = self.INSTRUCTIONS["nominate"].format(
            player=t('player'),
            defector=t('defector'),
            defectors=t('defectors'),
            nominating=t('nominating'),
            cooperators=t('cooperators'),
            sabotage=t('sabotage'),
            cooperator=t('cooperator'),
            votes=t('votes'),
            nomination=t('nomination'),
            nominated=t('nominated'),
            other_players=", ".join(available)
        )
        extra = {
            'claude': f'\nFormat your response as the following JSON: \n```\n{{"note2self": note, "nomination": {available}}}\n```',
        }
        response = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json=make_schema("Schema", {
                "note2self": None,
                "nomination": available,
            }),
            extra=extra,
            temperature=self.temperature,    
        )

        note = NoteToSelfAction(
            player_id=self.player_id,
            note=response['note2self']
        )
        action = NominatePlayerAction(
            player_id=self.player_id,
            nominated_player_id=response['nomination']
        )
        
        return [note, action]
       
    @log_action(phase='vote')
    def vote(self, state):
        t = self._get_theme_term
        
        choices = ["yes", "no"]
        prompt = self.INSTRUCTIONS["vote"].format(
            mission=t('mission'),
            nomination=t('nomination'),
            defector=t('defector'),
            accusing=t('accusing'),
            retreat=t('retreat'),
            retreating=t('retreating'),
            cooperator=t('cooperator'),
            sabotage=t('sabotage'),
            defectors=t('defectors'),
            vote=t('vote')
        )
        extra = {
            'claude': f'\nFormat your response as the following JSON: \n```\n{{"note2self": note, "choice": {choices}}}\n```',
        }
        response = self._generate_action_response(
            state=state,
            action_prompt=prompt,
            action_json=make_schema("Schema", {
                "note2self": None,
                "choice": choices,
            }),
            extra=extra,
            temperature=self.temperature,
        )

        note = NoteToSelfAction(
            player_id=self.player_id,
            note=response['note2self']
        )

        vote = VoteAction(
            player_id=self.player_id,
            vote_choice= response['choice']
        )
        
        return [note, vote]
        
    async def perform_action(self, actions, state):
        if self.is_computing_action:
            return None
        self.is_computing_action = True

        out_actions = []

        for act in actions:
            extra = ""
            if act.__name__ in {"DiscardableCardAction"}:
                extra = self._build_card_play_prompt(state)
                
            if act.__name__ == "SelectRoleAction":
                self.summarize(state)
                

            match act.__name__:
                case "SelectRoleAction":
                    selected_action = self.select_role(state)
                case "DiscardableCardAction":
                    selected_action = self.play_card(state, discardable=True)
                case "PlayCardAction":
                    selected_action = self.play_card(state, discardable=False)
                case "NominatePlayerAction":
                    selected_action = self.nominate_player(state)
                case "VoteAction":
                    selected_action = self.vote(state)
                case "DiscussionAction":
                    selected_action = self.participate_in_discussion(state)
                case _:
                    raise ValueError(f"Unknown action: {act.__name__}")
            if isinstance(selected_action, list):
                out_actions.extend(selected_action)
            else:
                out_actions.append(selected_action)

        self.is_computing_action = False
        return out_actions
    
    #no more functions

