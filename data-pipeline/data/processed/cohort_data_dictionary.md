
# MIMIC-IV ICU 코호트 데이터 딕셔너리

## 기본 정보
- subject_id: 환자 고유 ID
- hadm_id: 입원 ID
- stay_id: ICU 입실 ID (분석 단위)
- intime: ICU 입실 시간
- outtime: ICU 퇴실 시간
- los: ICU 체류 기간 (일)
- first_careunit: 첫 ICU 유형
- last_careunit: 마지막 ICU 유형

## 환자 특성
- anchor_age: 연령 (18세 이상)
- gender: 성별
- dod: 사망 날짜 (있는 경우)

## 입원 정보
- admittime: 병원 입원 시간
- dischtime: 병원 퇴원 시간
- deathtime: 사망 시간 (있는 경우)
- hospital_expire_flag: 병원 내 사망 여부 (0/1)

## 중재 시작 시점
- vent_start: 인공호흡기 시작 시간
- pressor_start: 승압제 시작 시간

## 예측 라벨 (예측 기간: ICU 입실 후 7-24시간)
- death_7_24h: 예측 기간 내 사망 (0/1)
- vent_start_7_24h: 예측 기간 내 인공호흡기 시작 (0/1)
- pressor_start_7_24h: 예측 기간 내 승압제 시작 (0/1)
- composite_outcome: 통합 라벨 - 위 3가지 중 하나라도 발생 (0/1)

## Outcome 변수
- icu_mortality: ICU 내 사망 (0/1) - Primary outcome
- hospital_mortality: 병원 내 사망 (0/1) - Secondary outcome

## 시간 윈도우
- 관찰 기간: ICU 입실 후 0-6시간 (feature 생성용)
- 리드 타임: 6-7시간 (안전 구간)
- 예측 기간: 7-24시간 (라벨 판단 구간)

## 포함/제외 기준
- 포함: 18세 이상, ICU 체류 24시간 이상, 첫 번째 입실
- 제외: DNR 환자(6시간 이내), 조기 이벤트(7시간 이내 사망/퇴원), 필수 활력징후 기록 없음
