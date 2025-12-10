import os
import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

# Daily usage limits (per process, not per user)
MAX_REQUESTS_PER_DAY = 50
MAX_TOKENS_PER_DAY = 20_000


@dataclass
class UsageStats:
    """Tracks simple daily usage for cost control."""
    requests_made: int = 0
    tokens_used: int = 0
    last_reset: date = date.today()

    def reset_if_new_day(self) -> None:
        """Reset counters when a new calendar day starts."""
        if self.last_reset < date.today():
            self.requests_made = 0
            self.tokens_used = 0
            self.last_reset = date.today()

    def can_make_request(self, tokens_needed: int) -> bool:
        """Check if we can make another request under the limits."""
        self.reset_if_new_day()
        return (
            self.requests_made + 1 <= MAX_REQUESTS_PER_DAY
            and self.tokens_used + tokens_needed <= MAX_TOKENS_PER_DAY
        )

    def record_request(self, tokens_used: int) -> None:
        """Record that a request has been made."""
        self.requests_made += 1
        self.tokens_used += tokens_used


class DailyLimitExceeded(RuntimeError):
    """Raised when the daily usage limit is exceeded."""
    pass


class MLClient:
    """
    Wrapper around OpenAI + CSV recipes.

    - Loads recipes from a CSV file.
    - For get_recommendation():
        * Filters CSV rows by include/exclude.
        * Sends only a small set of candidate rows to OpenAI.
        * Asks OpenAI to choose ONE and parse it into JSON.
    - For replace_ingredient(): uses OpenAI to edit an existing JSON recipe.
    """

    def __init__(
        self,
        api_key: str,
        csv_path: Path = Path("./dataset/1_Recipe_csv.csv"),
        model: str = "gpt-4o-mini",
        max_output_tokens: int = 1000,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty. Is OPENAI_API_KEY set?")
        self.client = OpenAI(api_key=api_key)
        self.csv_path = Path(csv_path)
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.usage_stats = UsageStats()
        # CSV setup (your format: recipe_title,category,subcategory,description,ingredients,directions,num_ingredients,num_steps)
        self.recipes: List[Dict[str, Any]] = self._load_recipes()

    # ---------- Public methods ----------

    def get_recommendation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pick the 'best' recipe from the CSV using OpenAI to parse and format it.

        payload keys:
          - include: list[str]
          - exclude: list[str]
          - dont_have: list[str] 
          - tools_have: list[str]
          - cuisine: str (optional / not strongly used here)
          - taste: str (optional)
          - diet: str (optional)
        """
        include = [s.lower() for s in payload.get("include", [])]
        exclude = [s.lower() for s in payload.get("exclude", [])]
        dont_have = [s.lower() for s in payload.get("dont_have", [])]

        exclusion = exclude + dont_have
        # 1) Find candidate recipes based on simple text matching
        candidates = self._find_candidate_recipes(
            include=include,
            exclude=exclusion,
            max_candidates=5,
        )
        if not candidates:
            raise RuntimeError("No recipes found that match the given filters.")

        # 2) Build prompt that *only* references these candidates
        prompt = self._build_prompt(payload, candidates)

        # 3) Call OpenAI to choose & parse ONE recipe
        content, total_tokens = self._call_model(prompt)
        self.usage_stats.record_request(total_tokens)
        return self._parse_response(content)

    def replace_ingredient(
        self,
        recipe: Dict[str, Any],
        from_name: str,
        to_name: str,
    ) -> Dict[str, Any]:
        """
        Replace a specific ingredient in the recipe and return an updated recipe.
        This still uses OpenAI, but grounded in the given JSON recipe.
        """
        prompt = (
            "You are a recipe editor. You will receive a recipe in JSON and must "
            "return updated JSON ONLY, no extra text or markdown.\n\n"
            f"Original recipe JSON:\n{json.dumps(recipe)}\n\n"
            f"Task: Replace the ingredient named '{from_name}' with '{to_name}'. "
            "Keep the same overall structure and fields."
        )
        content, total_tokens = self._call_model(prompt)
        self.usage_stats.record_request(total_tokens)
        return self._parse_response(content)

    # ---------- Internal helpers: CSV + filtering ----------

    def _load_recipes(self) -> List[Dict[str, Any]]:
        """
        Load recipes from CSV.

        CSV columns:
          recipe_title,category,subcategory,description,ingredients,directions,num_ingredients,num_steps
        """
        recipes: List[Dict[str, Any]] = []
        with self.csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                recipes.append(self._normalize_row(row, idx))
        return recipes

    def _normalize_row(self, row: Dict[str, str], idx: int) -> Dict[str, Any]:
        """
        Normalize a CSV row into a dict we can use later.
        We keep ingredients/directions as raw text; OpenAI will parse them.
        """
        def to_int(val: Optional[str]) -> int:
            try:
                return int(val) if val is not None else 0
            except ValueError:
                return 0

        return {
            "recipe_id": str(idx),  # you can change to row.get("id") if you have one
            "recipe_title": row.get("recipe_title") or "Untitled recipe",
            "category": row.get("category") or "",
            "subcategory": row.get("subcategory") or "",
            "description": row.get("description") or "",
            "ingredients_text": row.get("ingredients") or "",
            "directions_text": row.get("directions") or "",
            "num_ingredients": to_int(row.get("num_ingredients")),
            "num_steps": to_int(row.get("num_steps")),
        }

    def _find_candidate_recipes(
        self,
        include: List[str],
        exclude: List[str],
        max_candidates: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Very simple scoring over CSV rows based on plain-text ingredients.
        """
        scored: List[Tuple[int, Dict[str, Any]]] = []

        for r in self.recipes:
            ing_text = r["ingredients_text"].lower()

            # Hard filter: excluded ingredient present -> skip
            if any(ex in ing_text for ex in exclude):
                continue

            # Score by count of include matches
            score = 0
            for inc in include:
                if inc in ing_text:
                    score += 3

            # If no includes specified, give a small base score so we still return something
            if not include:
                score = 1

            if score > 0:
                scored.append((score, r))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [r for _, r in scored[:max_candidates]]

    # ---------- Internal helpers: prompt + OpenAI ----------

    def _build_prompt(self, payload: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
        includes = ", ".join(payload.get("include", [])) or "none specified"
        excludes = ", ".join(payload.get("exclude", [])) or "none specified"
        dont_have = ", ".join(payload.get("dont_have", [])) or "none specified"
        tools_have = ", ".join(payload.get("tools_have", [])) or "none specified"
        cuisine = payload.get("cuisine", "any")
        taste = payload.get("taste", "balanced")
        diet = payload.get("diet", "none")

        header = (
            "You are a recipe selector and parser.\n"
            "You will be given a small set of candidate recipes from a CSV dataset.\n"
            "Each recipe has fields: recipe_id, recipe_title, category, subcategory,\n"
            "description, ingredients_text, directions_text, num_ingredients, num_steps.\n\n"
            "Your job:\n"
            "1. Choose the single best recipe that fits the user constraints.\n"
            "2. Convert that ONE recipe into a JSON object.\n"
            "3. Use ONLY information that is present in the chosen recipe; do not invent new recipes.\n\n"
            "Return ONLY valid JSON (no prose, no markdown, no code fences) with fields:\n"
            "- recipe_id (string)\n"
            "- name (string)\n"
            "- ingredients (array of strings) parsed from ingredients_text\n"
            "- tools (array of strings) you infer from directions_text (e.g., pan, pot, oven)\n"
            "- steps (array of strings) parsed from directions_text into ordered steps\n"
            "- substitutions (array of strings) with simple substitution ideas\n\n"
            f"User constraints:\n"
            f"- Must include ingredients: {includes}\n"
            f"- Must exclude ingredients: {excludes}\n"
            f"- Preferred cuisine: {cuisine}\n"
            f"- Taste profile: {taste}\n"
            f"- Dietary restrictions: {diet}\n\n"
            "Candidate recipes:\n"
        )

        parts = [header]
        for r in candidates:
            parts.append(
                "###\n"
                f"recipe_id: {r['recipe_id']}\n"
                f"recipe_title: {r['recipe_title']}\n"
                f"category: {r['category']}\n"
                f"subcategory: {r['subcategory']}\n"
                f"description: {r['description']}\n"
                f"ingredients_text: {r['ingredients_text']}\n"
                f"directions_text: {r['directions_text']}\n"
                f"num_ingredients: {r['num_ingredients']}\n"
                f"num_steps: {r['num_steps']}\n\n"
            )

        parts.append(
            "Now choose the single best candidate and return ONLY the JSON object "
            "for that chosen recipe.\n"
        )

        return "".join(parts)

    def _estimate_tokens(self, text: str) -> int:
        """
        Very rough token estimate: tokens ≈ words * 1.3
        (Good enough for budget checks.)
        """
        words = text.split()
        return max(1, int(len(words) * 1.3))

    def _call_model(self, prompt: str) -> Tuple[str, int]:
        """
        Core OpenAI call with daily limit check.
        Returns (content, total_tokens_used).
        """
        prompt_tokens = self._estimate_tokens(prompt)
        tokens_needed = prompt_tokens + self.max_output_tokens

        if not self.usage_stats.can_make_request(tokens_needed):
            raise DailyLimitExceeded("Daily usage limits exceeded.")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=self.max_output_tokens,
        )

        usage = getattr(response, "usage", None)
        total_tokens = getattr(usage, "total_tokens", tokens_needed)

        content = response.choices[0].message.content
        return content, total_tokens

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse the model response as JSON.
        Tries direct parse; if that fails, extracts the first {...} block.
        """
        text = (content or "").strip()

        if not text:
            raise RuntimeError(
                f"Model returned empty content; cannot parse JSON. Raw content: {repr(content)}"
            )

        # First, try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass  # fall through to substring approach

        # Try to extract the first {...} block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse ML response as JSON even after extracting braces. "
                    f"First 200 chars: {text[:200]!r}. Error: {e}"
                ) from e

        # No braces at all
        raise RuntimeError(
            f"Failed to find JSON object in model response. First 200 chars: {text[:200]!r}"
        )


# ---------- Lazy singleton + helper functions ----------

_default_client: Optional[MLClient] = None


def _get_default_client() -> MLClient:
    """
    Lazily create a single MLClient using OPENAI_API_KEY + RECIPES_CSV_PATH.
    This avoids blowing up at import time.
    """
    global _default_client
    if _default_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. "
                "Set it in your environment before calling the ML API."
            )
        csv_path = Path("./app/dataset/1_Recipe_csv.csv")
        _default_client = MLClient(api_key=api_key, csv_path=csv_path)
    return _default_client


def get_recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function used by your Flask api.py:
    from .ml_client import get_recommendation
    """
    client = _get_default_client()
    return client.get_recommendation(payload)


def replace_ingredient(
    recipe: Dict[str, Any],
    from_name: str,
    to_name: str,
) -> Dict[str, Any]:
    """
    Convenience function used by your Flask api.py.
    """
    client = _get_default_client()
    return client.replace_ingredient(recipe, from_name, to_name)
