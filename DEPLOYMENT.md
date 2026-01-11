# EDCC Dashboard 배포 가이드
## Oracle Cloud + Nginx (Port 2026)

---

## 1단계: React 앱 빌드

로컬에서 실행:

```bash
cd /home/hykim/projects/mimic/frontend-edcc
npm run build
```

빌드가 완료되면 `dist` 폴더가 생성됩니다.

---

## 2단계: 빌드 파일을 오라클 클라우드에 업로드

**Windows PowerShell에서 실행:**

```powershell
# SCP로 dist 폴더 전체 업로드
scp -i C:\Users\KDT_06\Downloads\ssh-key-2025-12-15.key -r /home/hykim/projects/mimic/frontend-edcc/dist ubuntu@168.107.4.22:/tmp/edcc-dist
```

---

## 3단계: 서버에 접속하여 설정

**SSH로 서버 접속:**

```bash
ssh -i C:\Users\KDT_06\Downloads\ssh-key-2025-12-15.key ubuntu@168.107.4.22
```

---

## 4단계: Nginx 설치 및 설정

서버에서 실행:

```bash
# Nginx 설치 (아직 없다면)
sudo apt update
sudo apt install nginx -y

# EDCC 디렉토리 생성 및 파일 이동
sudo mkdir -p /var/www/edcc
sudo mv /tmp/edcc-dist/* /var/www/edcc/
sudo chown -R www-data:www-data /var/www/edcc
sudo chmod -R 755 /var/www/edcc

# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/edcc
```

**Nginx 설정 내용** (`/etc/nginx/sites-available/edcc`):

```nginx
server {
    listen 2026;
    listen [::]:2026;

    server_name 168.107.4.22;

    root /var/www/edcc;
    index index.html;

    # Gzip 압축 활성화
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 정적 파일 캐싱
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 프록시 (Flask 백엔드로 연결)
    location /api/ {
        proxy_pass http://localhost:5003/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Protocol endpoint 프록시
    location /protocol {
        proxy_pass http://localhost:5003/protocol;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**설정 활성화:**

```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/edcc /etc/nginx/sites-enabled/

# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 5단계: 오라클 클라우드 방화벽 설정

### 5-1. iptables 설정

서버에서 실행:

```bash
# 포트 2026 허용
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 2026 -j ACCEPT

# 설정 저장 (Ubuntu)
sudo netfilter-persistent save

# 또는 iptables-persistent 설치 후 저장
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

### 5-2. Oracle Cloud Security List 설정

**Oracle Cloud Console에서:**

1. **Networking** → **Virtual Cloud Networks** 접속
2. 해당 VCN 선택
3. **Security Lists** → 사용 중인 Security List 선택
4. **Add Ingress Rules** 클릭
5. 다음 정보 입력:
   - **Source CIDR**: `0.0.0.0/0` (모든 IP 허용)
   - **IP Protocol**: `TCP`
   - **Source Port Range**: `All`
   - **Destination Port Range**: `2026`
   - **Description**: `EDCC Dashboard`
6. **Add Ingress Rules** 클릭

---

## 6단계: 접속 확인

브라우저에서:

```
http://168.107.4.22:2026
```

---

## 추가: Flask 백엔드 연동 설정

React 앱에서 Flask API를 호출하려면, API URL을 설정해야 합니다.

**방법 1: 환경 변수 사용 (권장)**

`frontend-edcc/.env.production` 파일 생성:

```env
VITE_API_URL=http://168.107.4.22:2026
```

**방법 2: 상대 경로 사용**

Nginx 프록시 설정 덕분에 `/api/`로 시작하는 요청은 자동으로 Flask로 전달됩니다.

예:
```javascript
// 절대 경로 대신
fetch('http://168.107.4.22:5003/api/patients')

// 상대 경로 사용
fetch('/api/patients')
```

---

## 트러블슈팅

### 1. Nginx 시작 실패

```bash
# Nginx 상태 확인
sudo systemctl status nginx

# 에러 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 2. 포트가 열리지 않음

```bash
# 현재 열린 포트 확인
sudo netstat -tlnp | grep 2026

# iptables 규칙 확인
sudo iptables -L -n -v | grep 2026
```

### 3. 파일 권한 에러

```bash
# 권한 재설정
sudo chown -R www-data:www-data /var/www/edcc
sudo chmod -R 755 /var/www/edcc
```

---

## 업데이트 방법

새로운 버전 배포 시:

```bash
# 1. 로컬에서 빌드
cd /home/hykim/projects/mimic/frontend-edcc
npm run build

# 2. 업로드
scp -i C:\Users\KDT_06\Downloads\ssh-key-2025-12-15.key -r dist/* ubuntu@168.107.4.22:/tmp/edcc-update/

# 3. 서버에서 교체
ssh -i C:\Users\KDT_06\Downloads\ssh-key-2025-12-15.key ubuntu@168.107.4.22
sudo rm -rf /var/www/edcc/*
sudo mv /tmp/edcc-update/* /var/www/edcc/
sudo chown -R www-data:www-data /var/www/edcc
```

---

## 완료!

배포가 완료되면:
- 대시보드: `http://168.107.4.22:2026`
- Flask API: `http://168.107.4.22:5003` (백엔드)
