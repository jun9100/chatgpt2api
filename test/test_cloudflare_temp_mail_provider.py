import unittest

from services.register.mail_provider import CloudflareTempMailProvider


class FakeResponse:
    status_code = 200
    text = "{}"

    def json(self):
        return {"address": "test@example.com", "jwt": "mailbox-token"}


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, headers=None, params=None, json=None, timeout=None, verify=None):
        self.calls.append({"method": method, "url": url, "headers": headers or {}, "params": params, "json": json, "timeout": timeout, "verify": verify})
        return FakeResponse()

    def close(self):
        pass


class CloudflareTempMailProviderTests(unittest.TestCase):
    def test_private_site_password_is_sent_as_custom_auth_header(self):
        provider = CloudflareTempMailProvider(
            {
                "api_base": "https://mail.example.com/",
                "admin_password": "admin-secret",
                "site_password": "site-secret",
                "domain": ["example.com"],
            },
            {"user_agent": "test-agent", "request_timeout": 30},
        )
        provider.session = FakeSession()

        mailbox = provider.create_mailbox("alice")

        self.assertEqual(mailbox["address"], "test@example.com")
        headers = provider.session.calls[0]["headers"]
        self.assertEqual(headers["x-admin-auth"], "admin-secret")
        self.assertEqual(headers["x-custom-auth"], "site-secret")

    def test_custom_auth_alias_is_supported_for_backwards_compatibility(self):
        provider = CloudflareTempMailProvider(
            {
                "api_base": "https://mail.example.com/",
                "admin_password": "admin-secret",
                "custom_auth": "legacy-secret",
                "domain": ["example.com"],
            },
            {"user_agent": "test-agent", "request_timeout": 30},
        )
        provider.session = FakeSession()

        provider.get_existing_mailbox("alice@example.com")

        self.assertEqual(provider.session.calls[0]["headers"]["x-custom-auth"], "legacy-secret")


if __name__ == "__main__":
    unittest.main()