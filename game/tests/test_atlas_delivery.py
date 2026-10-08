"""Retired mounted atlases must not be decoded alongside their replacements."""
import json
import hashlib
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
            self.assertNotIn('mountatk2_' + hero, data['spr'])
            self.assertIn('mountwalk4_' + hero, data['spr'])
            current = 'mountbody3_' + hero
            self.assertIn(current, data['spr'])
            self.assertIn(current, data['sm'])
            self.assertTrue((ROOT / data['spr'][current].split('?')[0]).is_file())
        self.assertNotIn('mountatk2_musashi', data['spr'])
        self.assertIn('mountbody3_musashi', data['spr'])

    def test_pickup_walk_frames_and_hands_ship_together(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        data = json.loads(re.search(r'const DATA=(\{.*?\});', html).group(1))
        for hero in ['musashi', 'nobu', 'shin']:
            key = 'walkbody3_' + hero
            url = data['spr'][key]
            asset = ROOT / url.split('?')[0]
            self.assertEqual(len(data['sm'][key]['walk']), 8)
            self.assertEqual(len(data['hands'][key]['walk']), 8)
            self.assertIn(hashlib.sha256(asset.read_bytes()).hexdigest()[:16], url)


if __name__ == '__main__':
    unittest.main()
