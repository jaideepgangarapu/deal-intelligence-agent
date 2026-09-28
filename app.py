import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

import core

load_dotenv()


def _build_general_answer(slug, question):
    deal_name = core.deal_name(slug)
    queries = [
        f"{deal_name} {question}",
        question,
        f"{deal_name} customer concerns pricing security stakeholders",
    ]

    memories = core.recall_merged(slug, queries)
    if not memories:
        return {
            "answer": "No prior deal memories were found yet. Add an interaction to create context before asking a question.",
            "memories": [],
        }

    memory_text = "\n".join(memories)
    prompt = f"""
You are a sales deal intelligence assistant.
Use only the customer memories provided below.

Customer memories:
{memory_text}

Salesperson's question:
{question}

Answer clearly and stay grounded in these memories only.
"""

    response = core.groq.chat.completions.create(
        model=core.MODEL,
        messages=[
            {"role": "system", "content": "Use only the provided memories and do not invent facts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    answer = (response.choices[0].message.content or "No answer available.").strip()
    return {
        "answer": answer,
        "memories": memories,
    }


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "deal-intelligence-agent-dev-key")

    @app.route("/")
    def index():
        return render_template("index.html", deals=core.load_deals())

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        deals = core.load_deals()
        selected_slug = session.get("selected_deal")
        selected_name = deals.get(selected_slug, {}).get("name") if selected_slug in deals else None
        interactions = []
        analysis = None

        if request.method == "POST":
            action = request.form.get("action")

            if action == "create_deal":
                name = request.form.get("deal_name", "").strip()
                if not name:
                    flash("Please enter a deal/customer name.", "error")
                else:
                    selected_slug = core.select_deal(name)
                    session["selected_deal"] = selected_slug
                    selected_name = core.deal_name(selected_slug)
                    flash(f"Selected deal: {selected_name}", "success")
                    return redirect(url_for("dashboard"))

            elif action == "select_deal":
                selected_slug = request.form.get("deal_slug", "").strip()
                if selected_slug in deals:
                    session["selected_deal"] = selected_slug
                    selected_name = deals[selected_slug].get("name")
                    flash(f"Switched to {selected_name}.", "success")
                else:
                    flash("That deal could not be found.", "error")
                return redirect(url_for("dashboard"))

            elif action == "add_interaction":
                if not selected_slug:
                    flash("Select or create a deal before adding an interaction.", "error")
                else:
                    text = request.form.get("interaction", "").strip()
                    if not text:
                        flash("Interaction text is required.", "error")
                    else:
                        try:
                            core.retain_interaction(selected_slug, text)
                            flash("Interaction stored successfully in Hindsight memory.", "success")
                        except Exception as exc:  # pragma: no cover - environment failure path
                            flash(f"Could not save the interaction: {exc}", "error")
                return redirect(url_for("dashboard"))

            elif action == "run_analysis":
                if not selected_slug:
                    flash("Select or create a deal before running analysis.", "error")
                else:
                    mode = request.form.get("mode", "risk")
                    question = request.form.get("question", "").strip() or None
                    try:
                        analysis = core.analyze(mode, selected_slug, question)
                    except Exception as exc:  # pragma: no cover - environment failure path
                        flash(f"Analysis failed: {exc}", "error")
                return render_template(
                    "dashboard.html",
                    deals=core.load_deals(),
                    selected_slug=selected_slug,
                    selected_name=selected_name,
                    interactions=core.load_deals().get(selected_slug, {}).get("interactions", []),
                    analysis=analysis,
                )

            elif action == "ask_question":
                if not selected_slug:
                    flash("Select or create a deal before asking a question.", "error")
                else:
                    question = request.form.get("question", "").strip()
                    if not question:
                        flash("Please enter a question to ask the agent.", "error")
                    else:
                        try:
                            analysis = _build_general_answer(selected_slug, question)
                            flash("Insights generated from previous deal context.", "success")
                        except Exception as exc:  # pragma: no cover - environment failure path
                            flash(f"Question failed: {exc}", "error")
                return render_template(
                    "dashboard.html",
                    deals=core.load_deals(),
                    selected_slug=selected_slug,
                    selected_name=selected_name,
                    interactions=core.load_deals().get(selected_slug, {}).get("interactions", []),
                    analysis=analysis,
                )

        if selected_slug and selected_slug in deals:
            interactions = deals[selected_slug].get("interactions", [])
            selected_name = deals[selected_slug].get("name")

        return render_template(
            "dashboard.html",
            deals=deals,
            selected_slug=selected_slug,
            selected_name=selected_name,
            interactions=interactions,
            analysis=analysis,
        )

    @app.route("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
