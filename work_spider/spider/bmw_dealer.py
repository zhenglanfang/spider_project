import json


def get_dealer():
    data = {}
    with open('beijing_bmw_dealer.json', 'r') as f:
        data['北京'] = json.loads(f.read())['responseBody']['outlets']

    with open('shanghai_bmw_dealer.json', 'r') as f:
        data['上海'] = json.loads(f.read())['responseBody']['outlets']

    result = []
    for key in data:
        for i in data[key]:
            item = {
                'name': i['nz'],
                'email': i['em'],
                'mobile': i['tel'],
                'lnb': i['lnb'],
                'ltb': i['ltb'],
                'address': i['az'].split(' ')[0],
                'link': i['ws'],
                'city': key
            }
            result.append(item)
    print(len(result))
    with open('bmw_dealer.json', 'w') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    get_dealer()


