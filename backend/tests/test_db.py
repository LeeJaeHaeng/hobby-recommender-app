import mysql.connector
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

def test_database_connection():
    """MySQL 데이터베이스 연결 테스트"""
    print("\n=== 데이터베이스 연결 테스트 ===\n")
    
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME', 'hobby_recommender'),
            user=os.getenv('DB_USER', 'hobby_user'),
            password=os.getenv('DB_PASSWORD', 'password123')
        )
        
        if connection.is_connected():
            print("✅ 데이터베이스 연결 성공!")
            
            # 커서 생성
            cursor = connection.cursor()
            
            # MySQL 버전 확인
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📦 MySQL 버전: {version[0]}")
            
            # 데이터베이스 이름 확인
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"🗄️  현재 데이터베이스: {db_name[0]}")
            
            # 테이블 목록 확인
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 현재 테이블 수: {len(tables)}")
            
            if len(tables) > 0:
                print("테이블 목록:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("아직 생성된 테이블이 없습니다.")
            
            cursor.close()
            print("\n✅ 데이터베이스가 정상적으로 작동합니다!")
            
    except mysql.connector.Error as error:
        print(f"❌ 데이터베이스 연결 실패!")
        print(f"오류 메시지: {error}")
        print("\n해결 방법:")
        print("1. MySQL 서버가 실행 중인지 확인하세요")
        print("2. .env 파일의 데이터베이스 정보가 올바른지 확인하세요")
        print("3. MySQL에서 데이터베이스와 사용자가 생성되었는지 확인하세요")
        
    except Exception as error:
        print(f"❌ 예상치 못한 오류 발생: {error}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    test_database_connection()