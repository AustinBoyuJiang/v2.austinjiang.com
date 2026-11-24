import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('privacy', ROOT / 'scripts/check_privacy.py')
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)


class ContactPrivacyTests(unittest.TestCase):
    def test_contact_is_redacted_and_cannot_send(self):
        self.assertEqual(privacy.check((ROOT / 'contact.html').read_text()), [])

    def test_restored_contact_value_is_rejected(self):
        html = (ROOT / 'contact.html').read_text().replace('<h4>redacted</h4>', '<h4>555-0100</h4>', 1)
        self.assertTrue(privacy.check(html))

    def test_restored_message_form_is_rejected(self):
        html = (ROOT / 'contact.html').read_text().replace('</body>', '<form method="post"><input type="submit"></form></body>')
        self.assertTrue(privacy.check(html))

    def test_no_message_submission_code(self):
        script = (ROOT / 'js/main.js').read_text()
        self.assertNotIn('contact_form.php', script)
        self.assertNotIn('$.ajax(', script)
        self.assertFalse((ROOT / 'contact_form/email_template.html').exists())


if __name__ == '__main__':
    unittest.main()
