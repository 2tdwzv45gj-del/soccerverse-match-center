import json
from unittest.mock import patch

from src.commentary_mcp import SoccerverseMCPClient


def test_parse_json_rpc_result():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": '[{"fixture_id": 123}]',
                }
            ]
        },
    }

    result = SoccerverseMCPClient._parse_response(json.dumps(payload))

    assert result == [{"fixture_id": 123}]


def test_parse_sse_response():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": '{"ok": true}',
                }
            ]
        },
    }

    body = "event: message\ndata: " + json.dumps(payload)

    result = SoccerverseMCPClient._parse_response(body)

    assert result == {"ok": True}


def test_error_response():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -1,
            "message": "test error",
        },
    }

    try:
        SoccerverseMCPClient._parse_response(json.dumps(payload))
    except RuntimeError as exc:
        assert "test error" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")


def test_tool_methods():
    client = SoccerverseMCPClient()

    with patch.object(
        client,
        "_call",
        return_value={"ok": True},
    ) as mocked:
        assert client.get_fixture(123) == {"ok": True}
        mocked.assert_called_with(
            "get_fixture",
            {"fixture_id": 123},
        )

        assert client.get_match_events(123) == {"ok": True}
        mocked.assert_called_with(
            "get_match_events",
            {"fixture_id": 123},
        )

        assert client.get_match_commentary(123) == {"ok": True}
        mocked.assert_called_with(
            "get_match_commentary",
            {"fixture_id": 123},
        )
