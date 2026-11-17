import pytest
from pydantic import ValidationError
from enterprise_ai.core.config import Settings

def test_multiple_mcp_servers_parse():
    cfg=Settings(_env_file=None,mcp_servers_json='[{"name":"tickets","url":"http://localhost:9001/mcp","allowed_tools":["lookup"]},{"name":"ops","url":"https://ops.example/mcp","allowed_tools":["health"]}]')
    servers=cfg.configured_mcp_servers()
    assert [x["name"] for x in servers]==["tickets","ops"]

def test_mcp_duplicate_names_rejected():
    cfg=Settings(_env_file=None,mcp_servers_json='[{"name":"same","url":"http://localhost/mcp","allowed_tools":[]},{"name":"same","url":"http://localhost/other","allowed_tools":[]}]')
    with pytest.raises(ValueError):
        cfg.configured_mcp_servers()

def test_mcp_non_http_url_rejected():
    cfg=Settings(_env_file=None,mcp_servers_json='[{"name":"bad","url":"file:///etc/passwd","allowed_tools":[]}]')
    with pytest.raises(ValueError):
        cfg.configured_mcp_servers()
