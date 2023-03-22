import json
import os

import pytest
from fastapi import Depends, HTTPException, status
from fastapi.dependencies.utils import get_dependant
from fastapi.testclient import TestClient
from api.app_decorator import app, router


client = TestClient(router)


def test_warning():
    resp = client.get(
        '/warnings',
    )
    print(resp)
    assert resp.status_code == 200
    assert resp.json() == {"return": '/warnings response'}


def test_httpexception():
    with pytest.raises(HTTPException) as excinfo:
        resp = client.get(
            '/httpexception',
        )
        print(resp)
        assert resp.status_code == 403
        assert resp.json() == {"detail": 'httpexception'}

    exc = excinfo.value
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == 'httpexception'
