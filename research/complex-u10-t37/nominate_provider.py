# SPDX-License-Identifier: Apache-2.0
"""Bind the newly checked U10 provider into the T37 nomination before freezing.

The original T37 parent builder carries a U8 provider descriptor. This step
changes only the provider's authenticated artifacts and per-call program IDs;
the independently checked geometry, order, owners and profile remain fixed.
"""
import argparse
import copy
from pathlib import Path
from support import P, T21, read, sha, dump, load


def nominate(local, plan_path):
    before = read(plan_path)
    plan = copy.deepcopy(before)
    word = read(local/'CANONICAL-WORD.json.gz')
    checks = read(local/'LOCAL-CHECKS.json')
    assert word['local_profile'] == read(P/'CLAIM.json')['local_profile']
    assert set(plan['provider_registry']) == {'gauge44'}
    desc = plan['provider_registry']['gauge44']
    widths = [len(word['frames'][word['final'][224+h]]) -
              len(word['frames'][word['start'][224+h]]) for h in range(word['R'])]
    assert (word['v'], word['h'], word['R']) == (112, 9, 504)
    assert word['ports'] == desc['ports'] and word['centers'] == desc['centers']
    assert widths == desc['widths'] and sum(widths) == 3778
    module = load(T21/'vendor/pr870/code/generated_identity.py', 'u10_provider_identities')
    identities = module.artifact_identities(local)
    hashes = {name: sha(local/name) for name in module.FILES}
    assert set(hashes) == set(desc['artifact_sha256'])
    assert set(checks) == {'forward', 'backward'}
    for orientation, values in checks.items():
        assert values['paid_profile'] == word['local_profile']
    desc.update(artifact_sha256=hashes, artifact_semantic_sha256=identities,
                actual_paid_profile=word['local_profile'],
                orientation_program_sha256={o: checks[o]['sha256'] for o in checks})
    for call in plan['provider_calls']:
        assert call['provider'] == 'gauge44'
        assert call['orientation'] == ('forward' if call['stage'] % 2 == 0 else 'backward')
        call['local_program_sha256'] = checks[call['orientation']]['sha256']
    assert {k: v for k, v in plan.items() if k not in ('provider_registry','provider_calls')} == {
        k: v for k, v in before.items() if k not in ('provider_registry','provider_calls')}
    previous = plan_path.with_name('PLAN-U8-PROVIDER.json')
    assert not previous.exists()
    previous.write_bytes(plan_path.read_bytes())
    dump(plan_path, plan)
    dump(plan_path.with_name('U10-PROVIDER-NOMINATION.json'),
         dict(status='PASS_U10_PROVIDER_NOMINATION_SAME_T37_GEOMETRY',
              previous_plan_sha256=sha(previous), plan_sha256=sha(plan_path),
              native_artifact_sha256=hashes, native_semantic_sha256=identities,
              only_changed_fields=['provider_registry.artifact_sha256',
                                   'provider_registry.artifact_semantic_sha256',
                                   'provider_registry.actual_paid_profile',
                                   'provider_registry.orientation_program_sha256',
                                   'provider_calls.local_program_sha256']))
    print('PASS_U10_PROVIDER_NOMINATION_SAME_T37_GEOMETRY')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    nominate(args.local.resolve(), args.plan.resolve())
