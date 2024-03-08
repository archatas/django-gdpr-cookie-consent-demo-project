from urllib.parse import unquote
from time import sleep

from django.conf import settings
from django.test import LiveServerTestCase
from django.test import override_settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

from gdpr_cookie_consent.models import CookieConsentRecord


SHOW_BROWSER = getattr(settings, "TESTS_SHOW_BROWSER", False)


@override_settings(DEBUG=True)
class CookieManagementTest(LiveServerTestCase):
    host = "127.0.0.1"
    port = 8001

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        driver_path = settings.BASE_DIR / "drivers" / "chromedriver"
        chrome_options = Options()
        if not SHOW_BROWSER:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--window-position=50,50")

        cls.browser = webdriver.Chrome(
            service=ChromeService(executable_path=driver_path),
            options=chrome_options,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    def wait_until_element_found(self, css_selector):
        return WebDriverWait(self.browser, timeout=10).until(
            lambda x: self.browser.find_element(By.CSS_SELECTOR, css_selector)
        )

    def wait_until_element_found_and_interactable(self, css_selector):
        return WebDriverWait(self.browser, timeout=10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

    def wait_a_little(self, seconds=2):
        if SHOW_BROWSER:
            sleep(seconds)

    def focus_element(self, css_selector):
        self.browser.execute_script(f"""
            document.querySelector('{css_selector}').scrollIntoView(true);
            document.querySelector('{css_selector}').focus();
        """)
        self.wait_a_little(1)
        element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
        action = webdriver.ActionChains(self.browser)
        action.move_to_element(element).perform()
        self.wait_a_little(1)
        return element

    def test_01_accept_all_cookies(self):
        """
        Tries to accept all cookies in the modal dialog.
        """
        self.browser.delete_all_cookies()
        self.browser.get(f"{self.live_server_url}/")
        # self.wait_a_little(30)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_accept_all_cookies")
        self.focus_element("#cc_accept_all_cookies")
        button.click()
        self.wait_a_little()

        self.assertEqual(
            unquote(self.browser.get_cookie("cookie_consent")["value"]),
            "functionality|performance|marketing",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("functionality_cookie")["value"]), "🛠",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("performance_cookie")["value"]), "📊",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("marketing_cookie")["value"]), "📢",
        )
        self.assertEqual(CookieConsentRecord.objects.count(), 1)

    def test_02_reject_all_cookies(self):
        """
        Tries to reject all cookies in the modal dialog.
        """
        self.browser.delete_all_cookies()
        self.browser.get(f"{self.live_server_url}/")
        # self.wait_a_little(4)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_reject_all_cookies")
        self.focus_element("#cc_reject_all_cookies")
        button.click()
        self.wait_a_little()

        self.assertEqual(
            unquote(self.browser.get_cookie("cookie_consent")["value"]),
            '""',
        )
        self.assertEqual(
            self.browser.get_cookie("functionality_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("performance_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("marketing_cookie"), None,
        )
        self.assertEqual(CookieConsentRecord.objects.count(), 1)

    def test_03_accept_only_functionality_cookies(self):
        """
        Tries to manage cookies and accept only functionality cookies in the modal dialog.
        """
        self.browser.delete_all_cookies()
        self.browser.get(f"{self.live_server_url}/")
        # self.wait_a_little(4)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_manage_cookies")
        self.focus_element("#cc_manage_cookies")
        button.click()
        switch = self.focus_element("#cc_switch_functionality")
        switch.click()
        button = self.wait_until_element_found_and_interactable("#cc_save_preferences")
        self.focus_element("#cc_save_preferences")
        button.click()
        self.wait_a_little()

        self.assertEqual(
            unquote(self.browser.get_cookie("cookie_consent")["value"]),
            "functionality",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("functionality_cookie")["value"]), "🛠",
        )
        self.assertEqual(
            self.browser.get_cookie("performance_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("marketing_cookie"), None,
        )
        self.assertEqual(CookieConsentRecord.objects.count(), 1)

    def test_04_manage_cookies(self):
        """
        Tries to
        1. close the modal dialog,
        2. click on "manage cookies" link,
        3. accept all cookies,
        4. then click on "manage cookies" again,
        5. and reject all cookies.
        """
        self.browser.delete_all_cookies()
        self.browser.get(f"{self.live_server_url}/")
        # self.wait_a_little(4)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_modal_close")
        self.focus_element("#cc_modal_close")
        button.click()

        self.assertEqual(
            self.browser.get_cookie("cookie_consent"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("functionality_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("performance_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("marketing_cookie"), None,
        )
        link = self.browser.find_element(By.CSS_SELECTOR, "#manage_cookies")
        self.focus_element("#manage_cookies")
        link.click()
        button = self.wait_until_element_found("#cc_accept_all")
        self.focus_element("#cc_accept_all")
        button.click()
        self.wait_a_little()
        button = self.browser.find_element(By.CSS_SELECTOR, "#cc_save_preferences")
        self.focus_element("#cc_save_preferences")
        button.click()
        self.wait_a_little()

        link = self.wait_until_element_found_and_interactable("#manage_cookies")
        self.focus_element("#manage_cookies")

        self.assertEqual(
            unquote(self.browser.get_cookie("cookie_consent")["value"]),
            "functionality|performance|marketing",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("functionality_cookie")["value"]), "🛠",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("performance_cookie")["value"]), "📊",
        )
        self.assertEqual(
            unquote(self.browser.get_cookie("marketing_cookie")["value"]), "📢",
        )
        link.click()
        button = self.wait_until_element_found("#cc_reject_all")
        self.focus_element("#cc_reject_all")
        button.click()
        self.wait_a_little()
        button = self.browser.find_element(By.CSS_SELECTOR, "#cc_save_preferences")
        self.focus_element("#cc_save_preferences")
        button.click()
        self.wait_a_little()

        self.wait_until_element_found_and_interactable("#manage_cookies")
        self.wait_a_little()

        self.assertEqual(
            unquote(self.browser.get_cookie("cookie_consent")["value"]),
            '""',
        )
        self.assertEqual(
            self.browser.get_cookie("functionality_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("performance_cookie"), None,
        )
        self.assertEqual(
            self.browser.get_cookie("marketing_cookie"), None,
        )
        self.assertEqual(CookieConsentRecord.objects.count(), 2)
