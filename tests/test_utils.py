import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from jose import jwt
from app import utils, models

class TestUtils(unittest.TestCase):

    def setUp(self):
        # Підготовка тестових змінних
        self.test_email = "test@example.com"
        self.test_password = "testpassword"
        self.test_hashed_password = utils.get_password_hash(self.test_password)
        self.test_user = models.User(email=self.test_email, hashed_password=self.test_hashed_password)

    def test_get_password_hash(self):
        hashed_password = utils.get_password_hash(self.test_password)
        self.assertTrue(hashed_password.startswith("$2b$"))

    def test_verify_password(self):
        self.assertTrue(utils.verify_password(self.test_password, self.test_hashed_password))
        self.assertFalse(utils.verify_password("wrongpassword", self.test_hashed_password))

    def test_create_access_token(self):
        data = {"sub": self.test_email}
        expires_delta = timedelta(minutes=15)
        token = utils.create_access_token(data, expires_delta)
        decoded_data = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        self.assertEqual(decoded_data["sub"], self.test_email)

    def test_get_current_user(self):
        fake_token = "fake_token"
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = self.test_user

        with patch('app.utils.jwt.decode') as mock_decode:
            mock_decode.return_value = {"sub": self.test_email}
            user = utils.get_current_user(mock_db, fake_token)
            self.assertEqual(user.email, self.test_email)

    @patch('smtplib.SMTP')
    def test_send_verification_email(self, mock_smtp):
        mock_server = mock_smtp.return_value
        utils.send_verification_email(self.test_email, MagicMock())

        # Assert SMTP methods called
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(utils.os.getenv("SMTP_USER"), utils.os.getenv("SMTP_PASSWORD"))
        mock_server.sendmail.assert_called_once()

    def test_verify_email_token(self):
        data = {"sub": self.test_email}
        token = utils.create_access_token(data)
        verified_email = utils.verify_email_token(token)
        self.assertEqual(verified_email, self.test_email)

if __name__ == '__main__':
    unittest.main()



