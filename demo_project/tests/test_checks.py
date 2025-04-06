from io import StringIO

from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import SimpleTestCase, override_settings


class SystemCheckIntegrationTest(SimpleTestCase):
    """
    Here's the overview of all gdpr_cookie_consent errors Django system checks to test:
    - gdpr_cookie_consent.E001: `COOKIE_CONSENT_SETTINGS` is not defined in the settings.
    - gdpr_cookie_consent.E002: `["base_template_name"]` is not defined in `COOKIE_CONSENT_SETTINGS`.
    - gdpr_cookie_consent.E003: Template defined in `["*_template_name"]` doesn't exist.
    - gdpr_cookie_consent.E004: You cannot set both, `["*"]` and `["*_template_name"]`.
    - gdpr_cookie_consent.E005: `["dialog_position"]` must be one of `"center"`, `"top"`, `"left"`, `"right"`, `"bottom"`.
    - gdpr_cookie_consent.E006: `["sections"]` must contain at least one section.
    - gdpr_cookie_consent.E007: Each section must have a `["slug"]` defined.
    - gdpr_cookie_consent.E008: Slugs for sections must be unique.
    - gdpr_cookie_consent.E009: Each section must have at least one provider defined.
    - gdpr_cookie_consent.E010: Each provider must have at least one cookie defined.
    """

    @override_settings(COOKIE_CONSENT_SETTINGS=None)
    def test_configuration_missing(self):
        """
        gdpr_cookie_consent.E001: `COOKIE_CONSENT_SETTINGS` is not defined in the settings.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E001)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            # "base_template_name": "base.html", # <--
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_base_template_name_not_defined(self):
        """
        gdpr_cookie_consent.E002: `["base_template_name"]` is not defined in `COOKIE_CONSENT_SETTINGS`.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E002)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/THIS_TEMPLATE_DOESNT_EXIST.html", # <--
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_template_doesnt_exist(self):
        """
        gdpr_cookie_consent.E003: Template defined in `["*_template_name"]` doesn't exist.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E003)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "WHAT ARE COOKIES?", # <--
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html", # <--
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_duplicate_description_definition(self):
        """
        gdpr_cookie_consent.E004: You cannot set both, `["*"]` and `["*_template_name"]`.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E004)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "ABOVE", # <--
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_invalid_dialog_position(self):
        """
        gdpr_cookie_consent.E005: `["dialog_position"]` must be one of `"center"`, `"top"`, `"left"`, `"right"`, `"bottom"`.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E005)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [] # <--
        }
    )
    def test_empty_sections(self):
        """
        gdpr_cookie_consent.E006: `["sections"]` must contain at least one section.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E006)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    # "slug": "essential", # <--
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_no_section_slug(self):
        """
        gdpr_cookie_consent.E007: Each section must have a `["slug"]` defined.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E007)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
                {
                    "slug": "essential", # <--
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [
                                {
                                    "cookie_name": "cookie_consent",
                                    "duration": "6 Years",
                                    "description": "Settings of Cookie Consent preferences.",
                                    "description_template_name": "",
                                    "domain": "127.0.0.1",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    )
    def test_duplicate_section_slug(self):
        """
        gdpr_cookie_consent.E008: Slugs for sections must be unique.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E008)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [] # <--
                },
            ],
        }
    )
    def test_no_section_providers(self):
        """
        gdpr_cookie_consent.E009: Each section must have at least one provider defined.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E009)", stderr.getvalue())

    @override_settings(
        COOKIE_CONSENT_SETTINGS={
            "base_template_name": "base.html",
            "description": "",
            "description_template_name": "gdpr_cookie_consent/descriptions/what_are_cookies.html",
            "extra_information": "",
            "extra_information_template_name": "gdpr_cookie_consent/descriptions/extra.html",
            "dialog_position": "center",
            "sections": [
                {
                    "slug": "essential",
                    "title": "Essential Cookies",
                    "required": True,
                    "preselected": True,
                    "summary": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "summary_template_name": "",
                    "description": "These cookies are always on, as they’re essential for making this website work, and making it safe. Without these cookies, services you’ve asked for can’t be provided.",
                    "description_template_name": "",
                    "providers": [
                        {
                            "title": "This website",
                            "description": "",
                            "description_template_name": "",
                            "cookies": [], # <--
                        },
                    ],
                },
            ],
        }
    )
    def test_no_provider_cookies(self):
        """
        gdpr_cookie_consent.E010: Each provider must have at least one cookie defined.
        """
        stderr = StringIO()
        try:
            call_command("check", "-t", "gdpr_cookie_consent", stderr=stderr)
        except SystemCheckError:
            pass
        else:
            self.assertIn("(gdpr_cookie_consent.E010)", stderr.getvalue())
