"""Retired mounted atlases must not be decoded alongside their replacements."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AtlasDelivery(unittest.TestCase):
    def test_only_current_mounted_atlases_are_preloaded(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        # The generated data is the exact manifest used by loadSPR in production.
        match = re.search(r'const DATA=(\{.*?\});', html)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        for hero in ['yuki', 'kage', 'mitsu', 'nobu', 'shin', 'musashi']:
            self.assertNotIn('mountatk_' + hero, data['spr'])
            current = 'mountfull3_musashi' if hero == 'musashi' else 'mountatk2_' + hero
            self.assertIn(current, data['spr'])
            self.assertIn(current, data['sm'])
            self.assertTrue((ROOT / data['spr'][current].split('?')[0]).is_file())
        self.assertNotIn('mountatk2_musashi', data['spr'])
        self.assertIn('mountbody3_musashi', data['spr'])


if __name__ == '__main__':
    unittest.main()
