from pathlib import Path
from unittest import TestCase

from app.core.config import Settings


class TestSettings(TestCase):
    def test_settings(self):
        test_settings = Settings(_env_file=".env.example")
        self.assertEqual(first=test_settings.APP_NAME, second="llm-p")
        self.assertEqual(first=test_settings.ENV, second="local")

        self.assertEqual(first=test_settings.JWT_SECRET, second="change_me_super_secret")
        self.assertEqual(first=test_settings.JWT_ALG, second="HS256")
        self.assertEqual(first=test_settings.ACCESS_TOKEN_EXPIRE_MINUTES, second=60)

        self.assertEqual(first=test_settings.SQLITE_PATH, second=Path("./app.db"))

        self.assertEqual(first=test_settings.OPENROUTER_API_KEY, second="change_me_openrouter_api_key")
        self.assertEqual(first=test_settings.OPENROUTER_BASE_URL, second="https://openrouter.ai/api/v1")
        self.assertEqual(first=test_settings.OPENROUTER_MODEL, second="stepfun/step-3.5-flash:free")
        self.assertEqual(first=test_settings.OPENROUTER_SITE_URL, second="https://example.com")
        self.assertEqual(first=test_settings.OPENROUTER_APP_NAME, second="llm-fastapi-openrouter")
