import json


def organize():
    json_file = open("./models/bank.json", "r")
    banks = json.load(json_file)
    json_file.close()

    branchDetails = {}

    for _, value in banks.items():
        branchDetails.update({(value["name"].upper()): []})

    for key, value in banks.items():
        branchDetails[(value["name"].upper())].append({
            "id": key,
            "branchName": value["branch"]
        })

    json_file = open("./models/branch.json", "w")
    json_file.seek(0)
    json.dump(branchDetails, json_file)
    json_file.close()


# organize()
