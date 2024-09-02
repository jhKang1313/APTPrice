import requests as requests
from datetime import datetime as dt
import pandas as pd


NAME_FIELD = "cortarName"
totalRegion = '0000000000'
region_list_url = 'https://new.land.naver.com/api/regions/list?cortarNo={0}'
dong_list_url = 'https://new.land.naver.com/api/complexes/single-markers/2.0'
item_detail_url = 'https://new.land.naver.com/complexes/'




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
  'oldBuildYears' : 30,
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
  '1100000000': '서울'
  #,'4100000000': '경기'
}



df_result = pd.DataFrame([])
# 시, 도
for sidoItem in sidoList:
  if sidoItem['cortarNo'] in list(focusSidoList.keys()):
    response = requests.get(region_list_url.format(sidoItem['cortarNo']), headers = header)
    guList = response.json()['regionList']

    # 구
    for guItem in guList:

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

        aptList = response.json()

        print(f"{dongItem.get('cortarName')} : {len(aptList)}")

        for aptItem in aptList:
          detailParam = {
            "ms" : f"{dongItem.get('centerLat')}, {dongItem.get('centerLon')}, 16",
            "a" : "APT:ABYG: JGC:PRE",
            "b" : "A1",
            "e" : "RETAIL",
            "g" : "130000", # 최대12업
            "h" : "66",     # 최소면적
            "i" : "115",    # 최대면적
            "j" : "30",     # 연식
            "l" : "100",    # 세대수
            "ad" : "true"
          }

          newRow = {
            "id" : aptItem['markerId'],
            "시도": sidoItem[NAME_FIELD],
            "구": guItem[NAME_FIELD],
            "동": dongItem[NAME_FIELD],
            "APT명" : aptItem['complexName'],
            "준공일" : aptItem['completionYearMonth'][:4] + '-' + aptItem['completionYearMonth'][4:],
            "세대수" : aptItem['totalHouseholdCount'],
            "최저가" : aptItem['minDealPrice'],
            "최대가": aptItem['maxDealPrice'],
            "최소평당가": aptItem['minDealUnitPrice'],
            "최대평당가": aptItem['maxDealUnitPrice'],
            "최소면적" : aptItem['minArea'] + '㎡',
            "최대면적" : aptItem['maxArea'] + '㎡',
            "매물수" : aptItem['dealCount'],
            "URL" : makeApiUrl(item_detail_url + aptItem['markerId'], detailParam)
          }
          df_result = pd.concat([df_result, pd.DataFrame([newRow])])


# numberField = ['최저가', '최대가', '최소평당가', '최대평당가', '세대수']
# for field in numberField:
#   df_result[field] = df_result[field].apply(lambda x: "{:,}".format(x))

df_result = df_result.sort_values(by=['최저가', '준공일'], ascending=[True, False])

nowDate = dt.strftime(dt.now(), '%Y%m%d_%H%M%S')
df_result.to_excel(f"output/{nowDate}_excel_data.xlsx", index = False)
