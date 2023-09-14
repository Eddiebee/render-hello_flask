import csv
import pprint


def get_leads_list():
    # we are using this new pattern to reduce query time and load time.
    leads_list = []
    with open('prospective_leads.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    # transform data to expected format
    data.pop(0)

    for d in data:
        # we have 5 columns
        leads_list.append({
            "organization_id": d[1],
            "organization_title": d[2],
            "lead_name": d[3],
            "lead_title":  d[4]
        })

    return leads_list
