"""
============================================================
Flask ML Service
============================================================

역할:
- 학습된 ML 모델 로드
- 환자 데이터 받아서 예측 실행
- SHAP 분석 결과 반환

엔드포인트:
- GET  /health          : 서버 상태 확인
- POST /predict         : 단일 환자 예측
- POST /predict/batch   : 다중 환자 예측

실행:
- 개발: python app.py
- 운영: gunicorn app:app

TODO:
- [ ] 실제 모델 파일 로드 (models/*.pkl)
- [ ] 전처리 로직 연동
- [ ] SHAP 분석 구현
============================================================
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# 서비스 모듈 (나중에 구현)
# from src.predictor import Predictor
# from src.shap_explainer import ShapExplainer

app = Flask(__name__)
CORS(app)

# ============================================================
# 설정
# ============================================================
MODEL_PATH = os.getenv('MODEL_PATH', 'models/')
PORT = int(os.getenv('ML_SERVICE_PORT', 5001))

# ============================================================
# GET /health - 서버 상태 확인
# ============================================================
@app.route('/health', methods=['GET'])
def health():
    """
    서버 상태 확인
    
    Response:
    {
        "status": "ok",
        "model_loaded": true,
        "timestamp": "2024-01-01T11:00:00Z"
    }
    """
    return jsonify({
        'status': 'ok',
        'model_loaded': False,  # TODO: 실제 모델 로드 상태
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


# ============================================================
# POST /predict - 단일 환자 예측
# ============================================================
@app.route('/predict', methods=['POST'])
def predict():
    """
    단일 환자 예측
    
    Request Body:
    {
        "patient_id": "P-1024",
        "features": {
            // Vitals (최근 6시간 통계) - 예상 포맷, 전처리 후 확정
            "heart_rate_mean": 92,
            "heart_rate_std": 12,
            "heart_rate_min": 78,
            "heart_rate_max": 115,
            
            "sbp_mean": 118,
            "dbp_mean": 75,
            "map_mean": 89,
            
            "resp_rate_mean": 18,
            "spo2_mean": 96,
            "temperature_mean": 37.2,
            
            // Labs (최근 값)
            "lactate": 2.1,
            "creatinine": 1.4,
            "bilirubin": 0.8,
            "platelet": 180,
            "wbc": 12.5,
            
            // 기타
            "age": 65,
            "los_hours": 48,
            "gcs_score": 14
        }
    }
    
    Response:
    {
        "patient_id": "P-1024",
        "predictions": {
            "mortality_24h": 0.75,
            "vent_start_12h": 0.45,
            "pressors_start_12h": 0.60
        },
        "shap_top5": [
            { "feature": "lactate", "contribution": 0.23 },
            { "feature": "map_mean", "contribution": 0.18 },
            ...
        ],
        "predicted_at": "2024-01-01T11:00:00Z"
    }
    """
    try:
        data = request.get_json()
        
        # 입력 검증
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        patient_id = data.get('patient_id')
        features = data.get('features')
        
        if not patient_id:
            return jsonify({'error': 'patient_id is required'}), 400
        
        if not features:
            return jsonify({'error': 'features is required'}), 400
        
        # ====================================================
        # TODO: 실제 예측 로직
        # ====================================================
        # predictor = Predictor(MODEL_PATH)
        # predictions = predictor.predict(features)
        # shap_values = ShapExplainer.explain(predictor.model, features)
        
        # Mock 응답 (실제 모델 연동 전까지)
        mock_response = {
            'patient_id': patient_id,
            'predictions': {
                'mortality_24h': 0.75,
                'vent_start_12h': 0.45,
                'pressors_start_12h': 0.60
            },
            'shap_top5': [
                {'feature': 'lactate', 'contribution': 0.23},
                {'feature': 'map_mean', 'contribution': 0.18},
                {'feature': 'heart_rate_std', 'contribution': 0.12},
                {'feature': 'spo2_mean', 'contribution': -0.09},
                {'feature': 'creatinine', 'contribution': 0.07}
            ],
            'predicted_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(mock_response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# POST /predict/batch - 다중 환자 예측
# ============================================================
@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    다중 환자 예측 (Airflow 배치 처리용)
    
    Request Body:
    {
        "patients": [
            { "patient_id": "P-1024", "features": { ... } },
            { "patient_id": "P-2156", "features": { ... } },
            ...
        ]
    }
    
    Response:
    {
        "results": [
            { "patient_id": "P-1024", "predictions": { ... }, "shap_top5": [...] },
            { "patient_id": "P-2156", "predictions": { ... }, "shap_top5": [...] },
            ...
        ],
        "processed_count": 2,
        "predicted_at": "2024-01-01T11:00:00Z"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'patients' not in data:
            return jsonify({'error': 'patients array is required'}), 400
        
        patients = data['patients']
        
        # ====================================================
        # TODO: 실제 배치 예측 로직
        # ====================================================
        
        # Mock 응답
        results = []
        for patient in patients:
            results.append({
                'patient_id': patient.get('patient_id'),
                'predictions': {
                    'mortality_24h': 0.75,
                    'vent_start_12h': 0.45,
                    'pressors_start_12h': 0.60
                },
                'shap_top5': [
                    {'feature': 'lactate', 'contribution': 0.23},
                    {'feature': 'map_mean', 'contribution': 0.18},
                    {'feature': 'heart_rate_std', 'contribution': 0.12},
                    {'feature': 'spo2_mean', 'contribution': -0.09},
                    {'feature': 'creatinine', 'contribution': 0.07}
                ]
            })
        
        return jsonify({
            'results': results,
            'processed_count': len(results),
            'predicted_at': datetime.utcnow().isoformat() + 'Z'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 서버 실행
# ============================================================
if __name__ == '__main__':
    print(f"🚀 ML Service 실행 중: http://localhost:{PORT}")
    print(f"📁 모델 경로: {MODEL_PATH}")
    print("=" * 50)
    print("엔드포인트:")
    print("  GET  /health        - 서버 상태 확인")
    print("  POST /predict       - 단일 환자 예측")
    print("  POST /predict/batch - 다중 환자 예측")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=PORT, debug=True)