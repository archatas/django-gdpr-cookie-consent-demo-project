from urllib.parse import unquote
from time import sleep

from django.conf import settings
from django.test import LiveServerTestCase
from django.test import override_settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

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
        chrome_options.add_argument("--window-size=1200,800")

        cls.browser = webdriver.Chrome(
            executable_path=driver_path, options=chrome_options
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    def wait_until_element_found(self, css_selector):
        return WebDriverWait(self.browser, timeout=10).until(
            lambda x: self.browser.find_element_by_css_selector(css_selector)
        )

    def wait_a_little(self, seconds=2):
        if SHOW_BROWSER:
            sleep(seconds)

    def test_01_accept_all_cookies(self):
        """
        Tries to accept all cookies in the modal dialog.
        """
        self.browser.delete_all_cookies()
        self.browser.get(f"{self.live_server_url}/")
        button = self.wait_until_element_found("#cc_accept_all_cookies")

        self.browser.execute_script("""
            document.getElementById('cc_accept_all_cookies').focus();
        """)
        self.wait_a_little()
        button.click()
        self.wait_a_little(3)

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
        button = self.wait_until_element_found("#cc_reject_all_cookies")

        self.browser.execute_script("""
            document.getElementById('cc_reject_all_cookies').focus();
        """)
        self.wait_a_little()
        button.click()
        self.wait_a_little(3)

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
        button = self.wait_until_element_found("#cc_manage_cookies")

        self.browser.execute_script("""
            document.getElementById('cc_manage_cookies').focus();
        """)
        self.wait_a_little()
        button.click()
        self.wait_a_little()
        switch = self.browser.find_elements_by_css_selector(".cc-switch")[1]
        self.browser.execute_script("""
            document.querySelectorAll('.cc-switch')[1].focus();
        """)
        switch.click()
        self.wait_a_little()
        self.browser.execute_script("""
            document.getElementById('cc_save_preferences').focus();
        """)
        self.browser.find_element_by_id("cc_save_preferences").click()
        self.wait_a_little(3)

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
        button = self.wait_until_element_found("#cc_modal_close")

        self.browser.execute_script("""
            document.getElementById('cc_modal_close').focus();
        """)
        self.wait_a_little()
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
        self.browser.execute_script("""
            document.getElementById('manage_cookies').focus();
        """)
        self.wait_a_little()
        self.browser.find_element_by_id("manage_cookies").click()
        button = self.wait_until_element_found("#cc_accept_all")
        button.click()
        self.wait_a_little()
        self.browser.execute_script("""
            document.getElementById('cc_save_preferences').focus();
        """)
        self.browser.find_element_by_id("cc_save_preferences").click()
        button = self.wait_until_element_found("#manage_cookies")
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
        button.click()
        button = self.wait_until_element_found("#cc_reject_all")
        button.click()
        self.wait_a_little()
        self.browser.execute_script("""
            document.getElementById('cc_save_preferences').focus();
        """)
        self.browser.find_element_by_id("cc_save_preferences").click()
        self.wait_until_element_found("#manage_cookies")
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
