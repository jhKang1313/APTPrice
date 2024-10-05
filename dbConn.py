import mysql.connector



class DBConnector:
  def __init__(self):
    self.conn  = mysql.connector.connect(
      host="jhkang1313.iptime.org",
      port="13306",
      user="root",
      password="qwer1234!",
      database="kang"
    )
    self.cursor = self.conn.cursor()
  def commit(self):
    self.conn.commit()
  def rollback(self):
    self.conn.rollback()

  def close(self):
    self.conn.close()

  def commitAndClose(self):
    self.commit()
    self.close()
  def exec(self, query, param):
    self.cursor.execute(query, param)

  def makeInsertQuery(self, table, colList, row):
    insertQuery = f"insert into {table} ("
    for col in colList:
      insertQuery += col + ", "

    insertQuery = insertQuery[: -2] + ") values ("
    for col in colList:
      insertQuery += "%s, "

    return insertQuery[: -2] + ")"

  def makeRowParam(self, colList, row):
    list = []
    for col in colList:
      list.append(row[1][col])
    return list

# 커서 객체 생성
# cursor = conn.cursor()
#
#
# for row in df_result.iterrows():
#   cursor.execute(makeInsertQuery("apt_table", colList, row), makeRowParam(colList,row))
#
# conn.commit()

# 데이터 조회
# cursor.execute("SELECT * FROM users")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

#conn.close()