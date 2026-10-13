"""Rebuild the X54 scalar edit and literal frame assignments without a solver.

The mapped scalar recipe is retained from Rohan Arun's PR1207, using Jeremy
Kothe's X54 operation and chafreaky's PR1196 constructor. The exact frame
assignments here were independently regenerated with PR1186's toolkit.
"""
import argparse
from pathlib import Path
from common import P,read,dump,load,identity,sha

def build(source,out):
    assert not out.exists()
    word=read(source)
    assert word==read(P/'vendor/pr1195/FULL-WORD.json.gz')
    recipe=read(P/'vendor/pr1207/MAPPED-RECIPE.json')
    constructor=load(P/'vendor/pr1207/build_tri.py','retained_x54_constructor')
    word=constructor.apply(word,recipe)
    frames=read(P/'data/X54-FRAMES.json')
    assert set(frames)=={'A','B','early_cleanup','cleanup','report'}
    for section in ('A','B','early_cleanup','cleanup'):
        for i,old,new in frames[section]:
            assert word[section][i]==old and old[:-1]==new[:-1]
            word[section][i]=new
    word['report']=frames['report']
    assert word==read(P/'data/THREE-WORD.json.gz')
    dump(out,word)
    return dict(status='PASS_LITERAL_X54_COMPOSITION',content_sha256=identity(word),
      recipe_sha256=sha(P/'vendor/pr1207/MAPPED-RECIPE.json'),frames_sha256=sha(P/'data/X54-FRAMES.json'))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();print(build(a.source,a.out)['status'])
