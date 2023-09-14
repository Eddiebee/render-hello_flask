import requests

import os

import time
import csv

from utils.get_leads_list  import  get_leads_list


def get_leads(label_id: str):
    url = "https://api.apollo.io/v1/contacts/search"

    data = {
        "api_key": os.environ["LABEL_API_KEY"],
        "page": 1,
        "per_page": 100,
        "contact_label_ids": [label_id],
    }

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }

    contacts_list = []

    response = requests.request("POST", url, headers=headers, json=data)
    total_pages = response.json()["pagination"]["total_pages"]

    for i in range(total_pages):
        data = {
            "api_key": os.environ["LABEL_API_KEY"],
            "page": i+1,
            "per_page": 100,
            "contact_label_ids": [label_id],
        }

        response = requests.request("POST", url, headers=headers, json=data)

        contacts = response.json()["contacts"]

        for contact in contacts:
            name = contact.get("name")
            title = contact.get("title")
            email = contact.get("email")
            company = contact.get("organization_name")
            company_id = contact.get("organization_id")
            if contact.get("organization"):
                company_website = contact.get("organization")["website_url"]

            contacts_list.append({"Name": name,
                                  "Title": title,
                                  "Email": email,
                                  "Company": company,
                                  "Company Id": company_id,
                                  "Company website": company_website, })

    # generate filters for just organizations that our contacts belong to
    # q_org = ""
    # for contact in contacts_list:
    #     q_org += (contact["Company"] + "\n")

    # # generate prospective leads
    # leads_list = []

    # people_url = "https://api.apollo.io/v1/mixed_people/search"

    # for i in range(100):
    #     data = {
    #         "api_key": os.environ["LABEL_API_KEY"],
    #         "page": i+1,
    #         "per_page": 100,
    #         "q_organization_domains ": q_org
    #     }

    #     response = requests.request(
    #         "POST", people_url, headers=headers, json=data)
    #     lead_contacts = response.json()["people"]

    #     for lead_contact in lead_contacts:
    #         if lead_contact.get("organization"):
    #             organization_id = lead_contact.get("organization_id")
    #             organization_title = lead_contact.get("organization")["name"]
    #             lead_name = lead_contact.get("name")
    #             lead_title = lead_contact.get("title")

    #         leads_list.append({"organization_id": organization_id,
    #                            "organization_title":  organization_title,
    #                            "lead_name":  lead_name,
    #                            "lead_title": lead_title})

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

    # leads_list = get_leads_list()

    # connect contacts to leads
    contacts_with_leads = []
    choice_leads = []

    for i, contact in enumerate(contacts_list):
        for lead in leads_list:
            if lead.get("lead_name") != contact.get("Name") and lead.get("organization_id") == contact.get("Company Id"):
                choice_leads.append({i: lead})

    for choice_lead in choice_leads:
        for choice_lead_key, choice_lead_value in choice_lead.items():
            contacts_with_leads.append({"Name": contacts_list[choice_lead_key].get("Name"),
                                        "Title": contacts_list[choice_lead_key].get("Title"),
                                        "Email": contacts_list[choice_lead_key].get("Email"),
                                        "Company": contacts_list[choice_lead_key].get("Company"),
                                        "Company Website": contacts_list[choice_lead_key].get("Company website"),
                                        "Leads' Name": choice_lead_value["lead_name"],
                                        "Leads' Title": choice_lead_value["lead_title"]})

    # write files to csv
    ts = time.time()
    filename = f"/tmp/{ts}.csv"

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Title', "Email",
                      "Company name", "Company website", "Leads' name",  "Leads' title"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        rows = [{"Name": contact_with_leads["Name"], "Title": contact_with_leads["Title"],
                "Email": contact_with_leads["Email"], "Company name": contact_with_leads["Company"],
                 "Company website": contact_with_leads["Company Website"],
                 "Leads' name": contact_with_leads["Leads' Name"],
                 "Leads' title": contact_with_leads["Leads' Title"]} for contact_with_leads in contacts_with_leads]

        for row in rows:
            writer.writerow(row)

    return response.json(), filename
