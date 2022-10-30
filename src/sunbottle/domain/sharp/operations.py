import time
from typing import Optional

from django.conf import settings
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By

from sunbottle.data.sharp import constants as sharp_constants


class AlreadyLoggedIn(Exception):
    """
    Raised when we already have an active session.
    """


def login_browser(browser: webdriver.Firefox, url: Optional[str] = None):
    # Open the login page
    url = url or sharp_constants.GENERATION_URL
    browser.get(url)
    # Wait for the redirects to finish and the page to finish loading.
    time.sleep(_get_sleep_time())

    # Fill out the password form if we're not already logged in.
    try:
        browser.find_element(By.NAME, "memberId").send_keys(settings.SHARP_LOGIN_MEMBERID)
        browser.find_element(By.ID, "password").send_keys(settings.SHARP_LOGIN_PASSWORD)
    except exceptions.NoSuchElementException:
        # We already have an active session...probably.
        raise AlreadyLoggedIn()
    else:
        # Submit the form using their JS function, as submitting the form doesn't work.
        browser.execute_script("doSubmit()")


def _get_sleep_time() -> int:
    return 5
