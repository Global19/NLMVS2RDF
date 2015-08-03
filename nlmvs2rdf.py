from __future__ import print_function

import pdb
import sys
from collections import defaultdict

def_header = ['OID', 'ValueSetName', 'VersionComment', 'Version', 'Definition']
code_header = ['OID', 'ValueSetName', 'Version', 'Code', 'Descriptor', 'CodeSystemName', 'CodeSystemVersion', 'CodeSystemOID']

set_attrs = def_header
code_attrs = ["Code","Descriptor","CodeSystemName"]


PREFIXES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix nlmvs: <http://bioportal.bioontology.org/NLMVS/> .
"""

ONTOLOGY_HEADER = """
<http://bioportal.bioontology.org/ontologies/NLMVS>
    a owl:Ontology ;
    a skos:ConceptScheme ;
    rdfs:comment "NIH NLM Value Set as a SKOS ontology" ;
    rdfs:label "NLM Value Sets Ontology" ;
    owl:imports <http://www.w3.org/2004/02/skos/core> ;
    owl:versionInfo "1.0" .

"""

BP_URI = "http://purl.bioontology.org/ontology/%s/%s"
class ValueSet:
    TTL = '''<%s> a skos:Concept;
\tskos:prefLabel """%s"""
'''
    TTL_VAL = '''\t<%s> """%s"""^^xsd:string'''
    REL = "<%s> skos:broader <%s>.\n"
    TOP = ("<http://bioportal.bioontology.org/ontologies/NLMVS> "
    "skos:hasTopConcept <%s>.\n")
    def __init__(self,**data):
        for attr in set_attrs:
            setattr(self,attr,data[attr])
        self.values = []
        self.uri = BP_URI%("NLMVS",self.OID)

    def turtle(self):
        metadata = [ValueSet.TTL%(self.uri,self.ValueSetName)]
        for attr in set_attrs:
            if attr == "ValueSetName":
                continue
            uri_attr = BP_URI%("NLMVS",attr)
            val = self.__dict__[attr]
            metadata.append(ValueSet.TTL_VAL%(uri_attr,val))
        content = ";\n".join(metadata)
        content += ".\n"
        content += ValueSet.TOP%(self.uri)
        for v in self.values:
            content += ValueSet.REL%(v.uri,self.uri)
        return content


class Value:
    TTL = '''<%s> a skos:Concept;
\tskos:prefLabel """%s""" .
'''
    def __init__(self,**data):
        for attr in code_attrs:
            setattr(self,attr,data[attr])
        self.uri = BP_URI%(self.CodeSystemName,self.Code)

    def turtle(self):
        return Value.TTL%(self.uri,self.Descriptor)

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
            if attrs["OID"] in value_sets_idx:
                value_sets_idx[attrs["OID"]].values.append(Value(**attrs))
    value_sets_idx = dict([(_id,_set)
            for (_id,_set) in value_sets_idx.items() if _set.values])
    return value_sets_idx

def value_concepts(value_sets_idx):
    generated = set()
    content = []
    for s in value_sets_idx.values():
        for v in s.values:
            if v.uri in generated:
                continue
            content.append(v.turtle())
    return "\n".join(content)

def set_concepts(value_sets_idx):
    generated = set()
    content = []
    for s in value_sets_idx.values():
        content.append(s.turtle())
    return "\n".join(content)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage python nlmvs2rdf.py def-file-path codes-file-path")
        sys.exit(-1)
    value_sets_def_file = sys.argv[1]
    value_sets_code_file = sys.argv[2]
    value_sets_idx = parse_input_files(
            value_sets_def_file,
            value_sets_code_file)
    value_content = value_concepts(value_sets_idx)
    set_content = set_concepts(value_sets_idx)
    print(PREFIXES)
    print(ONTOLOGY_HEADER)
    print(value_content)
    print(set_content)
