from bs4 import BeautifulSoup

def test_password_hashing(test_user):
    assert test_user.check_password("testpass") is True
    assert test_user.check_password("wrongpass") is False