def get_names(city):
    '''
    获取开始urls
    :param city:
    :return:
    '''
    with open('data/%s.txt' % city, 'r') as f:
        for line in f.readlines():
            name = line.strip()
            yield name



if __name__ == '__main__':
    t = get_names('newyork')
    t = list(t)
    print(t)
