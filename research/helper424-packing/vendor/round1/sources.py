# SPDX-License-Identifier: Apache-2.0
"""Exact PR2894@18d03c44 inputs used by this local investigation."""
from pathlib import Path
import hashlib
SOURCE=Path(__file__).resolve().parent.parent/'shared-kernel-packing'
PINS={
'MANIFEST.json':'3cb842b93dd3b0707ceea825bef2afeaa68f8df0d554867761b4752b69077293',
'vendor/pm/words/WORD-PM-base.json.gz':'c20a470aec0f3e61833cb41fe190639eb358f58017143d2336c55c80fba265eb',
'vendor/pm/words/WORD-PM-extra.json.gz':'db34e39876241087b581ed9374c53e9cd393e3e86ef6103bfb54f3077c3d2761',
'data/PROFILE.json':'528400282a268b6e5983a5251af6040450fa0e7d9ddf7d65e4a0aa6a0b9096a6',
'vendor/pr2857/sources/PR2833-T37-TEMPLATE.json.gz':'21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e',
'vendor/pr2857/audit_relaxation.py':'0e489823b37303ba383648e3fd21aca1b497abc74c297b5b131a3e4684cf5302',
}
def authenticate(source=SOURCE):
    for name,expected in PINS.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('PR2894 source mismatch: '+name)
