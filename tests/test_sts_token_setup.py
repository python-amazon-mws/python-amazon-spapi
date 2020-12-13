"""We focus on testing and showing some of the ways you can use pydantic."""
import pytest
from pathlib import Path
from pydantic import ValidationError
from spapi import setup


def test_params_env_file():
    """Test the env file without moving it."""
    setup.StsTokenRequest(_env_file=Path('./.sellerpartnerapi.env'))


def test_missing_params_env_file():
    """Test the env file without moving it."""
    with pytest.raises(ValidationError):
        setup.StsTokenRequest(_env_file=Path(
            './tests/data/.invalid_sellerpartnerapi.env'))


def test_fix_missing_params_env_file():
    """Test the env file without moving it."""
    setup.StsTokenRequest(
        role_session_name='example_id',
        _env_file=Path('./tests/data/.invalid_sellerpartnerapi.env'))


def test_invalid_params():
    """Validation of params."""
    with pytest.raises(ValidationError):
        setup.StsTokenRequest(params={
            'grant_type': 'refresh_token',
            'refresh_token': 'example1',
            'client_id': 'example2',
            'client_secret': None})
