from ttp import ttp
import json

data = "example-config.txt"
template = "show_run.ttp"

parser = ttp(data, template)
parser.parse()
result = parser.result()

print(json.dumps(result, sort_keys=True, indent=4))

with open('example-result.json', 'w') as outfile:
    json.dump(result, outfile, sort_keys=True, indent=4)