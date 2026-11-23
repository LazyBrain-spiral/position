from contracts.models import HealthStatus, PaginationParams, StandardResponse


def test_pagination_params_defaults():
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20


def test_standard_response_wrapping():
    resp = StandardResponse[dict](success=True, data={"key": "value"}, correlation_id="req-123")
    assert resp.success is True
    assert resp.data is not None
    assert resp.data["key"] == "value"
    assert resp.correlation_id == "req-123"


def test_health_status():
    hs = HealthStatus(version="1.0.0", environment="test", uptime_seconds=12.5)
    assert hs.status == "healthy"
    assert hs.uptime_seconds == 12.5
