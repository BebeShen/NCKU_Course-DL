import json
import requests
import time
from bs4 import BeautifulSoup
import requests

def layer2crawler(id):
    print(id)
    base_url = "https://www.wantgoo.com/index/"+"%5E"+str(id)+"/stocks"
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50'}
    r = requests.get(base_url, headers=agent)
    # print(r.content.decode('unicode-escape'))
    # contents = json.loads(r.content.decode('unicode-escape'))
    soup = BeautifulSoup(r.text, 'html.parser')
    cls = soup.find_all('tr')
    for c in cls:
        print(c)
    return "test"

def webCrawler():
    base_url = "https://www.wantgoo.com/index/all-industry-of-groups"
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50'}
    r = requests.get(base_url, headers=agent)
    # print(r.content.decode('unicode-escape'))
    contents = json.loads(r.content.decode('unicode-escape'))
    soup = BeautifulSoup(r.text, 'html.parser')
    data = dict()
    idListA = []
    idListB = []
    for c in contents:
        groupId:str = ""
        if len(str(c['id']))==2:
            groupId = "^0"+str(c['id'])
        else:
            groupId = "^"+str(c['id'])
        if c['groupName'] == '上市':
            idListA.append(groupId)
            # groupA.append({
            #     "id": groupId,
            #     "groupName": c['shortName'] 
            # })
        elif c['groupName'] == '上櫃':
            idListB.append(groupId)
            # groupB.append({
            #     "id": groupId ,
            #     "groupName": c['shortName']
            # })
    data['上市'] = idListA
    data['上櫃'] = idListB
    print(data['上市'])
    return data
    # print(layer2crawler(20))
    # print(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
    
def allalive(idList):
    base_url = "https://www.wantgoo.com/investrue/all-alive"
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50'}
    r = requests.get(base_url, headers=agent)
    # print(r.content.decode('unicode-escape'))
    contents = json.loads(r.content.decode('unicode-escape'))
    # print(contents[399:402])
    soup = BeautifulSoup(r.text, 'html.parser')
    data = []
    dictList = dict()
    searchDict = dict()
    for c in contents:
        searchDict[c['id']] = c['name']
        if len(c['industries']) < 1:
            continue
        for i in range(len(c['industries'])):
            if c['industries'][i]['id'] in idList["上市"]:
                # print(c['name'], c['id'])
                # print(c['industries'][i]['id'], c['industries'][i]['name'], c['industries'][i]['shortName'])
                if c['industries'][i]['name'] not in dictList.keys():
                    dictList[c['industries'][i]['name']] = []
                dictList[c['industries'][i]['name']].append({
                    "id":c['id'], 
                    "name":c['name']
                })
            if c['industries'][i]['id'] in idList["上櫃"]:
                if c['industries'][i]['name'] not in dictList.keys():
                    dictList[c['industries'][i]['name']] = []
                dictList[c['industries'][i]['name']].append({
                    "id":c['id'], 
                    "name":c['name']
                })
    return dictList, searchDict
    # print(dictList)
if __name__ == "__main__":
    data = webCrawler()
    outputData, searchList = allalive(data)
    print(len(outputData), outputData.keys())
    with open('stock.json', 'w', encoding='utf8') as outfile:
        json.dump(outputData, outfile, indent=4, ensure_ascii=False)
    with open('search.json', 'w', encoding='utf8') as out:
        json.dump(searchList, out, indent=4, ensure_ascii=False)
    # print(json.dumps(outputData, indent=4, sort_keys=True, ensure_ascii=False))  
