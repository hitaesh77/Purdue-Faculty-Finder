from fastapi import HTTPException
from backend.app.auth import verify_admin

"""
Unit tests for admin authentication.
Goals:
  - verify_admin succeeds with correct credentials
  - verify_admin fails with incorrect credentials
"""

# Test for successful admin verification
def test_verify_admin_success(monkeypatch):
    class Cred:
        username = "u"
        password = "p"
    monkeypatch.setenv("ADMIN_USER","u")
    monkeypatch.setenv("ADMIN_PASS","p")
    assert verify_admin(Cred())

# Test for failed admin verification
def test_verify_admin_fail(monkeypatch):
    class Cred:
        username = "x"
        password = "y"
    monkeypatch.setenv("ADMIN_USER","u")
    monkeypatch.setenv("ADMIN_PASS","p")
    try:
        verify_admin(Cred())
        assert False
    except HTTPException as e:
        assert e.status_code == 401
