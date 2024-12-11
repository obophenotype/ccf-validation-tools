from argparse import ArgumentParser
from itertools import product
import re
import pandas as pd
import os
import json

from uberongraph_tools import UberonGraph
from ccf_tools import split_terms, transform_to_str

def get_ct_loc_marker(file):
  def is_valid_id(content):
    if re.match("(CL|UBERON|HGNC)\:[0-9]+", content):
      return content
    else:
      return False

  asct_b = json.load(open(file))

  out = []

  for row in asct_b:
    anatomical_structures = row["anatomical_structures"]
    cell_types = row["cell_types"]
    biomarkers = row["biomarkers"]
    refs = row["references"]

    if not biomarkers or not anatomical_structures or not cell_types:
      continue

    last_as = anatomical_structures[-1]
    last_ct = cell_types[-1]

    if last_ct["id"] == "":
        if len(cell_types) > 1:
            last_ct = cell_types[-2]
            if last_ct["id"] == "":
                continue

    if last_as["id"] == "":
        if len(anatomical_structures) > 1:
            last_as = anatomical_structures[-2]
            if last_as["id"] == "":
                continue

    if not is_valid_id(last_ct["id"]) or not is_valid_id(last_as["id"]):
      continue

    markers_group = sorted([marker["id"] for marker in biomarkers if is_valid_id(marker["id"])])

    if not markers_group:
      continue

    refs_group_doi = [ref["doi"].replace(' ', '') for ref in refs]

    refs_group_pmid = [list(map(lambda x: x.replace(' ', ''), ref["id"].split('.'))) for ref in refs if "PM" in ref["id"]]
    refs_group_pmid = [pid for pmid in refs_group_pmid for pid in pmid]

    r = {}
    r["Terminal AS/ID"] = last_as["id"]
    r["Terminal AS/label"] = last_as["rdfs_label"]
    r["Terminal AS/user_label"] = last_as["name"]
    r["Terminal CT/ID"] = last_ct["id"]
    r["Terminal CT/label"] = last_ct["rdfs_label"]
    r["Terminal CT/user_label"] = last_ct["name"]
    r["Markers"] = ', '.join(markers_group)
    r["References"] = '|'.join(refs_group_doi + refs_group_pmid)
    out.append(r)

  report = None
  if out:
    report = pd.DataFrame.from_records(out).drop_duplicates(["Terminal AS/ID", "Terminal CT/ID", "Markers"]).sort_values("Terminal CT/ID")

  return report

def merge_csv(path):
  dir_path = os.path.dirname(path)
  csv_files = os.listdir(os.path.dirname(path))
  filter = ["cell-loc-diff-markers.tsv", "ct_loc_b_report.tsv"]
  for file in filter:
    csv_files.remove(file)

  pds = []

  for f in csv_files:
    rep = pd.read_csv(f'{dir_path}/{f}', sep='\t')
    name = f.split('_report')
    rep['Table'] = name[0]
    pds.append(rep)

  df = pd.concat(pds, ignore_index=True).drop_duplicates().sort_values("Terminal CT/ID")

  df.to_csv(path, sep='\t', index=False)

  

def create_template(input, relationship):
  output = [{'ID': 'ID', 
             'Label': 'LABEL',
             'Equivalent axioms': 'EC %',
             'Equivalent relationship axioms': f'EC {relationship} some %',
            }]

  for _, row in input.iterrows():
    d = {}
    d['Label'] = f'{row["Terminal CT/label"]} of {row["Terminal AS/label"]}'
    d['Equivalent axioms'] = row["Terminal CT/ID"]
    d['Equivalent relationship axioms'] = row["Terminal AS/ID"]
    output.append(d)
  return pd.DataFrame.from_records(output)

def generate_id(start_range, end_range):
  for i in range(start_range, end_range, 1):
    yield f'CL:{str(i)}'

def create_dosdp_template(input):
  output = []
  cl_id = generate_id(6000011, 6003543)
  for _, row in input.iterrows():
    d = {}
    d["defined_class"] = next(cl_id)
    d["defined_class_label"] = ""
    d["cell"] = row["Terminal CT/ID"]
    d["anatomical_entity"] = row["Terminal AS/ID"]
    d["pubs"] = row["References"]
    output.append(d)

  return pd.DataFrame.from_records(output)
  
def template(args):
  ug = UberonGraph()

  report = pd.read_csv(args.input, sep='\t')
  dir_path = os.path.dirname(args.input)

  # Filtering cases where there're more than 1 CT, AS and Marker list.
  multi_loc_rep = report.groupby(['Terminal AS/ID', 'Terminal CT/ID']).filter(lambda x: len(x)>1)
  multi_loc_rep.to_csv(f"{dir_path}/multi_loc_report.tsv", sep="\t", index=False)

  # Same CT and AS with different Marker list
  cell_loc_diff_markers = multi_loc_rep.drop_duplicates(['Terminal AS/ID','Terminal CT/ID','Markers']).sort_values(['Terminal AS/ID','Terminal CT/ID']).groupby(['Terminal AS/ID','Terminal CT/ID']).filter(lambda x: len(x)>1)
  cell_loc_diff_markers.to_csv(f"{dir_path}/cell-loc-diff-markers.tsv", sep="\t", index=False)
  
  # Filtering the rows from cell_loc_diff_marks
#   clean_report = multi_loc_rep[(multi_loc_rep['Terminal AS/ID'].isin(cell_loc_diff_markers['Terminal AS/ID']) == False) & (multi_loc_rep['Terminal CT/ID'].isin(cell_loc_diff_markers['Terminal CT/ID']) == False)].drop_duplicates(['Terminal AS/ID','Terminal CT/ID'])
  clean_report = cell_loc_diff_markers[~cell_loc_diff_markers.isin(multi_loc_rep)].dropna()
  clean_report.to_csv('clean_report.tsv', sep='\t', index=False)

                    # leukocyte    myeloid cell
  parent_classes = ["CL:0000738", "CL:0000763"]
  ct_list = list(clean_report["Terminal CT/ID"].drop_duplicates())
  combine = list(product(ct_list, parent_classes))

  terms_pairs = transform_to_str(combine)

  valid_subclass, not_valid_subclass = ug.verify_relationship(terms_pairs=terms_pairs, relationship=ug.select_subclass)

  terms_ct_i, _ = split_terms(transform_to_str(valid_subclass))
  ccf_input_temp = clean_report.loc[clean_report["Terminal CT/ID"].isin(terms_ct_i)]
  
  ccf_template = create_template(ccf_input_temp, "located in")
  ccf_template.to_csv(args.output, sep='\t', index=False)

  terms_ct_ni, _ = split_terms(not_valid_subclass)
  terms_ct = set(terms_ct_ni) - set(terms_ct_i)
  cl_input_temp = clean_report.loc[clean_report["Terminal CT/ID"].isin(terms_ct)][["Terminal AS/ID", "Terminal CT/ID", "References"]].drop_duplicates()

  cl_template = create_dosdp_template(cl_input_temp)
  cl_template.to_csv('../templates/cellPartOfAnatomicalEntity.tsv', sep='\t', index=False)

def generate(args):
  report = get_ct_loc_marker(args.input)

  if report is not None:
    report.to_csv(args.output, sep='\t', index=False)


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('-i', '--input', help='input json file')
  parser.add_argument('-o', '--output', help='output csv file')
  parser.add_argument('-m', '--mode', help='three modes to deal with report: generate, merge or template')

  args = parser.parse_args()
  if args.mode == 'generate':
    generate(args)
  elif args.mode == 'merge':
    merge_csv(args.output)
  elif args.mode == 'template':
    template(args)