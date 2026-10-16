"""Read-only, source-bound verification of the scoped proof additions."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from crt_layers import need


def bindings():
    source=json.loads((HERE/'SOURCES.json').read_text())
    for item in source['files']:
        if item.get('usage')=='provenance':continue
        need(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],
             'changed predecessor: '+item['path'])
    return sum(item.get('usage')!='provenance' for item in source['files'])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--suite',choices=('all','crt','router','parameters'),default='all')
    args=ap.parse_args()
    results={'source_files':bindings()}
    if args.suite in ('all','crt'):
        import check_crt
        addresses,c1=check_crt.check_addresses()
        fourier,c2=check_crt.check_fourier()
        results['crt']={'addresses':addresses,'fourier':fourier,'rejecting_controls':c1+c2}
    if args.suite in ('all','router'):
        import coordinate_router
        import sparse_router
        results['coordinate_router']=coordinate_router.verify()
        results['sparse_router']={'algebra':sparse_router.algebra(),
                                 'unequal_gaps':sparse_router.unequal_gaps(),
                                 'physical':sparse_router.physical(),
                                 'rejecting_controls':sparse_router.controls()}
    if args.suite in ('all','parameters'):
        import check_parameters
        results['parameters']=check_parameters.verify()
    results['status']='PASS_SCOPED_REFIT_PROOFS'
    results['scope']='Scoped algebra, generated coordinate routing, reduced physical seam, and exact parameter bindings. Full complex dispatch and the uniform analytic source-transform contract remain unproved here.'
    print(json.dumps(results,sort_keys=True,indent=2))


if __name__=='__main__':main()
