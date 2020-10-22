from random import randint
import json


def createAccountNumber(ifsc):
    randomNumber = randint(9, 100)

    json_file = open("./models/tracker.json", "r")
    data = json.load(json_file)
    json_file.close()

    lastNumber = data["last"] + 1

    data["last"] = lastNumber

    json_file = open("./models/tracker.json", "w")
    json_file.seek(0)
    json.dump(data, json_file)
    json_file.close()

    accountNumber = f"{str(ifsc)}{str(randomNumber)}{str(lastNumber)}"

    return accountNumber


# print(createAccountNumber("SBIN001200"))
