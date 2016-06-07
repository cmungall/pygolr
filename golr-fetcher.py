#!/usr/bin/env python3
"""Script for downloading associations from GO Database for a given species."""
# -*- coding: UTF-8 -*-
from __future__ import print_function

"""
Fetch associations for S Pombe (NCBI Taxonomy ID 4896)
>>> python {SCR} --taxon_id 4896 -o spombe.assocs

The output format is the same as for 

    SPBC18H10.18c   GO:0008150;GO:0005737;GO:0016021;GO:0003674
    mis13   GO:0005634;GO:0005515;GO:0031617;GO:0000070;GO:0000779;GO:0000941;GO:0000444
    fap7    GO:0016887;GO:0005634;GO:0000462;GO:0004017;GO:0005524;GO:0017111;GO:0005829
    SPCC594.01      GO:0008150;GO:0005575;GO:0003674

Other useful taxon IDs:

 - 9606 Human
 - 10090 Mouse

Note that sometimes it is necessary to use the strain ID. See: http://geneontology.org/page/download-annotations

TODO: allow use of taxon labels, allow custom filtering

""".format(SCR=__file__)

import pysolr
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))



def main():
    """Fetch simple gene-term assocaitions from Golr using bioentity document type, one line per gene."""
    import argparse
    prs = argparse.ArgumentParser(__doc__,
                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    prs.add_argument('--golr_url', default='https://solr.monarchinitiative.org/solr/golr/', type=str,
                     help='Golr URL')
    prs.add_argument('-o', default=None, type=str,
                     help="Specifies the name of the output file")
    prs.add_argument('-m','--max_rows', default=10, type=int,
                     help="maximum rows to be fetched")
    prs.add_argument('-k','--truncate', action='store_true', default=False,
                     help="true if truncation OK")
    prs.add_argument('-n','--noheader', action='store_true', default=False,
                     help="set if you want a header")
    prs.add_argument('-f','--fields', nargs='+', default=['subject_taxon','subject_gene','subject_gene_label','object','object_label'],
                     help="SELECT")
    prs.add_argument('-q','--query', nargs='+', default=[],
                     help="query K=V*")
    prs.add_argument('-x','--extrafields', nargs='+', default=[],
                     help="additional SELECTs")
    prs.add_argument('-t', '--type', default='gene-disease', type=str,
                     help="Specifies the name of the output file. Hyphen-delimited. E.g. gene-disease")

    args = prs.parse_args()

    solr = pysolr.Solr(args.golr_url, timeout=30)
    fl = args.fields
    fl.extend(args.extrafields)
    if len(fl) == 1 and (fl[0] == '*' or fl[0] == ''):
        fl=[]
    
    [subject_category, object_category] = args.type.split('-')

    qmap = { 'subject_category' : subject_category, 'object_category' : object_category }
    if len(args.query) > 0:
        for qa in args.query:
            [k,v]=qa.split("=")
            qmap[k] = v
    qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])
    
    results = solr.search(q=qstr,
                          fl=",".join(fl), rows=args.max_rows)
    #sys.stderr.write("NUM ROWS:"+str(len(results))+"\n")
    if (len(results) ==0):
        sys.stderr.write("NO RESULTS")
        exit(1)
    if (len(results) == args.max_rows and not args.truncate):
        sys.stderr.write("max_rows set too low")
        exit(1)

    file_out = sys.stdout if args.o is None else open(args.o, 'w')
    if not args.noheader and len(fl) > 0:
        file_out.write("\t".join(fl))
        file_out.write("\n")
    for r in results:
        if len(fl) == 0:
            fl = r.keys()
            file_out.write("\t".join(fl))
            file_out.write("\n")

        file_out.write("\t".join([str(r[f]) if f in r else "" for f in fl]))
        file_out.write("\n")

    if args.o is not None:
        file_out.close()
        sys.stdout.write("  WROTE: {}\n".format(args.o))

if __name__ == "__main__":
    main()
