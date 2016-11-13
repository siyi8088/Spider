__author__='siyi'

# -*- coding:utf-8 -*-

def getRegion():
    regions={
            'beijing':'bj',
            'shenghai':'sh',
            'shenzhen':'sz',
            'chengdu':'cd',
            'chongqing':'cq'
            }
    print('The availiable cities are\n',regions)
    print('Please input the abbreviation for the city you want to crawl. ')
    region=input()
    if region in regions.values():
        pass
    else:
        print('Sorry,you entered the wrong word.')
        region=None
    return region
