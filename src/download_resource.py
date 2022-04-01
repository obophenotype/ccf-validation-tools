import argparse, requests, json, datetime
from urllib.parse import quote_plus

SHEET_ID = "1tK916JyG5ZSXW_cXfsyZnzXfjyoN-8B2GXLbYD6_vF0"

JOB_SHEET_GID_MAPPING = {
    'Bone-Marrow': '1845311048', # Bone Marrow_v1.1
    'Brain': '1379088218', # Brain_v1.1
    'Blood': '1315753355', # Blood_v1.1
    'Eye': '1593659227', # Eye_v1.0
    'Fallopian_tube': '1417514103', # Fallopian_Tube_v1.0
    'Heart': '2133445058', # Heart_v1.1
    'Kidney': '2137043090', # Kidney_v1.1
    'Knee': '1572314003', # Knee_v1.0
    'Large_intestine': '512613979', # Large_Intestine_v1.1
    'Liver': '2079993346', # Liver_v1.0
    'Lung': '1824552484', # Lung_v1.1
    'Lymph_node': '1440276882', # Lymph_Node_v1.1
    'Lymph_vasculature': '598065183', # Lymph_Vasculature_v1.0
    'Ovary': '1072160013', # Ovary_v1.0
    'Pancreas': '1044871154', # Pancreas_v1.0
    'Peripheral_nervous_system': '887132317', # Peripheral_Nervous_System_v1.0
    'Prostate': '1921589208', # Prostate_v1.0
    'Skin': '1158675184', # Skin_v1.1
    'Small_intestine': '1247909220', # Small_Intestine_v1.0
    'Spleen': '984946629', # Sleen_v1.1
    'Thymus': '1823527529', # Thymus_v1.1
    'Ureter': '1106564583', # Ureter_v1.0
    'Urinary_bladder': '498800030', # Urinary_Bladder_v1.0
    'Uterus': '877379009', # Uterus_v1.0
    'Blood_vasculature': '361657182' # Blood_Vasculature_v1.1
}

def main(args):
  API_URL = f'https://asctb-api.herokuapp.com/v2/{SHEET_ID}/{JOB_SHEET_GID_MAPPING[args.job]}'

  data = requests.get(API_URL).text
  data = json.loads(data)

  try:
    table_date = datetime.datetime.strptime(data["parsed"][6][1], '%m/%d/%Y').strftime('%Y-%m-%d')
    table_version = data["parsed"][7][1]
  except:
    table_date = datetime.datetime.strptime(data["parsed"][7][1], '%m/%d/%Y').strftime('%Y-%m-%d')
    table_version = data["parsed"][8][1]
    
  with open('tables_version.txt', 'a+', encoding='utf-8') as t:
    t.write(args.job + "," + table_version + "," + table_date + "\n")

  with open(args.output_file, 'w', encoding='utf-8') as f:
    json.dump(data['data'], f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('job', help='job to download')
  parser.add_argument('output_file', help='output file path')

  args = parser.parse_args()
  main(args)