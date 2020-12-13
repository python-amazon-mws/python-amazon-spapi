"""We focus on testing and showing some of the ways you can use pydantic."""
import pytest
from pathlib import Path
from pydantic import ValidationError
from spapi import setup


def test_params_env_file():
    """Test the env file without moving it."""
    setup.AccessTokenParams(_env_file=Path('./.sellerpartnerapi.env'))


def test_missing_params_env_file():
    """Test the env file without moving it."""
    with pytest.raises(ValidationError):
        setup.AccessTokenParams(_env_file=Path(
            './tests/data/.invalid_sellerpartnerapi.env'))


def test_fix_missing_params_env_file():
    """Test the env file without moving it."""
    setup.AccessTokenParams(
        client_id='example_id',
        _env_file=Path('./tests/data/.invalid_sellerpartnerapi.env'))


def test_invalid_params():
    """Validation of params."""
    with pytest.raises(ValidationError):
        setup.AccessTokenRequest(params={
            'grant_type': 'refresh_token',
            'refresh_token': 'example1',
            'client_id': 'example2',
            'client_secret': None})


def test_required_params_dict():
    """Validation and completeness of params with overwriting."""
    # not recommended to do in production
    setup.AccessTokenRequest(params={
        'grant_type': 'refresh_token',
        'refresh_token': 'example1',
        'client_id': 'example2',
        'client_secret': 'example3'})


def test_required_params_bymodel():
    """Validation and completeness of params with model."""
    # grant_type has an default value and is optional
    params = setup.AccessTokenParams(
        refresh_token='example1',
        client_id='example2',
        client_secret='example3')
    setup.AccessTokenRequest(params=params)


def test_request_access_token_bymodel():
    """Simple API call to exchange refresh token."""
    expected = (
        'refresh_token=example1'
        '&client_id=example2'
        '&client_secret=example3&'
        'grant_type=refresh_token')
    params = setup.AccessTokenParams(
        refresh_token='example1',
        client_id='example2',
        client_secret='example3')
    setupapi = setup.AccessTokenRequest(params=params)
    token_request = setupapi.prepare_access_token_request()
    prepared_request = token_request.prepare()  # requests prepare() function
    assert prepared_request.body == expected


def test_prepare_access_token_request():
    params = setup.AccessTokenParams(_env_file=Path(
        './.sellerpartnerapi.env'))
    setupapi = setup.AccessTokenRequest(params=params)
    token_request = setupapi.prepare_access_token_request()
    prepared_request = token_request.prepare()
    assert prepared_request.body
    assert prepared_request.url == 'https://api.amazon.com/auth/o2/token'
