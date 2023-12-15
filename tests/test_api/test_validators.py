import unittest

from api.error_msgs import PWD_ERROR_MSGS, REQUIRED_FIELD_MISSING
from api.utils.validators import PasswordValidator, EmailValidator, check_required_fields


class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        password = "ValidP@ssw0rd"
        validator = PasswordValidator(password)
        self.assertTrue(validator.valid_length)
        self.assertTrue(validator.has_uppercase)
        self.assertTrue(validator.has_lowercase)
        self.assertTrue(validator.has_digit)
        self.assertTrue(validator.has_special_char)

    def test_invalid_length(self):
        password = "ShortPwd"
        validator = PasswordValidator(password, min_length=9)
        self.assertFalse(validator.valid_length)

        error_messages = validator.validate()
        self.assertIsInstance(error_messages, list)
        self.assertIn(PWD_ERROR_MSGS["invalid_length"] % 9, error_messages)

    def test_no_different_case(self):
        # Test a password without both uppercase and lowercase letters
        password = "no:password123"
        validator = PasswordValidator(password)
        self.assertTrue(validator.valid_length)
        self.assertFalse(validator.has_uppercase)
        self.assertTrue(validator.has_lowercase)
        self.assertTrue(validator.has_digit)
        self.assertTrue(validator.has_special_char)

        error_messages = validator.validate()
        self.assertIsInstance(error_messages, list)
        self.assertIn(PWD_ERROR_MSGS["has_no_different_case"], error_messages)

    def test_no_digit(self):
        # Test a password without a digit
        password = "NoDigitPassword!"
        validator = PasswordValidator(password)
        self.assertTrue(validator.valid_length)
        self.assertTrue(validator.has_uppercase)
        self.assertTrue(validator.has_lowercase)
        self.assertFalse(validator.has_digit)
        self.assertTrue(validator.has_special_char)

        error_messages = validator.validate()
        self.assertIsInstance(error_messages, list)
        self.assertIn(PWD_ERROR_MSGS["has_no_digit"], error_messages)

    def test_no_special_char(self):
        # Test a password without a special character
        password = "NoSpecialCharPassword123"
        validator = PasswordValidator(password)
        self.assertTrue(validator.valid_length)
        self.assertTrue(validator.has_uppercase)
        self.assertTrue(validator.has_lowercase)
        self.assertTrue(validator.has_digit)
        self.assertFalse(validator.has_special_char)

        error_messages = validator.validate()
        self.assertIsInstance(error_messages, list)
        self.assertIn(PWD_ERROR_MSGS["has_no_special_char"] % validator.SPECIAL_CHAR, error_messages)


class TestEmailValidation(unittest.TestCase):
    def test_valid_emails(self):
        valid_emails = [
            "user@gmail.com",
            "user123@mail.ru",
        ]
        for email in valid_emails:
            validator = EmailValidator(email=email)
            self.assertTrue(validator.is_email_string)

    def test_invalid_emails(self):
        invalid_emails = [
            "invalid_email",
            "user@.com",
            "user@example",
            "user@.co.uk",
            "user@com",
            "user@example.",
        ]
        for email in invalid_emails:
            validator = EmailValidator(email=email)
            self.assertFalse(validator.is_email_string)

    def test_success_supported_domains(self):
        validator = EmailValidator(email="valid_email@gmail.com")
        self.assertTrue(validator.has_supported_domain)

        validator = EmailValidator(email="valid_email@mail.ru")
        self.assertTrue(validator.has_supported_domain)

    def test_failure_supported_domains(self):
        validator = EmailValidator(email="valid_email@gmail.co")
        self.assertFalse(validator.has_supported_domain)

        validator = EmailValidator(email="valid_email@mail.")
        self.assertFalse(validator.has_supported_domain)

        validator = EmailValidator(email="valid_email@example.com")
        self.assertFalse(validator.has_supported_domain)

        validator = EmailValidator(email="valid_email@test.com")
        self.assertFalse(validator.has_supported_domain)


class TestCheckRequiredFields(unittest.TestCase):
    def test_not_found_fields(self):
        result = check_required_fields({}, ("some_required_field",))
        self.assertIsInstance(result, dict)
        self.assertIn('some_required_field', result)
        self.assertEqual(result.get("some_required_field"), REQUIRED_FIELD_MISSING)

    def test_empty_value(self):
        result = check_required_fields({"test_field": ""}, ("test_field",))
        self.assertIsInstance(result, dict)
        self.assertIn('test_field', result)
        self.assertEqual(result.get("test_field"), REQUIRED_FIELD_MISSING)


if __name__ == '__main__':
    unittest.main()
