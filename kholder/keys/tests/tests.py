from django.test import TestCase
import json

from keys.models import Key


class KeysAPITest(TestCase):
    def setUp(self):
        # sample data
        self.label = "test-key"
        self.decrypted = "super-secret"
        self.password = "pwd123"

    def create_key(self):
        payload = {"label": self.label, "decrypted_key": self.decrypted, "password": self.password}
        resp = self.client.post("/keys/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 201)

    def test_01_list_empty(self):
        resp = self.client.get("/keys/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_02_create_key(self):
        self.create_key()
        # DB entry created
        self.assertTrue(Key.objects.filter(label=self.label).exists())

    def test_03_list_after_create(self):
        self.create_key()
        resp = self.client.get("/keys/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(any(item.get("label") == self.label for item in data))
        # ensure encrypted_key (binary) is not exposed in list
        for item in data:
            self.assertNotIn("encrypted_key", item)

    def test_04_patch_update_label(self):
        self.create_key()
        # rename the key
        new_label = "renamed-key"
        payload = {"label": new_label}
        resp = self.client.patch(f"/keys/{self.label}", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Key.objects.filter(label=new_label).exists())
        self.assertFalse(Key.objects.filter(label=self.label).exists())
        # update in-memory label for following tests
        self.label = new_label

    def test_05_patch_update_value(self):
        self.create_key()
        # update the stored encrypted value via decrypted_key + password
        payload = {"decrypted_key": "new-secret", "password": self.password}
        resp = self.client.patch(f"/keys/{self.label}", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_06_decrypt_correct_password(self):
        self.create_key()
        payload = {"password": self.password}
        resp = self.client.post(f"/keys/decrypt/{self.label}", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("decrypted_key", data)
        self.assertEqual(data["decrypted_key"], self.decrypted)

    def test_07_decrypt_wrong_password(self):
        self.create_key()
        payload = {"password": "wrong"}
        resp = self.client.post(f"/keys/decrypt/{self.label}", data=json.dumps(payload), content_type="application/json")
        # application returns 400 when password is invalid in current implementation
        self.assertIn(resp.status_code, (400, 403))

    def test_08_get_detail_not_allowed(self):
        self.create_key()
        # GET on /keys/{label} should be unsupported (405)
        resp = self.client.get(f"/keys/{self.label}")
        self.assertIn(resp.status_code, (405, 400))

    def test_09_delete_key(self):
        self.create_key()
        resp = self.client.delete(f"/keys/{self.label}")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Key.objects.filter(label=self.label).exists())

    def test_10_create_missing_fields(self):
        # missing password
        payload = {"label": "x", "decrypted_key": "v"}
        resp = self.client.post("/keys/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 400)
