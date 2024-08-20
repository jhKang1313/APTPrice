import requests as requests

totalRegion = '0000000000'
region_list_url = 'https://new.land.naver.com/api/regions/list?cortarNo={0}'
dong_list_url = 'https://new.land.naver.com/api/complexes/single-markers/2.0'

latDegree = 0.0073249
lonDegree = 0.0180244
default_condition = {
  'cortarNo': '1156011700',
  'zoom': 16,
  'priceType': 'RETAIL',
  'markerId' : '',
  'markerType' : '',
  'selectedComplexNo' : '',
  'selectedComplexBuildingNo' : '',
  'fakeComplexMarker' : '',
  'realEstateType' : 'APT',
  'tradeType' : 'A1',
  'rentPriceMin': 0,
  'rentPriceMax': 900000000,
  'priceMin': 0,
  'priceMax': 120000,
  'areaMin': 66,
  'areaMax': 115,
  'oldBuildYears' : 15,
  'recentlyBuildYears' : '',
  'minHouseHoldCount': 198,
  'maxHouseHoldCount' : '',
  'showArticle' : False,
  'sameAddressGroup' : True,
  'minMaintenanceCost' : '',
  'maxMaintenanceCost' : '',
  'directions' : '',
  'leftLon': 126.8884756,
  'rightLon': 126.9245244,
  'topLat': 37.5420249,
  'bottomLat': 37.5273744,
  'isPresale': False
}

def makeApiUrl(url, param):
  url = url + "?"
  for key in param.keys():
    url += key + "=" + str(param.get(key)) + "&"
  return url[:-1]

print(makeApiUrl(dong_list_url, default_condition))

header = {
  "Accept" : "*/*",
  "Accept-Encoding" : "gzip, deflate, br",
  "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
}

response = requests.get(region_list_url.format(totalRegion), headers = header)
sidoList = response.json()['regionList']

focusSidoList = {
  '1100000000': '서울',
  '4100000000': '경기'
}

# 시, 도
for sidoItem in sidoList:
  if sidoItem['cortarNo'] in list(focusSidoList.keys()):
    response = requests.get(region_list_url.format(sidoItem['cortarNo']), headers = header)
    guList = response.json()['regionList']

    # 구
    for guItem in guList:
      if guItem['cortarNo'] in ['1156000000']: # 영등포구
        response = requests.get(region_list_url.format(guItem['cortarNo']), headers=header)

        dongList = response.json()['regionList']
        # 동 탐색
        for dongItem in dongList:
          newParam = default_condition
          newParam['cortarNo'] = dongItem.get('cortarNo')
          newParam['leftLon'] = dongItem.get('centerLon') - lonDegree
          newParam['rightLon'] = dongItem.get('centerLon') + lonDegree
          newParam['topLat'] = dongItem.get('centerLat') + latDegree
          newParam['bottomLat'] = dongItem.get('centerLat') - latDegree

          response = requests.get(makeApiUrl(dong_list_url, newParam), headers=header)

