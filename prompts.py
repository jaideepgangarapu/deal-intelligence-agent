"""Prompts for the analysis modes: risk, stakeholder, timeline, next."""

COMMON_RULES = """You analyze a sales deal using ONLY the customer memories provided.
Rules:
- Use only information in the memories. Never invent facts, people, risks, dates or numbers.
- Every item must include "evidence": a list of 1-3 short quotes copied EXACTLY, word for word, from the memories.
- If a detail is not stated, write "Not stated". Do not guess.
- Memories tagged "[Interaction #N | recorded ...]" are ordered by N. Later interactions override earlier ones.
- Never invent dates. Use only the interaction numbers or dates that appear in the memories.
- Only call something resolved/addressed if a later memory explicitly says so.
- If there is nothing to report, return an empty list.
- Respond with a single JSON object and nothing else."""

RISK_QUERIES = [
    "pricing objection discount cost budget",
    "integration technical concern existing system",
    "security legal compliance review approval",
    "procurement contract vendor process",
    "deadline deployment timeline go-live",
    "objection concern blocker unresolved",
    "approval sign-off decision maker",
]

STAKEHOLDER_QUERIES = [
    "stakeholders roles departments",
    "CTO CFO CEO procurement legal concerns requirements",
    "who approves sign-off approval responsibility",
    "requests objections requirements",
]

TIMELINE_QUERIES = [
    "first interaction initial requirements",
    "changed updated now instead",
    "new concern objection requirement",
    "resolved approved agreed accepted",
    "deadline pricing discount change",
    "new stakeholder joined",
]

RECALL_QUERIES = {
    "risk": RISK_QUERIES,
    "stakeholder": STAKEHOLDER_QUERIES,
    "timeline": TIMELINE_QUERIES,
    "next": RISK_QUERIES + STAKEHOLDER_QUERIES + TIMELINE_QUERIES,
}

RISK_TASK = """Identify deal risks and unresolved blockers.
Categories: Pricing, Technical/Integration, Security/Legal, Procurement, Deadline, Missing Approval, Customer Objection, Other.

Level rubric:
- High: blocks approval, is a hard deadline, or is a required approval/review not yet completed.
- Medium: a stated objection or concern with no resolution recorded.
- Low: a minor concern, or one a later memory says has been addressed.
If a later memory explicitly resolves a concern, set status "Addressed" and level "Low", and quote the resolving text.
Do not report a risk unless a memory supports it.

Return JSON:
{"risks": [{"category": "...", "title": "short title", "level": "High|Medium|Low",
  "reason": "one sentence why this level", "status": "Open|Addressed",
  "evidence": ["exact quote from memories"]}],
 "summary": "one or two sentences"}"""

STAKEHOLDER_TASK = """Build a stakeholder map of every person or department in the memories.
For each: name (if stated), role/department, concerns, requirements, objections, requests,
approval responsibility (only if a memory says they must approve/review something), and
blocking_deal ("Yes" only if a memory shows they are holding up the deal, otherwise "No" or "Not stated").
Use "Not stated" for anything missing. Lists may be empty.
If the salesperson asked a question, answer it in "answer" using only the stakeholders you listed. If no question, use "".

Return JSON:
{"answer": "...", "stakeholders": [{"name": "...", "role": "...", "concerns": [], "requirements": [],
  "objections": [], "requests": [], "approval_responsibility": "...", "blocking_deal": "Yes|No|Not stated",
  "evidence": ["exact quote from memories"]}]}"""

TIMELINE_TASK = """Build a chronological timeline of how the deal changed, oldest first.
Track: new objections, new requirements, pricing changes, new stakeholders, new technical concerns,
new security/legal requirements, deadline changes, resolved concerns, newly unresolved concerns, priority changes.
"when" must be the interaction number/date shown in the memory (e.g. "Interaction #2 (2026-09-28)").
If the memory has no number or date, write "Order not recorded". Never invent dates.
If the salesperson asked a question, answer it in "answer" from the events you listed. If none, use "".

Return JSON:
{"answer": "...", "summary": "how the deal has changed overall, or 'Only one interaction recorded'",
 "events": [{"when": "...", "event": "what happened or changed",
  "change_type": "New objection|New requirement|Pricing change|New stakeholder|Technical concern|Security/Legal|Deadline change|Resolved|Unresolved|Priority change",
  "evidence": ["exact quote from memories"]}]}"""

NEXT_TASK = """You are a sales advisor. Using the memories and the analysis below, recommend the next best actions
for the salesperson, most important first (max 4), then draft a short follow-up message.
Rules for the draft: mention only facts and terms that appear in the memories. Do NOT promise discounts,
dates or terms that the memories do not show as agreed. Address the person/department most tied to the top action.

Return JSON:
{"actions": [{"priority": 1, "action": "what to do", "stakeholder": "who, or Not stated",
  "reason": "why, based on the memories", "evidence": ["exact quote from memories"]}],
 "draft_message": {"to": "...", "subject": "...", "body": "..."}}"""

TASKS = {
    "risk": RISK_TASK,
    "stakeholder": STAKEHOLDER_TASK,
    "timeline": TIMELINE_TASK,
    "next": NEXT_TASK,
}


def build_prompt(mode, deal_name, memories, question=None, context=None):
    memory_text = "\n".join(f"- {m}" for m in memories)
    parts = [f"Deal / customer: {deal_name}", f"Customer memories:\n{memory_text}"]

    if context:
        parts.append(f"Analysis so far (for reference only):\n{context}")

    if question:
        parts.append(f"Salesperson's question: {question}")

    parts.append(f"Task:\n{TASKS[mode]}")

    return "\n\n".join(parts)