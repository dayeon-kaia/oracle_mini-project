
# MIMIC-IV ICU 코호트 데이터

## 파일 설명
- `cohort_final.csv`: 최종 코호트 테이블
- `cohort_data_dictionary.md`: 데이터 딕셔너리

## 사용 방법
```python
import pandas as pd

# 데이터 로드
df = pd.read_csv('cohort_final.csv')

# 기본 정보 확인
print(df.info())
print(df.describe())

# 라벨 분포 확인
print(df['composite_outcome'].value_counts())
```

## 데이터 생성 날짜
2026-01-05 03:24

## 문의사항
코호트 정의나 데이터 관련 문의사항은 팀 채널로 연락 주세요.
