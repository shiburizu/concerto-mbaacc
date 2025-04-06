# convert csv to json or vice versa for localization effort

import sys, json, csv

if ".json" in sys.argv[1]:
    with open('strings.csv', 'w', encoding='utf-8', newline='') as out:
        locjson = json.load(open(sys.argv[1],encoding='utf-8'))
        langkeys = ['Key']
        rows = []
        for i in locjson.items():
            new_row = {
                'Key' : i[0]
            }
            for l in list(i[1].keys()):
                
                new_row[l] = i[1][l]

                if l not in langkeys:
                    langkeys.append(l)
            rows.append(new_row)
        langkeys.append('Notes')
        writer = csv.DictWriter(out, fieldnames=langkeys)
        writer.writeheader()
        writer.writerows(rows)
elif ".csv" in sys.argv[1]:
    with open(sys.argv[1], encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        locjson = {}
        for row in reader:
            locjson[row['Key']] = {}
            new_key = locjson[row['Key']]
            for i in list(row.keys()):
                if i != 'Key' and i != 'Notes' and row[i] != '':
                    new_key[i] = row[i]
        print(locjson)
        with open("strings.json", "w") as outfile:
            outfile.write(json.dumps(locjson, indent=4))