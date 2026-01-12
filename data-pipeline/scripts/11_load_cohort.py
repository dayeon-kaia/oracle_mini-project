import pandas as pd
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 설정
# ============================================================
CSV_PATH = '../data/cohort_base.csv'  # 경로 맞게 수정

# Oracle 접속 정보 (.env에서)
DB_USER = os.getenv('ORACLE_USER')
DB_PASSWORD = os.getenv('ORACLE_PASSWORD')
DB_DSN = os.getenv('ORACLE_DSN')  # 예: host:port/service_name

# ============================================================
# CSV 로드
# ============================================================
print("CSV 로드 중...")
df = pd.read_csv(CSV_PATH)
print(f"  ✓ {len(df):,} rows 로드")

# 컬럼명 소문자로 (Oracle 호환)
df.columns = df.columns.str.lower()

# NaN → None 변환 (Oracle NULL)
df = df.where(pd.notnull(df), None)

# ============================================================
# Oracle 연결
# ============================================================
print("Oracle 연결 중...")
conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
cursor = conn.cursor()
print("  ✓ 연결 성공")

# ============================================================
# 데이터 적재
# ============================================================
print("데이터 적재 중...")

insert_sql = """
INSERT INTO cohort (
    stay_id, subject_id, hadm_id, intime, outtime, los,
    first_careunit, last_careunit, anchor_age, gender, dod,
    admittime, dischtime, deathtime, hospital_expire_flag,
    icu_mortality, hospital_mortality, dnr_time,
    vent_start_time, pressor_start_time
) VALUES (
    :stay_id, :subject_id, :hadm_id, 
    TO_TIMESTAMP(:intime, 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(:outtime, 'YYYY-MM-DD HH24:MI:SS'),
    :los, :first_careunit, :last_careunit, :anchor_age, :gender,
    TO_DATE(:dod, 'YYYY-MM-DD'),
    TO_TIMESTAMP(:admittime, 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(:dischtime, 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(:deathtime, 'YYYY-MM-DD HH24:MI:SS'),
    :hospital_expire_flag, :icu_mortality, :hospital_mortality,
    TO_TIMESTAMP(:dnr_time, 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(:vent_start_time, 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(:pressor_start_time, 'YYYY-MM-DD HH24:MI:SS')
)
"""

import time

def _fmt_hms(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

# 배치 insert
batch_size = 1000
total = len(df)

start_t = time.time()
last_t = start_t
last_done = 0

for i in range(0, total, batch_size):
    batch = df.iloc[i:i+batch_size].to_dict('records')
    cursor.executemany(insert_sql, batch)
    conn.commit()

    done = min(i + batch_size, total)
    pct = (done / total) * 100 if total else 100.0

    now = time.time()
    elapsed = now - start_t

    # 전체 평균 속도
    avg_rps = (done / elapsed) if elapsed > 0 else 0.0

    # 배치 구간 속도(최근 구간)
    dt = now - last_t
    drows = done - last_done
    inst_rps = (drows / dt) if dt > 0 else 0.0

    # ETA는 평균 속도로 계산(안정적)
    remaining_rows = total - done
    eta_sec = (remaining_rows / avg_rps) if avg_rps > 0 else 0.0

    print(
        f"\r  {done:,}/{total:,} ({pct:6.2f}%) | "
        f"avg {avg_rps:,.0f} rows/s | "
        f"inst {inst_rps:,.0f} rows/s | "
        f"elapsed {_fmt_hms(elapsed)} | "
        f"ETA {_fmt_hms(eta_sec)}",
        end="",
        flush=True
    )

    last_t = now
    last_done = done

print(f"\n✓ 총 {total:,} rows 적재 완료")

# ============================================================
# 정리
# ============================================================
cursor.close()
conn.close()
print("✓ 연결 종료")
