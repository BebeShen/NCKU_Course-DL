import stock as stock
import json

response = stock.getStock(2303, period='D')

# print(response)
# print(json.dumps(response, indent=4, sort_keys=True))
with open("out.json", 'w', encoding='utf8') as f:
    json.dump(response, f, indent=4, sort_keys=False, ensure_ascii=False)