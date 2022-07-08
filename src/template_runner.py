from datetime import date
from template_generation_tools import generate_class_graph_template, generate_vasculature_template
from ccf_tools import parse_asctb
import argparse
import os
import pandas as pd
print(os.getcwd())
parser = argparse.ArgumentParser()
parser.add_argument('--test', help='Run in test mode.',
                    action="store_true")  # Not doing anything with this yet.
parser.add_argument("job", help="job name")
parser.add_argument("target_file", help='input file path')
parser.add_argument("output_file", help='output file path')
parser.add_argument("old_version", help="is old version")
parser.add_argument("parse_asctb", help="need to parse ASCT+b table")

TODAY = date.today().strftime("%Y%m%d")
args = parser.parse_args()

if eval(args.parse_asctb):
  ccf_tools_df, report_t, new_terms_report = parse_asctb(args.target_file)
else:
  ccf_tools_df = pd.read_csv(args.target_file)

class_template, no_valid_template, error_log, annotations, indirect_error_log, report_r, strict_log, has_part_log, ub_subs_t, cl_subs_t, image_report, sec_graph = generate_class_graph_template(ccf_tools_df)

class_template.to_csv(args.output_file, sep=',', index=False)

annotations.serialize(f'../owl/{args.job}_annotations.owl', format='xml')

if args.job == 'Blood_vasculature':
  vasculature_template = generate_vasculature_template(ccf_tools_df)
  vasculature_template.to_csv(f'../templates/vasculature_class.tsv', sep='\t', index=False)

if not eval(args.old_version):
  # report_t['Table'] = args.job
  # report_t = pd.DataFrame.from_dict(report_t)
  # report_t_path = f"../reports/report_terms_{TODAY}.tsv"

  # new_terms_report.to_csv(f'../logs/new_cl_terms_{args.job}.tsv', sep='\t', index=False)

  # report_r['Table'] = args.job
  # report_r = pd.DataFrame.from_dict(report_r)
  # report_r_path = f"../reports/report_relationship_{TODAY}.tsv"

  no_valid_template.to_csv(f'../templates/{args.job}_no-valid.csv', sep=',', index=False)

  error_log.to_csv(f'../logs/class_{args.job}_log.tsv', sep='\t', index=False)

  sec_graph.serialize(f'../owl/{args.job}_sec.owl', format='xml')

  indirect_error_log.to_csv(f'../logs/class_{args.job}_indirect_log.tsv', sep='\t', index=False)

  strict_log.to_csv(f'../logs/{args.job}_AS_CT_strict_log.tsv', sep='\t', index=False)

  has_part_log.to_csv(f'../logs/{args.job}_AS_has_part_CT_log.tsv', sep='\t', index=False)

  ub_subs_t.to_csv(f'../templates/temp_ub_{args.job}_ASCTB_subset.csv', sep=',', index=False)

  cl_subs_t.to_csv(f'../templates/temp_cl_{args.job}_ASCTB_subset.csv', sep=',', index=False)

  image_report.to_csv(f'../logs/report_images_{args.job}.tsv', sep='\t', index=False)

  # if os.path.isfile(report_t_path):
  #   report_t.to_csv(report_t_path, sep='\t', index=False, mode='a', header=False)
  # else:
  #   report_t.to_csv(report_t_path, sep='\t', index=False)

  # if os.path.isfile(report_r_path):
  #   report_r.to_csv(report_r_path, sep='\t', index=False, mode='a', header=False)
  # else:
  #   report_r.to_csv(report_r_path, sep='\t', index=False)
      

                       


