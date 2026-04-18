import os
from importlib import import_module
from copy import deepcopy
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.test import override_settings

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from gdpr_cookie_consent.models import CookieConsentRecord

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

SHOW_BROWSER = getattr(settings, "TESTS_SHOW_BROWSER", False)
COOKIE_CONSENT_SETTINGS = deepcopy(settings.COOKIE_CONSENT_SETTINGS)
COOKIE_CONSENT_SETTINGS["redirect_url"] = "test"


@override_settings(DEBUG=True, COOKIE_CONSENT_SETTINGS=COOKIE_CONSENT_SETTINGS)
class CookieManagementTest(LiveServerTestCase):
    host = "127.0.0.1"
    port = 8001

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=not SHOW_BROWSER,
        )
        cls.context = cls.browser.new_context(
            viewport={"width": 1280, "height": 720},
        )

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.page = self.context.new_page()
        self.console_logs = []
        self.page.on("console", lambda msg: self.console_logs.append(msg))

    def tearDown(self):
        self.page.close()
        super().tearDown()

    def wait_until_element_found(self, css_selector):
        self.page.wait_for_selector(css_selector, timeout=10000)
        return self.page.locator(css_selector)

    def wait_until_element_found_and_interactable(self, css_selector):
        self.page.wait_for_selector(css_selector, state="visible", timeout=10000)
        return self.page.locator(css_selector)

    def wait_a_little(self, seconds=2):
        if SHOW_BROWSER:
            self.page.wait_for_timeout(seconds * 1000)

    def focus_element(self, css_selector):
        self.page.evaluate(
            f"""
            window.scrollComplete = false;
            let element = document.querySelector('{css_selector}');

            // Set up scroll end listener
            window.addEventListener('scrollend', function handleScrollEnd() {{
                element.setAttribute('tabindex', '-1');
                element.focus();
                window.scrollComplete = true;
                window.removeEventListener('scrollend', handleScrollEnd);
            }}, {{ once: true }});

            // Trigger scroll (or no-op if already in view)
            element.scrollIntoView({{ block: 'center', behavior: 'smooth' }});

            // Fallback: if no scroll needed, complete immediately
            setTimeout(() => {{
                if (!window.scrollComplete) {{
                    element.setAttribute('tabindex', '-1');
                    element.focus();
                    window.scrollComplete = true;
                }}
            }}, 100);
            """
        )

        self.page.wait_for_function("window.scrollComplete === true", timeout=10000)
        return self.page.locator(css_selector)

    def extract_log_sequence(self):
        """Extracts messages like "functionality cookies granted" or "marketing cookies denied" from console.log()"""
        import re

        granting_denying_pattern = re.compile(r"[a-z]+ cookies (granted|denied)")
        consent_preferences_pattern = re.compile(r"consentPreferences: (\{.+})")
        sequence = []
        for log in self.console_logs:
            if log.type == "log":
                message = log.text
                if group := granting_denying_pattern.search(message):
                    sequence.append(group[0])
                elif group := consent_preferences_pattern.search(message):
                    sequence.append(group[1].replace("\\", ""))
        return sequence

    def test_01_accept_all_cookies(self):
        """
        Tries to accept all cookies in the modal dialog.
        """
        self.context.clear_cookies()
        self.assertEqual(CookieConsentRecord.objects.count(), 0)

        User = get_user_model()
        superuser = User.objects.create_superuser(
            username="admin", password="secret", email="admin@example.com"
        )

        self.page.goto(f"{self.live_server_url}/test/")
        # self.wait_a_little(30)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_accept_all_cookies")
        self.focus_element("#cc_accept_all_cookies")
        button.click()
        self.wait_a_little()

        cookies = {cookie["name"]: unquote(cookie["value"]) for cookie in self.context.cookies()}
        self.assertEqual(
            cookies["cookie_consent"],
            "functionality|performance|marketing",
        )
        self.assertEqual(cookies["functionality_cookie"], "🛠")
        self.assertEqual(cookies["performance_cookie"], "📊")
        self.assertEqual(cookies["marketing_cookie"], "📢")
        self.assertEqual(CookieConsentRecord.objects.count(), 1)
        self.assertIsNone(CookieConsentRecord.objects.first().user)

        sequence = self.extract_log_sequence()
        self.assertEqual(
            sequence,
            [
                "functionality cookies granted",
                "performance cookies granted",
                "marketing cookies granted",
                '{"functionality":true,"performance":true,"marketing":true}',
            ],
        )

        record = CookieConsentRecord.objects.first()
        self.assertEqual(record.user, None)

        session = SessionStore(session_key=cookies["sessionid"])
        self.assertEqual(session.get("ok"), "OK")
        self.assertEqual(session.get("cookie_consent_record_id"), record.pk)

        # Log into /admin/ and verify the consent record gets the user assigned.
        self.page.goto(f"{self.live_server_url}/admin/")
        self.wait_until_element_found("#id_username").fill("admin")
        self.page.locator("#id_password").fill("secret")
        self.page.locator('[type="submit"]').click()
        self.wait_until_element_found("#user-tools")  # admin dashboard loaded

        record.refresh_from_db()
        self.assertEqual(record.user, superuser)

    def test_02_reject_all_cookies(self):
        """
        Tries to reject all cookies in the modal dialog.
        """
        self.context.clear_cookies()
        self.page.goto(f"{self.live_server_url}/test/")
        # self.wait_a_little(4)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_reject_all_cookies")
        self.focus_element("#cc_reject_all_cookies")
        button.click()
        self.wait_a_little()

        cookies = {cookie["name"]: unquote(cookie["value"]) for cookie in self.context.cookies()}
        self.assertEqual(cookies["cookie_consent"], '""')
        self.assertNotIn("functionality_cookie", cookies)
        self.assertNotIn("performance_cookie", cookies)
        self.assertNotIn("marketing_cookie", cookies)
        self.assertEqual(CookieConsentRecord.objects.count(), 1)

        sequence = self.extract_log_sequence()
        self.assertEqual(
            sequence,
            [
                "functionality cookies denied",
                "performance cookies denied",
                "marketing cookies denied",
                '{"functionality":false,"performance":false,"marketing":false}',
            ],
        )

    def test_03_accept_only_functionality_cookies(self):
        """
        Tries to manage cookies and accept only functionality cookies in the modal dialog.
        """
        self.context.clear_cookies()
        self.page.goto(f"{self.live_server_url}/test/")
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

        cookies = {cookie["name"]: unquote(cookie["value"]) for cookie in self.context.cookies()}
        self.assertEqual(cookies["cookie_consent"], "functionality")
        self.assertEqual(cookies["functionality_cookie"], "🛠")
        self.assertNotIn("performance_cookie", cookies)
        self.assertNotIn("marketing_cookie", cookies)
        self.assertEqual(CookieConsentRecord.objects.count(), 1)

        sequence = self.extract_log_sequence()
        self.assertEqual(
            sequence,
            [
                "functionality cookies granted",
                "performance cookies denied",
                "marketing cookies denied",
                '{"functionality":true,"performance":false,"marketing":false}',
            ],
        )

    def test_04_manage_cookies(self):
        """
        Tries to
        1. close the modal dialog,
        2. click on "manage cookies" link,
        3. accept all cookies,
        4. then click on "manage cookies" again,
        5. and reject all cookies.
        """
        self.context.clear_cookies()
        self.page.goto(f"{self.live_server_url}/test/")
        # self.wait_a_little(4)  # DEBUG: for the screen recording
        button = self.wait_until_element_found("#cc_modal_close")
        self.focus_element("#cc_modal_close")
        button.click()

        cookies = {cookie["name"]: unquote(cookie["name"]) for cookie in self.context.cookies()}
        self.assertNotIn("cookie_consent", cookies)
        self.assertNotIn("functionality_cookie", cookies)
        self.assertNotIn("performance_cookie", cookies)
        self.assertNotIn("marketing_cookie", cookies)

        link = self.page.locator("#manage_cookies")
        self.focus_element("#manage_cookies")
        link.click()
        button = self.wait_until_element_found("#cc_accept_all")
        self.wait_a_little(3)  # wait for JS animation to finish
        self.focus_element("#cc_accept_all")
        button.click()
        self.wait_a_little()
        button = self.page.locator("#cc_save_preferences")
        self.focus_element("#cc_save_preferences")
        self.wait_a_little()
        button.click()
        self.wait_a_little()

        link = self.wait_until_element_found_and_interactable("#cc_message")

        cookies = {cookie["name"]: unquote(cookie["value"]) for cookie in self.context.cookies()}
        self.assertEqual(
            cookies["cookie_consent"],
            "functionality|performance|marketing",
        )
        self.assertEqual(cookies["functionality_cookie"], "🛠")
        self.assertEqual(cookies["performance_cookie"], "📊")
        self.assertEqual(cookies["marketing_cookie"], "📢")

        button = self.wait_until_element_found("#cc_reject_all")
        self.focus_element("#cc_reject_all")
        button.click()
        self.wait_a_little()
        button = self.page.locator("#cc_save_preferences")
        self.focus_element("#cc_save_preferences")
        self.wait_a_little()
        button.click()
        self.wait_a_little()

        self.wait_until_element_found_and_interactable("#cc_message")
        self.wait_a_little()

        cookies = {cookie["name"]: unquote(cookie["value"]) for cookie in self.context.cookies()}
        self.assertEqual(cookies["cookie_consent"], '""',)
        self.assertNotIn("functionality_cookie", cookies)
        self.assertNotIn("performance_cookie", cookies)
        self.assertNotIn("marketing_cookie", cookies)
        self.assertEqual(CookieConsentRecord.objects.count(), 2)

        sequence = self.extract_log_sequence()
        self.assertEqual(
            sequence,
            [
                "functionality cookies granted",
                "performance cookies granted",
                "marketing cookies granted",
                '{"functionality":true,"performance":true,"marketing":true}',
                "functionality cookies denied",
                "performance cookies denied",
                "marketing cookies denied",
                '{"functionality":false,"performance":false,"marketing":false}',
            ],
        )
