from __future__ import annotations

import unittest

from scripts.local_bridge import normalized_api_key_env, override_provider_config, resolve_api_key


class LocalBridgeConfigTest(unittest.TestCase):
    def test_bare_api_key_in_env_field_is_not_written_to_config(self) -> None:
        payload = {
            "provider": "openai",
            "model": "deepseek-v4-pro",
            "base_url": "https://api.deepseek.com",
            "api_key_env": "sk-testbarekey12345678901234567890",
            "api_mode": "chat_completions",
        }

        config = override_provider_config("sources_file: sources.example.yaml\n", payload)

        self.assertEqual(normalized_api_key_env(payload), "DEEPSEEK_API_KEY")
        self.assertEqual(resolve_api_key(payload), "sk-testbarekey12345678901234567890")
        self.assertIn("api_key_env: DEEPSEEK_API_KEY", config)
        self.assertNotIn("sk-testbarekey", config)


if __name__ == "__main__":
    unittest.main()
