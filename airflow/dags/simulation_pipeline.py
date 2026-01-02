"""
============================================================
준실시간 시뮬레이션 파이프라인
============================================================

목적:
- MIMIC-IV 정적 데이터를 시간순으로 "재생"
- 실시간 모니터링처럼 보여주기

흐름:
1. 현재 시뮬레이션 시각 조회
2. 해당 시각까지의 환자 데이터 추출
3. ML 모델로 예측 실행
4. 예측 결과 저장
5. 시뮬레이션 시각 업데이트

TODO:
- [ ] Oracle DB 연결 설정
- [ ] 시뮬레이션 시각 관리 로직
- [ ] ML 모델 호출 연동
- [ ] 시뮬레이션 속도 설정 (1:1 or 1:60)
============================================================
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# ============================================================
# DAG 기본 설정
# ============================================================
default_args = {
    'owner': 'team4',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ============================================================
# DAG 정의
# ============================================================
with DAG(
    dag_id='simulation_pipeline',
    default_args=default_args,
    description='MIMIC-IV 준실시간 시뮬레이션 파이프라인',
    # schedule_interval='*/10 * * * *',  # 10분마다 (활성화 시)
    schedule_interval=None,  # 수동 실행 (테스트용)
    catchup=False,
    tags=['simulation', 'mimic-iv', 'team4'],
) as dag:

    # ========================================================
    # Task 1: 시작
    # ========================================================
    start = EmptyOperator(task_id='start')

    # ========================================================
    # Task 2: 시뮬레이션 시각 조회
    # ========================================================
    def get_simulation_time(**context):
        """
        현재 시뮬레이션 시각 조회
        
        TODO:
        - DB 또는 파일에서 현재 시뮬레이션 시각 읽기
        - 없으면 ICU 입실 시각(intime)으로 초기화
        """
        print("🕐 시뮬레이션 시각 조회 중...")
        
        # TODO: 실제 구현
        # simulation_time = db.execute("SELECT current_sim_time FROM simulation_state")
        
        simulation_time = datetime(2024, 1, 1, 9, 0, 0)  # 임시값
        print(f"✅ 현재 시뮬레이션 시각: {simulation_time}")
        
        # 다음 Task로 전달
        context['ti'].xcom_push(key='simulation_time', value=str(simulation_time))

    get_sim_time = PythonOperator(
        task_id='get_simulation_time',
        python_callable=get_simulation_time,
    )

    # ========================================================
    # Task 3: 환자 데이터 추출
    # ========================================================
    def extract_patient_data(**context):
        """
        시뮬레이션 시각까지의 환자 데이터 추출
        
        TODO:
        - Oracle DB 연결
        - charttime <= simulation_time 조건으로 필터링
        - vitals, labs 데이터 추출
        
        쿼리 예시:
        SELECT subject_id, charttime, heart_rate, blood_pressure, spo2
        FROM vitals
        WHERE charttime <= :simulation_time
        """
        simulation_time = context['ti'].xcom_pull(key='simulation_time')
        print(f"📥 데이터 추출 중... (기준 시각: {simulation_time})")
        
        # TODO: 실제 구현
        # data = db.execute(query, {'simulation_time': simulation_time})
        
        print("✅ 데이터 추출 완료")

    extract_data = PythonOperator(
        task_id='extract_patient_data',
        python_callable=extract_patient_data,
    )

    # ========================================================
    # Task 4: ML 예측 실행
    # ========================================================
    def run_predictions(**context):
        """
        ML 모델로 예측 실행
        
        TODO:
        - Flask ML 서비스 호출 (POST /predict)
        - 또는 직접 모델 로드하여 예측
        
        예측 항목:
        - mortality: 24시간 내 사망 확률
        - vent_start: 12/24시간 내 인공호흡기 시작 확률
        - pressors_start: 12/24시간 내 승압제 시작 확률
        """
        print("🤖 ML 예측 실행 중...")
        
        # TODO: 실제 구현
        # response = requests.post('http://ml-service:5000/predict', json=data)
        # predictions = response.json()
        
        print("✅ 예측 완료")

    run_ml = PythonOperator(
        task_id='run_predictions',
        python_callable=run_predictions,
    )

    # ========================================================
    # Task 5: 예측 결과 저장
    # ========================================================
    def save_predictions(**context):
        """
        예측 결과 DB에 저장
        
        TODO:
        - predictions 테이블에 INSERT
        - 대시보드에서 이 테이블 조회하여 표시
        
        저장 항목:
        - patient_id, simulation_time
        - mortality, vent_start, pressors_start
        - shap_top5 (JSON)
        """
        print("💾 예측 결과 저장 중...")
        
        # TODO: 실제 구현
        # db.execute("INSERT INTO predictions ...")
        
        print("✅ 저장 완료")

    save_results = PythonOperator(
        task_id='save_predictions',
        python_callable=save_predictions,
    )

    # ========================================================
    # Task 6: 시뮬레이션 시각 업데이트
    # ========================================================
    def advance_simulation_time(**context):
        """
        시뮬레이션 시각 1시간 전진
        
        TODO:
        - 현재 시각 + 1시간으로 업데이트
        - DB 또는 파일에 저장
        
        설정 가능:
        - 1시간씩 전진 (기본)
        - 6시간씩 전진 (빠른 데모용)
        """
        print("⏩ 시뮬레이션 시각 업데이트 중...")
        
        # TODO: 실제 구현
        # db.execute("UPDATE simulation_state SET current_sim_time = current_sim_time + INTERVAL '1 hour'")
        
        print("✅ 시뮬레이션 1시간 전진")

    advance_time = PythonOperator(
        task_id='advance_simulation_time',
        python_callable=advance_simulation_time,
    )

    # ========================================================
    # Task 7: 종료
    # ========================================================
    end = EmptyOperator(task_id='end')

    # ========================================================
    # Task 순서 정의
    # ========================================================
    start >> get_sim_time >> extract_data >> run_ml >> save_results >> advance_time >> end