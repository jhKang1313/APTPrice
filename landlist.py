import requests as requests
from datetime import datetime as dt
import pandas as pd
import mysql.connector


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
  'areaMin': 90,
  'areaMax': 120,
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

focusGuList = {
  #'1156000000' : '영등포구'
}

hateList = {
  '100495' : '벽산베스트블루밍',
  '425' : '북가좌삼호'
}

nowDate = dt.strftime(dt.now(), '%Y%m%d_%H%M%S')
df_result = pd.DataFrame([])
# 시, 도
for sidoItem in sidoList:
  if sidoItem['cortarNo'] in list(focusSidoList.keys()):
    response = requests.get(region_list_url.format(sidoItem['cortarNo']), headers = header)
    guList = response.json()['regionList']

    # 구
    for guItem in guList:
      if (len(focusGuList) > 0 and guItem['cortarNo'] in focusGuList) or len(focusGuList) == 0 : # 영등포구
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

            if len(df_result) > 0 and aptItem['markerId'] in list(df_result["apt_id"]):
              continue

            newRow = {
              "proc_dt" : nowDate,
              "apt_id" : aptItem['markerId'],
              "local1_nm": sidoItem[NAME_FIELD],
              "local2_nm": guItem[NAME_FIELD],
              "local3_nm": dongItem[NAME_FIELD],
              "apt_nm" : aptItem['complexName'],
              "crt_dt" : aptItem['completionYearMonth'][:4] + '-' + aptItem['completionYearMonth'][4:],
              "reg_cnt" : aptItem['totalHouseholdCount'],
              "min_amt" : aptItem['minDealPrice'],
              "max_amt": aptItem['maxDealPrice'],
              "min_sqr_amt": aptItem['minDealUnitPrice'],
              "max_sqr_amt": aptItem['maxDealUnitPrice'],
              "min_space" : aptItem['minArea'],
              "max_space" : aptItem['maxArea'],
              "sale_cnt" : aptItem['dealCount'],
              "url_nm" : makeApiUrl(item_detail_url + aptItem['markerId'], detailParam)
            }

            df_result = pd.concat([df_result, pd.DataFrame([newRow])])

df_result = df_result.sort_values(by=['min_amt', 'crt_dt'], ascending=[True, False])
#df_result.to_excel(f"output/{nowDate}_excel_data.xlsx", index = False)



conn = mysql.connector.connect(
    host="jhkang1313.iptime.org",
    port="13306",
    user="root",
    password="qwer1234!",
    database="kang"
)

# 커서 객체 생성
cursor = conn.cursor()

def makeInsertQuery(table, colList, row):
  insertQuery = f"insert into {table} ("
  for col in colList:
    insertQuery += col + ", "

  insertQuery = insertQuery[: -2] + ") values ("
  for col in colList:
    insertQuery += "%s, "

  return insertQuery[: -2] + ")"

def makeRowParam(colList, row):
  list = []
  for col in colList:
    list.append(row[1][col])
  return list

colList = list(df_result.columns)

for row in df_result.iterrows():
  cursor.execute(makeInsertQuery("apt_table", colList, row), makeRowParam(colList,row))

conn.commit()

# 데이터 조회
# cursor.execute("SELECT * FROM users")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

conn.close()