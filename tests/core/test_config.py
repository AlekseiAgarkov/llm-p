from pathlib import Path
from unittest import TestCase

from app.core.config import Settings


class TestSettings(TestCase):
    def test_settings(self):
        test_settings = Settings(_env_file=".env.example")
        self.assertEqual("llm-p", test_settings.APP_NAME)
        self.assertEqual("local", test_settings.ENV)

        self.assertEqual("change_me_super_secret", test_settings.JWT_SECRET)
        self.assertEqual("HS256", test_settings.JWT_ALG)
        self.assertEqual(60, test_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        self.assertEqual(Path("./app.db"), test_settings.SQLITE_PATH)

        self.assertEqual("change_me_openrouter_api_key", test_settings.OPENROUTER_API_KEY)
        self.assertEqual("https://openrouter.ai/api/v1", test_settings.OPENROUTER_BASE_URL)
        self.assertEqual("stepfun/step-3.5-flash:free", test_settings.OPENROUTER_MODEL)
        self.assertEqual("https://example.com", test_settings.OPENROUTER_SITE_URL)
        self.assertEqual("llm-fastapi-openrouter", test_settings.OPENROUTER_APP_NAME)
