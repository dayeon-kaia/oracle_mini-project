from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd
import io
import requests

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials():
    """
    Google Drive 인증 정보 가져오기
    - token.pickle이 있으면 재사용
    - 만료되었으면 자동 갱신
    - 없으면 최초 인증 진행
    """
    creds = None
    
    # 기존 토큰 로드
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 토큰 유효성 확인 및 갱신
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print("🔐 최초 인증이 필요합니다. 브라우저가 열립니다...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ 인증 완료!")
    
    return creds

def read_csv_from_drive(file_id, usecols=None):
    """
    Google Drive에서 CSV 파일을 메모리로 읽어 pandas DataFrame 반환
    (파일을 디스크에 저장하지 않음)
    
    Args:
        file_id (str): Google Drive 파일 ID
        usecols (list): 읽을 특정 컬럼 리스트 (선택사항)
    
    Returns:
        pandas.DataFrame: CSV 데이터
    """
    try:
        # 인증 정보 가져오기
        creds = get_credentials()
        
        # Google Drive API 호출
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        headers = {"Authorization": f"Bearer {creds.token}"}
        
        print(f"📖 파일 읽는 중... (메모리 로드, 저장 안함)")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # CSV를 메모리에서 직접 DataFrame으로 변환
            if usecols:
                df = pd.read_csv(io.StringIO(response.text), usecols=usecols)
            else:
                df = pd.read_csv(io.StringIO(response.text))
            
            print(f"✅ 조회 완료! 데이터 크기: {df.shape[0]:,}행 x {df.shape[1]}열")
            return df
        else:
            raise Exception(f"오류 {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        raise

def get_file_id_from_url(drive_url):
    """
    Google Drive 공유 링크에서 파일 ID 추출
    
    Args:
        drive_url (str): Google Drive 공유 링크
    
    Returns:
        str: 파일 ID
    """
    if "/file/d/" in drive_url:
        return drive_url.split("/file/d/")[1].split("/")[0]
    elif "id=" in drive_url:
        return drive_url.split("id=")[1].split("&")[0]
    else:
        return drive_url  # 이미 ID인 경우
