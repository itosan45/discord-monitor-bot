"""Grounded boss animation transitions must use the feet, not weapon bounds."""
import json
import sys
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'game/sprites'))
from boss_registration import foot_contact

class BossRegistrationTests(unittest.TestCase):
    def test_grounded_frames_have_shared_contact(self):
        meta=json.loads((ROOT/'game/sprites/sprmeta.json').read_text())
        checked=0
        for key in ('boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9'):
            im=Image.open(ROOT/f'gfx/atlas_{key}.webp').convert('RGBA')
            for an in ('idle','walk','hit','a1','big','dash'):
                for i,q in enumerate(meta[key][an]):
                    fx,fy=foot_contact(im,q)
                    with self.subTest(boss=key,animation=an,frame=i):
                        self.assertAlmostEqual(q[4]+fx*q[6],0,delta=.02)
                        if key=='boss7' and an=='big' and i in (3,4):
                            self.assertLess(q[5]+fy*q[6],-10)
                        else:
                            self.assertAlmostEqual(q[5]+fy*q[6],0,delta=.02)
                    checked+=1
        self.assertEqual(checked,272)

if __name__=='__main__':unittest.main()
