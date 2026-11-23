from common.config import BaseAppSettings
from common.exceptions import BadRequestError, NotFoundError


def test_base_settings_defaults():
    settings = BaseAppSettings(app_name="TestApp", environment="test")
    assert settings.app_name == "TestApp"
    assert settings.environment == "test"
    assert settings.debug is False


def test_exception_status_codes():
    nf = NotFoundError("Item missing")
    assert nf.status_code == 404
    assert nf.code == "NOT_FOUND"

    br = BadRequestError("Invalid parameter")
    assert br.status_code == 400
