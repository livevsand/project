import json

with open("personal_info.json", 'r') as file:
    user_info = json.load(file)
with open("alt_names.json", 'r') as file:
    tags = json.load(file)
masterdic = {}

if len(user_info['middle name']) == 0:
    user_info["name"] = user_info['first name'] + ' ' + user_info['last name']
else:
    user_info["name"] = user_info['first name'] + ' ' + user_info['middle name'] + ' ' + user_info['last name']
user_info["please provide more information"] = "see resume"
user_info["do you currently have any family members"] = 'no'
if user_info["u.s. citizen or legal permanent resident"] == 'yes':
    user_info["require sponsorship"] = 'no'
    user_info["authorized to work"] = 'yes'

for text in user_info:
    if text in tags:
        for j in tags[text]:
            masterdic[j] = user_info[text]
    else:
        masterdic[text] = user_info[text]

if user_info["u.s. citizen or legal permanent resident"] == 'yes':
    masterdic["what's your citizenship"] = "citizen"
    masterdic["which countries are you currently legally authorized to work in"] = "US"
if user_info["do you currently have any family members"] == 'no':
    masterdic["name of relative"] = ""
for i in user_info["language"].split('|'):
    masterdic['proficiency in ' + i] = "native"

for i in user_info["country"].lower().split('|'):
    if i in ["united states", "us"]:
        masterdic["phone country code"] = "united states (+1)"
        masterdic["extension"] = "1"
        break

with open("default_responses.json", 'r') as file:
    default = json.load(file)

masterdic = masterdic | default
with open("responses.json", 'w') as file:
    json.dump(masterdic, file, indent=2)
