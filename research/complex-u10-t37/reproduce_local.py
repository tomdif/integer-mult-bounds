# SPDX-License-Identifier: Apache-2.0
"""Run PR987's unchanged local builder through byte-identical PR890 dependencies."""
import gzip
from pathlib import Path
from support import P, T21, read, sha, load

if __name__ == '__main__':
    provenance = read(P/'vendor/pr987/UPSTREAM.json')
    for name, record in provenance['files'].items():
        assert sha(P/'vendor/pr987'/name) == record['sha256']
    module = load(P/'vendor/pr987/reproduce_u10.py', 'original_pr987_u10_driver')
    module.PKG = T21
    module.BARCH = T21/'vendor/pr870/construction/barch'
    module.P6 = T21/'vendor/pr870/construction/layers_p6n'
    module.main()
