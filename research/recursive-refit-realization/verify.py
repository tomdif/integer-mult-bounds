"""Cold source-bound replay; normal runs never rewrite evidence."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import canonical, need


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',required=True,choices=('bit','core','schedule','bridge','controls'))
    parser.add_argument('--emit',action='store_true')
    args=parser.parse_args()
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage']=='input':
            path=HERE.parents[1]/row['path']
            need(sha256(path.read_bytes()).hexdigest()==row['sha256'],'changed repository source: '+row['path'])
    for row in sources['vendor']:
        need(sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],
             'changed retained proof source: '+row['path'])
    if args.suite=='bit':
        import bit_bridge
        result={'arithmetic':bit_bridge.arithmetic(),'physical_setup':bit_bridge.physical_setup()}
    elif args.suite=='core':
        import complex_core
        result=complex_core.run()
    elif args.suite=='schedule':
        import deferred,parameters
        result={'controller':deferred.verify(),'parameters':parameters.run()}
    elif args.suite=='bridge':
        import compact_bridge
        result=compact_bridge.run()
    else:
        import controls
        result=controls.run()
    if not args.emit:
        expected=json.loads((HERE/'evidence'/(args.suite+'.json')).read_text())
        need(canonical(result)==canonical(expected),'complete typed receipt differs: '+args.suite)
    print(json.dumps(result,indent=2,sort_keys=True))
    print('PASS_RECURSIVE_REFIT_'+args.suite.upper())


if __name__=='__main__':main()
