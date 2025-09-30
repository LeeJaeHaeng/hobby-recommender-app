import mysql.connector

print("MySQL 연결 테스트 시작...")

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='hobby_recommender',
        user='hobby_user',
        password='password123'
    )
    
    print("✅ 연결 성공!")
    
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL 버전: {version[0]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ 오류: {e}")