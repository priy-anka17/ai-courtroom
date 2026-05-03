"""LangGraph node functions — each node is a courtroom agent."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agents.tools import web_search
from config import GROQ_BASE_URL, LLM_MODEL, get_groq_api_key

# ── LLM helper ───────────────────────────────────────────────────────────────

def _llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=get_groq_api_key(),
        base_url=GROQ_BASE_URL,
        model=LLM_MODEL,
        temperature=0.3,
    )


def _invoke(system: str, user: str) -> str:
    return _llm().invoke([SystemMessage(content=system), HumanMessage(content=user)]).content


# ── 1. Research Agent ────────────────────────────────────────────────────────

RESEARCH_PROMPT = """\
You are a Court Research Clerk. Your job is to gather factual evidence on a claim.

Search results are provided below. Organize the evidence into:
1. **Facts Supporting the Claim** — bullet points with source references
2. **Facts Against the Claim** — bullet points with source references
3. **Key Statistics & Data** — any numbers, percentages, studies found
4. **Context & Background** — relevant background information

Be objective. Present ALL evidence found, for and against.
Format your response in clean markdown.
"""


def research_node(state: dict[str, Any]) -> dict[str, Any]:
    """Gather evidence from the web on both sides of the claim."""
    claim = state["claim"]

    # Search for evidence on both sides
    search_for = web_search(f"{claim} evidence data statistics", max_results=5)
    search_against = web_search(f"{claim} criticism counterargument debunked", max_results=5)
    search_context = web_search(f"{claim} background context overview", max_results=3)

    all_evidence = (
        f"=== Evidence Search (FOR) ===\n{search_for}\n\n"
        f"=== Evidence Search (AGAINST) ===\n{search_against}\n\n"
        f"=== Background Context ===\n{search_context}"
    )

    research_brief = _invoke(
        RESEARCH_PROMPT,
        f"Claim: \"{claim}\"\n\nSearch Results:\n{all_evidence}",
    )

    return {
        "research": research_brief,
        "raw_evidence": all_evidence,
        "stage": "research_complete",
    }


# ── 2. Prosecution Agent (argues FOR the claim) ─────────────────────────────

PROSECUTION_PROMPT = """\
You are the PROSECUTION attorney in an AI Courtroom. You must argue IN FAVOR of the claim.

You have access to research evidence. Build the STRONGEST possible case FOR the claim.

Structure your argument as:
## Opening Statement
A powerful 2-3 sentence opening.

## Argument 1: [Title]
Your first key argument with evidence.

## Argument 2: [Title]
Your second key argument with evidence.

## Argument 3: [Title]
Your third key argument with evidence.

## Key Evidence
Cite the most compelling data points and statistics.

## Closing Statement
A persuasive closing that summarizes why the claim is TRUE.

Be persuasive, logical, and cite evidence. Use **bold** for emphasis.
Assign a CONFIDENCE SCORE (0-100) at the very end: "Prosecution Confidence: XX/100"
"""


def prosecution_node(state: dict[str, Any]) -> dict[str, Any]:
    """Build the case FOR the claim."""
    claim = state["claim"]
    research = state["research"]

    argument = _invoke(
        PROSECUTION_PROMPT,
        f"Claim: \"{claim}\"\n\nResearch Evidence:\n{research}",
    )

    return {"prosecution_argument": argument, "stage": "prosecution_complete"}


# ── 3. Defense Agent (argues AGAINST the claim) ─────────────────────────────

DEFENSE_PROMPT = """\
You are the DEFENSE attorney in an AI Courtroom. You must argue AGAINST the claim.

You have access to research evidence AND the prosecution's argument. Dismantle their case.

Structure your argument as:
## Opening Statement
A powerful 2-3 sentence opening challenging the claim.

## Rebuttal 1: [Title]
Counter the prosecution's first argument with evidence.

## Rebuttal 2: [Title]
Counter the prosecution's second argument with evidence.

## Rebuttal 3: [Title]
Your own independent argument AGAINST the claim.

## Key Counter-Evidence
Cite the most compelling data points that DISPROVE the claim.

## Closing Statement
A persuasive closing that summarizes why the claim is FALSE or misleading.

Be sharp, logical, and find weaknesses in the prosecution's case. Use **bold** for emphasis.
Assign a CONFIDENCE SCORE (0-100) at the very end: "Defense Confidence: XX/100"
"""


def defense_node(state: dict[str, Any]) -> dict[str, Any]:
    """Build the case AGAINST the claim."""
    claim = state["claim"]
    research = state["research"]
    prosecution = state["prosecution_argument"]

    argument = _invoke(
        DEFENSE_PROMPT,
        (
            f"Claim: \"{claim}\"\n\n"
            f"Research Evidence:\n{research}\n\n"
            f"Prosecution's Argument:\n{prosecution}"
        ),
    )

    return {"defense_argument": argument, "stage": "defense_complete"}


# ── 4. Cross-Examination Agent ──────────────────────────────────────────────

CROSS_EXAM_PROMPT = """\
You are a Cross-Examination specialist. Analyze BOTH sides' arguments and identify:

## Prosecution Weaknesses
- What logical fallacies or weak evidence did the prosecution use?
- What did they ignore or misrepresent?

## Defense Weaknesses
- What logical fallacies or weak evidence did the defense use?
- What did they ignore or misrepresent?

## Unresolved Questions
- What key questions remain unanswered by both sides?

## Strongest Points (Each Side)
- Prosecution's single strongest argument
- Defense's single strongest argument

Be brutally analytical. Grade each side's argument quality (A-F).
"""


def cross_examination_node(state: dict[str, Any]) -> dict[str, Any]:
    """Cross-examine both sides' arguments."""
    claim = state["claim"]
    prosecution = state["prosecution_argument"]
    defense = state["defense_argument"]

    analysis = _invoke(
        CROSS_EXAM_PROMPT,
        (
            f"Claim: \"{claim}\"\n\n"
            f"Prosecution's Argument:\n{prosecution}\n\n"
            f"Defense's Argument:\n{defense}"
        ),
    )

    return {"cross_examination": analysis, "stage": "cross_exam_complete"}


# ── 5. Judge Agent ───────────────────────────────────────────────────────────

JUDGE_PROMPT = """\
You are the JUDGE presiding over this AI Courtroom debate. Deliver your final verdict.

You have reviewed ALL evidence, both arguments, and the cross-examination analysis.

Deliver your verdict in this EXACT format:

## ⚖️ Verdict: [SUSTAINED / OVERRULED / PARTIALLY SUSTAINED]
One sentence summary of the ruling.

## 📊 Confidence Score: [0-100]%

## 🔍 Judicial Analysis

### Evidence Quality
Rate the overall quality of evidence presented (1-10) and explain.

### Prosecution Assessment
- Strength of arguments (1-10)
- Key strengths and weaknesses

### Defense Assessment
- Strength of arguments (1-10)  
- Key strengths and weaknesses

### Reasoning
Your detailed reasoning for the verdict. What tipped the scales?

## 📋 Final Ruling
A comprehensive 3-5 sentence final ruling explaining your decision, noting any
nuances or conditions.

## 🏷️ Tags
Provide exactly 3 one-word tags that categorize this debate topic.

IMPORTANT: You MUST also output a JSON block at the very end for data extraction:
```json
{
  "verdict": "SUSTAINED" or "OVERRULED" or "PARTIALLY SUSTAINED",
  "confidence": <0-100>,
  "prosecution_score": <1-10>,
  "defense_score": <1-10>,
  "evidence_quality": <1-10>,
  "tags": ["tag1", "tag2", "tag3"]
}
```
"""


def judge_node(state: dict[str, Any]) -> dict[str, Any]:
    """Deliver the final verdict."""
    claim = state["claim"]
    research = state["research"]
    prosecution = state["prosecution_argument"]
    defense = state["defense_argument"]
    cross_exam = state["cross_examination"]

    verdict_text = _invoke(
        JUDGE_PROMPT,
        (
            f"Claim: \"{claim}\"\n\n"
            f"Research Brief:\n{research}\n\n"
            f"Prosecution:\n{prosecution}\n\n"
            f"Defense:\n{defense}\n\n"
            f"Cross-Examination:\n{cross_exam}"
        ),
    )

    # Extract JSON scores
    scores = _extract_scores(verdict_text)

    return {
        "verdict": verdict_text,
        "scores": scores,
        "stage": "verdict_delivered",
    }


def _extract_scores(verdict_text: str) -> dict:
    """Extract the JSON scores block from the judge's verdict."""
    import re

    match = re.search(r"```json\s*\n(.*?)```", verdict_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Fallback defaults
    return {
        "verdict": "PARTIALLY SUSTAINED",
        "confidence": 50,
        "prosecution_score": 5,
        "defense_score": 5,
        "evidence_quality": 5,
        "tags": ["debate", "analysis", "AI"],
    }
