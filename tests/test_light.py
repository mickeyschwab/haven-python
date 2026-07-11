import pytest

from havenlighting.credentials import Credentials
from havenlighting.devices.light import Light
from havenlighting.exceptions import ApiError


@pytest.fixture
def light(mocker):
    credentials = mocker.Mock(spec=Credentials)
    return Light(
        credentials,
        location_id=123,
        light_id=456,
        data={
            "lightId": 456,
            "name": "Test Light",
            "lightingStatusId": 1,
            "lightBrightnessId": 10,
            "colorId": 11,
            "patternSpeedId": 0,
        },
    )


def test_turn_on_success(light):
    light._credentials.make_request.return_value = [
        {"id": 456, "type": "Light", "success": True}
    ]

    light.turn_on()

    assert light.is_on
    light._credentials.make_request.assert_called_once_with(
        "POST", "/Commands/On", json={"id": 456, "type": "Light"}
    )


def test_turn_off_success(light):
    light._data.status = 2  # start "on"
    light._credentials.make_request.return_value = [
        {"id": 456, "type": "Light", "success": True}
    ]

    light.turn_off()

    assert not light.is_on


def test_turn_on_command_failure_raises(light):
    light._credentials.make_request.return_value = [
        {"id": 456, "type": "Light", "success": False}
    ]

    with pytest.raises(ApiError):
        light.turn_on()

    assert not light.is_on
