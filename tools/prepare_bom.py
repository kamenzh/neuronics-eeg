#!/usr/bin/env python3
"""Group exact candidate PCB parts; no stock/price or release claims."""
import csv
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    data=json.loads((ROOT/'hardware/parts.json').read_text())
    design=json.loads((ROOT/'hardware/design.json').read_text())
    actual={p['ref']:p for p in design['parts']}
    assigned=[r for g in data['groups'] for r in g['references']]
    if len(assigned)!=len(set(assigned)) or set(assigned)!=set(actual):
        raise ValueError('Catalog must cover each PCB component exactly once')
    path=ROOT/'hardware/bom/bom-candidates.csv'
    with path.open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(['References','Quantity','Manufacturer','Candidate_MPN','Specification','Footprint','Source','Review_status','Notes'])
        for g in data['groups']:
            ps=[actual[r] for r in g['references']]
            if any(p['mpn']!=g['mpn'] for p in ps):raise ValueError(f"Regenerate design for {g['mpn']}")
            if len({p['fp'] for p in ps})!=1:raise ValueError('Mixed footprints in group')
            w.writerow([' '.join(g['references']),len(ps),g['manufacturer'],g['mpn'],g['specification'],ps[0]['fp'],g['source'],g['status'],g.get('review','')])
    print(f'{len(actual)} PCB components in {len(data["groups"])} candidate groups')

if __name__=='__main__':main()
