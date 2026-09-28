"""Core logic for the new features: multi-deal banks + shared analysis engine."""

import os
import re
import json
import threading
import datetime
import textwrap
from difflib import SequenceMatcher

from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

import prompts

load_dotenv()

HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
hindsight = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY,
)

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
DEALS_FILE = "deals.json"


def _run_hindsight_call(method_name, *args, **kwargs):
    """Run each Hindsight request with a client owned by its worker thread."""
    result = {}
    error = {}

    def runner():
        client = Hindsight(
            base_url=HINDSIGHT_BASE_URL,
            api_key=HINDSIGHT_API_KEY,
        )
        try:
            result["value"] = getattr(client, method_name)(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - surfaced to user as a flash message
            error["value"] = exc
        finally:
            try:
                client.close()
            except Exception:
                pass

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()

    if "value" in error:
        raise error["value"]

    return result.get("value")


# ---------------------------------------------------------------
# Multi-deal memory isolation
# ---------------------------------------------------------------

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def bank_for(slug):
    return f"deal-{slug}"


def load_deals():
    if os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_deals(deals):
    with open(DEALS_FILE, "w", encoding="utf-8") as f:
        json.dump(deals, f, indent=2)


def select_deal(name):
    """Select a deal, creating it if new. Returns its slug."""
    slug = slugify(name)

    if not slug:
        raise ValueError("Deal name cannot be empty.")

    deals = load_deals()

    if slug not in deals:
        deals[slug] = {
            "name": name.strip(),
            "count": 0,
            "interactions": []
        }
        save_deals(deals)

    else:
        # Support deals.json files created by the older version.
        deals[slug].setdefault("interactions", [])
        deals[slug].setdefault("count", 0)
        save_deals(deals)

    return slug


def deal_name(slug):
    return load_deals()[slug]["name"]


# ---------------------------------------------------------------
# Store interaction
# ---------------------------------------------------------------

def retain_interaction(slug, text):
    """
    Store an interaction in Hindsight and also keep a small local
    metadata copy containing interaction number and original text.

    The local copy is NOT the main memory system.
    It only preserves ordering metadata if Hindsight rewrites memory text.
    """

    deals = load_deals()

    deals[slug].setdefault("interactions", [])

    deals[slug]["count"] += 1
    n = deals[slug]["count"]

    now = datetime.datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M")

    content = (
        f"[Interaction #{n} | recorded {stamp}]\n"
        f"Customer: {deals[slug]['name']}\n"
        f"Interaction: {text}"
    )

    try:
        _run_hindsight_call(
            "retain",
            bank_id=bank_for(slug),
            content=content,
            timestamp=now,
        )
    except TypeError:
        _run_hindsight_call(
            "retain",
            bank_id=bank_for(slug),
            content=content,
        )

    # Preserve ordering information locally.
    deals[slug]["interactions"].append(
        {
            "number": n,
            "recorded": stamp,
            "text": text
        }
    )

    save_deals(deals)

    return n


# ---------------------------------------------------------------
# Recall
# ---------------------------------------------------------------

def _results(resp):
    return getattr(resp, "results", resp)


def _order_key(text):
    m = re.search(r"Interaction #(\d+)", text)

    if m:
        return int(m.group(1))

    return 999999


def _clean_text(text):
    return " ".join(str(text).split())


def _similarity(a, b):
    """
    Compare a recalled Hindsight memory with the original
    locally stored interaction.

    Hindsight may rewrite the wording, so exact matching
    is not required here.
    """

    a = _clean_text(a).lower()
    b = _clean_text(b).lower()

    if not a or not b:
        return 0.0

    return SequenceMatcher(None, a, b).ratio()


def _attach_interaction_metadata(slug, memories):
    """
    If Hindsight returned a rewritten memory without the original
    interaction number, attach the number using the local interaction
    record.

    This preserves timeline ordering without inventing dates.
    """

    deals = load_deals()
    interactions = deals.get(slug, {}).get("interactions", [])

    if not interactions:
        return memories

    updated = []

    for memory in memories:

        # Already tagged.
        if re.search(r"Interaction #\d+", memory):
            updated.append(memory)
            continue

        best = None
        best_score = 0.0

        for interaction in interactions:

            original = interaction.get("text", "")

            score = _similarity(memory, original)

            if score > best_score:
                best_score = score
                best = interaction

        # Only attach metadata when there is a strong match.
        if best is not None and best_score >= 0.45:

            number = best["number"]
            recorded = best["recorded"]

            memory = (
                f"[Interaction #{number} | recorded {recorded}] "
                f"{memory}"
            )

        updated.append(memory)

    return updated


def recall_merged(slug, queries):

    bank = bank_for(slug)

    seen = set()
    out = []

    for q in queries:

        try:
            resp = _run_hindsight_call(
                "recall",
                bank_id=bank,
                query=q,
            )

        except Exception as e:

            print(
                f"(recall failed for '{q}': {e})"
            )

            continue

        for r in _results(resp):

            text = _clean_text(r.text)

            key = text.lower()

            if key in seen:
                continue

            seen.add(key)

            when = next(
                (
                    str(getattr(r, a))
                    for a in ("occurred_start", "mentioned_at")
                    if getattr(r, a, None)
                ),
                None,
            )

            if when and "recorded" not in text:

                text = (
                    f"{text} "
                    f"[memory date: {when}]"
                )

            out.append(text)

    # Recover interaction numbers if Hindsight rewrote the memory text.
    out = _attach_interaction_metadata(slug, out)

    # Sort using recovered interaction numbers.
    out.sort(key=_order_key)

    return out


# ---------------------------------------------------------------
# Groq analysis + evidence validation
# ---------------------------------------------------------------

KEYS = {
    "risk": "risks",
    "stakeholder": "stakeholders",
    "timeline": "events",
    "next": "actions",
}


def _llm_json(user_prompt):

    kwargs = dict(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": prompts.COMMON_RULES
            },
            {
                "role": "user",
                "content": user_prompt
            },
        ],
    )

    try:

        resp = groq.chat.completions.create(
            response_format={
                "type": "json_object"
            },
            **kwargs
        )

    except Exception:

        resp = groq.chat.completions.create(
            **kwargs
        )

    text = (
        resp.choices[0]
        .message
        .content
        or ""
    ).strip()

    text = re.sub(
        r"^```(?:json)?|```$",
        "",
        text,
        flags=re.M
    ).strip()

    return json.loads(
        text[
            text.find("{"):
            text.rfind("}") + 1
        ]
    )


def _tokens(s):
    return set(
        re.findall(
            r"\w+",
            s.lower()
        )
    )


def _supported(evidence, memories):
    """
    Evidence counts only if almost all its words
    appear in one recalled memory.
    """

    et = _tokens(evidence)

    if len(et) < 2:
        return False

    return any(
        len(et & _tokens(m)) / len(et) >= 0.85
        for m in memories
    )


def validate(items, memories):
    """
    Drop any item whose evidence is not found
    in the recalled memories.
    """

    kept = []
    dropped = 0

    for item in items or []:

        if not isinstance(item, dict):
            dropped += 1
            continue

        ev = item.get("evidence") or []

        if isinstance(ev, str):
            ev = [ev]

        good = [
            e
            for e in ev
            if (
                isinstance(e, str)
                and _supported(e, memories)
            )
        ]

        if good:

            item["evidence"] = good
            kept.append(item)

        else:

            dropped += 1

    return kept, dropped


def _run(
    mode,
    name,
    memories,
    question=None,
    context=None
):

    data = _llm_json(
        prompts.build_prompt(
            mode,
            name,
            memories,
            question,
            context
        )
    )

    key = KEYS[mode]

    data[key], data["dropped"] = validate(
        data.get(key),
        memories
    )

    return data


def analyze(
    mode,
    slug,
    question=None
):
    """
    mode:
    risk
    stakeholder
    timeline
    next
    """

    name = deal_name(slug)

    queries = [
        f"{name} {q}"
        for q in prompts.RECALL_QUERIES[mode]
    ]

    if question:

        queries.append(
            f"{name} {question}"
        )

    memories = recall_merged(
        slug,
        queries
    )

    if not memories:

        return {
            "empty": True,
            "memories": []
        }

    if mode == "next":

        context = {
            m: _run(
                m,
                name,
                memories
            )
            for m in (
                "risk",
                "stakeholder",
                "timeline"
            )
        }

        slim = {
            "risks": [
                {
                    k: r.get(k)
                    for k in (
                        "title",
                        "level",
                        "status"
                    )
                }
                for r in context["risk"]["risks"]
            ],

            "stakeholders": [
                {
                    k: s.get(k)
                    for k in (
                        "name",
                        "role",
                        "blocking_deal",
                        "approval_responsibility"
                    )
                }
                for s in context[
                    "stakeholder"
                ]["stakeholders"]
            ],

            "changes": [
                e.get("event")
                for e in context[
                    "timeline"
                ]["events"]
            ],
        }

        data = _run(
            "next",
            name,
            memories,
            context=json.dumps(
                slim,
                indent=1
            )
        )

    else:

        data = _run(
            mode,
            name,
            memories,
            question
        )

    data["memories"] = memories

    return data


# ---------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------

def _cell(v):

    if isinstance(v, list):

        v = "; ".join(
            str(x)
            for x in v
            if x
        )

    v = (
        str(v).strip()
        if v is not None
        else ""
    )

    return v or "Not stated"


def _wrap(
    text,
    indent=0,
    width=86
):

    return textwrap.fill(
        text,
        width=width,
        subsequent_indent=" " * indent
    )


def _evidence(
    item,
    pad="    "
):

    for e in item.get(
        "evidence",
        []
    ):

        print(
            _wrap(
                f'{pad}Evidence: "{e}"',
                len(pad) + 10
            )
        )


def _footer(data):

    if data.get("dropped"):

        print(
            f"\n({data['dropped']} unsupported "
            f"item(s) removed: no matching "
            f"memory evidence.)"
        )


def show_memories(data):

    print("\nHindsight recalled:")

    for m in data.get(
        "memories",
        []
    ):

        print(
            _wrap(
                f"- {m}",
                2
            )
        )


def show(mode, data):

    if data.get("empty"):

        print(
            "\nNo memories found for this deal yet. "
            "Add interactions first (option 9)."
        )

        return

    show_memories(data)

    {
        "risk": _show_risk,
        "stakeholder": _show_stakeholders,
        "timeline": _show_timeline,
        "next": _show_next
    }[mode](data)

    _footer(data)


def _show_risk(data):

    print(
        "\n=========== DEAL RISK RADAR ==========="
    )

    risks = data.get(
        "risks",
        []
    )

    if not risks:

        print(
            "No supported risks found in memory."
        )

        return

    order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    risks.sort(
        key=lambda r:
        order.get(
            str(
                r.get(
                    "level",
                    ""
                )
            ).lower(),
            3
        )
    )

    for r in risks:

        print(
            f"\n[{str(r.get('level', '?')).upper()}] "
            f"{_cell(r.get('category'))}: "
            f"{_cell(r.get('title'))}"
        )

        print(
            _wrap(
                f"    Why: {_cell(r.get('reason'))}",
                9
            )
        )

        print(
            f"    Status: "
            f"{_cell(r.get('status'))}"
        )

        _evidence(r)

    if data.get("summary"):

        print(
            _wrap(
                f"\nSummary: {data['summary']}",
                9
            )
        )


def _show_stakeholders(data):

    print(
        "\n======== STAKEHOLDER RELATIONSHIP MAP ========"
    )

    if data.get("answer"):

        print(
            _wrap(
                f"\nAnswer: {data['answer']}",
                8
            )
        )

    people = data.get(
        "stakeholders",
        []
    )

    if not people:

        print(
            "No stakeholders found in memory."
        )

        return

    fields = [
        (
            "Concerns",
            "concerns"
        ),
        (
            "Requirements",
            "requirements"
        ),
        (
            "Objections",
            "objections"
        ),
        (
            "Requests",
            "requests"
        ),
        (
            "Approval responsibility",
            "approval_responsibility"
        ),
        (
            "Blocking the deal?",
            "blocking_deal"
        ),
    ]

    for i, s in enumerate(
        people,
        1
    ):

        print(
            f"\n[{i}] "
            f"{_cell(s.get('name'))} | "
            f"{_cell(s.get('role'))}"
        )

        print(
            "    " + "-" * 70
        )

        for label, key in fields:

            print(
                _wrap(
                    f"    {label:<24}| "
                    f"{_cell(s.get(key))}",
                    29
                )
            )

        _evidence(s)


def _show_timeline(data):

    print(
        "\n====== DEAL TIMELINE & CHANGE DETECTOR ======"
    )

    if data.get("answer"):

        print(
            _wrap(
                f"\nAnswer: {data['answer']}",
                8
            )
        )

    events = data.get(
        "events",
        []
    )

    if not events:

        print(
            "No timeline events found in memory."
        )

    for e in events:

        print(
            f"\n{_cell(e.get('when'))} "
            f"[{_cell(e.get('change_type'))}]"
        )

        print(
            _wrap(
                f"    {_cell(e.get('event'))}",
                4
            )
        )

        _evidence(e)

    if data.get("summary"):

        print(
            _wrap(
                f"\nOverall: {data['summary']}",
                9
            )
        )


def _show_next(data):

    print(
        "\n========== NEXT BEST ACTION =========="
    )

    actions = data.get(
        "actions",
        []
    )

    if not actions:

        print(
            "No supported actions found in memory."
        )

    for a in actions:

        print(
            f"\n{a.get('priority', '-')}. "
            f"{_cell(a.get('action'))}"
        )

        print(
            f"    Who: "
            f"{_cell(a.get('stakeholder'))}"
        )

        print(
            _wrap(
                f"    Why: "
                f"{_cell(a.get('reason'))}",
                9
            )
        )

        _evidence(a)

    msg = data.get(
        "draft_message"
    ) or {}

    if msg.get("body"):

        print(
            "\n--- Draft follow-up message ---"
        )

        print(
            f"To: {_cell(msg.get('to'))}"
        )

        print(
            f"Subject: "
            f"{_cell(msg.get('subject'))}\n"
        )

        print(
            msg["body"]
        )


def close():

    hindsight.close()