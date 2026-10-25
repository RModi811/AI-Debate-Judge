import asyncio

from app.llm import ollama_client


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"response": '{"ok": true}'}


class FakeAsyncClient:
    last_payload = None
    last_timeout = None

    def __init__(self, timeout):
        type(self).last_timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        type(self).last_payload = json
        return FakeResponse()


def test_generate_requests_bounded_json_and_disables_qwen_thinking(monkeypatch):
    monkeypatch.setattr(ollama_client.httpx, "AsyncClient", FakeAsyncClient)

    result = asyncio.run(ollama_client.generate("Return a JSON object.", num_predict=1234))

    assert result == '{"ok": true}'
    payload = FakeAsyncClient.last_payload
    assert payload["format"] == "json"
    assert payload["think"] is False
    assert payload["options"]["num_predict"] == 1234
    assert payload["prompt"].endswith("/no_think")
    assert FakeAsyncClient.last_timeout == 180
