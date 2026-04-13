from unittest import TestCase

from app.core.config import Settings
from app.core.security import verify_password, create_access_token, decode_token, JWTTokenType, create_refresh_token


class TestSecurity(TestCase):
    settings: Settings
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int

    @classmethod
    def setUpClass(cls):
        cls.settings = Settings(_env_file=".env.example")
        cls.sub = "sub"
        cls.jwt_secret = cls.settings.JWT_SECRET
        cls.jwt_algorithm = cls.settings.JWT_ALG
        cls.jwt_expire_minutes = cls.settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def test_verify_password(self):
        self.assertTrue(verify_password(plain_password="password",
                                        password_hash="$2b$12$egYdvOrgav9UfJ79ei2T2.gIAXIo0Rkmj9iO65VTzsunvToFjFaMy"))

    def test_decode_access_token(self):
        token = create_access_token(
            sub=self.sub,
            jwt_secret=self.jwt_secret,
            jwt_algorithm=self.jwt_algorithm,
            token_expire_minutes=self.jwt_expire_minutes)

        decoded_token = decode_token(token=token,
                                     jwt_secret=self.jwt_secret,
                                     jwt_algorithm=self.jwt_algorithm)

        self.assertEqual(self.sub, decoded_token["sub"])
        self.assertEqual(JWTTokenType.access.name, decoded_token["type"])

    def test_decode_refresh_token(self):
        token, _ = create_refresh_token(
            sub=self.sub,
            jwt_secret=self.jwt_secret,
            jwt_algorithm=self.jwt_algorithm,
            token_expire_minutes=self.jwt_expire_minutes)

        decoded_token = decode_token(token=token,
                                     jwt_secret=self.jwt_secret,
                                     jwt_algorithm=self.jwt_algorithm)

        self.assertEqual(self.sub, decoded_token["sub"])
        self.assertEqual(JWTTokenType.refresh.name, decoded_token["type"])
