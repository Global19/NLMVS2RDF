from __future__ import print_function

import pdb
import sys

def_header = ['OID', 'ValueSetName', 'Version', 'Definition']
code_header = ['OID', 'ValueSetName', 'Version', 'Code', 'Descriptor', 'CodeSystemName', 'CodeSystemVersion', 'CodeSystemOID']

set_attrs = def_header
code_attrs = ["Code","Descriptor","CodeSystemName"]


class ValueSet:
    def __init__(self,**data):
        for attr in set_attrs:
            setattr(self,attr,data[attr])
        self.values = []

class Value:
    def __init__(self,**data):
        for attr in code_attrs:
            setattr(self,attr,data[attr])

def parse_input_files(defs_path,codes_path):
    value_sets_idx = None
    with open(defs_path,"r") as fin:
        def_content = fin.read().strip()
        def_lines = [x.strip().split("|")
                for x in def_content.split("\n")]
        def_lines.pop(0)
        values_sets = [ValueSet(**dict(zip(def_header,l)))
                for l in def_lines]
        value_sets_idx = dict([(x.OID,x) for x in values_sets])
    with open(codes_path,"r") as fin:
        code_content  = fin.read().strip()
        code_lines = [x.strip().split("|")
                for x in code_content.split("\n")]
        code_lines.pop(0)
        for line in code_lines:
            attrs = dict(zip(code_header,line))
        value_sets_idx[attrs["OID"]].values.append(Value(**attrs))
    value_sets_idx = dict([(_id,_set)
            for (_id,_set) in value_sets_idx.iteritems() if _set.values])
    return value_sets_idx

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage python nlmvs2rdf.py def-file-path codes-file-path")
        sys.exit(-1)
    value_sets_def_file = sys.argv[1]
    value_sets_code_file = sys.argv[2]
    values_sets_idx = parse_input_files(
            value_sets_def_file,
            value_sets_code_file)
