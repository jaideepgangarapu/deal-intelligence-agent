import threading

import core
from app import create_app


def test_app_loads():
    app = create_app()
    assert app is not None

    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_save_reports_success(monkeypatch):
    app = create_app()

    def fake_load_deals():
        return {"alpha": {"name": "Alpha", "count": 1, "interactions": [{"number": 1, "text": "Initial note."}]}}

    def fake_retain(slug, text):
        return 1

    monkeypatch.setattr("app.core.load_deals", fake_load_deals)
    monkeypatch.setattr("app.core.retain_interaction", fake_retain)

    client = app.test_client()
    with client.session_transaction() as session:
        session["selected_deal"] = "alpha"

    response = client.post(
        "/dashboard",
        data={"action": "add_interaction", "interaction": "Pricing concerns require a 10% discount."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Interaction stored successfully" in response.data


def test_hindsight_calls_use_fresh_client_per_worker(monkeypatch):
    clients = []

    class FakeHindsight:
        def __init__(self, **kwargs):
            self.closed = False
            clients.append(self)

        def retain(self, **kwargs):
            assert threading.current_thread() is not threading.main_thread()
            return self

        def close(self):
            self.closed = True

    monkeypatch.setattr(core, "Hindsight", FakeHindsight)

    first = core._run_hindsight_call("retain", bank_id="test", content="first")
    second = core._run_hindsight_call("retain", bank_id="test", content="second")

    assert first is clients[0]
    assert second is clients[1]
    assert first is not second
    assert all(client.closed for client in clients)
