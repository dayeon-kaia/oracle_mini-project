from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 모듈 로드
from src.predictor import Predictor
from src.shap_explainer import ShapExplainer

app = Flask(__name__)
CORS(app)

# 모델 로드 (서버 시작 시 1회)
print("\n=== ML Service 초기화 ===")
predictor = Predictor(model_dir='models', version='v1')
shap_explainer = ShapExplainer(predictor)
print("=== 초기화 완료 ===\n")


@app.route('/health', methods=['GET'])
def health():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': list(predictor.models.keys()),
        'n_features': len(predictor.feature_cols)
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    단일 환자 예측
    
    Request Body:
    {
        "patient_id": "P-1024",
        "features": {
            "hr": 92, "rr": 18, "spo2": 96, ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({'error': 'features 필드 필요'}), 400
        
        patient_id = data.get('patient_id', 'unknown')
        features = data['features']
        
        # 예측
        result = predictor.predict(features)
        
        # SHAP (composite 모델 기준)
        shap_top5 = shap_explainer.get_top_features(features, 'composite', top_n=5)
        
        return jsonify({
            'patient_id': patient_id,
            'predictions': result['predictions'],
            'risk_levels': result['risk_levels'],
            'shap_top5': shap_top5
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    배치 예측
    
    Request Body:
    {
        "patients": [
            {"patient_id": "P-1024", "features": {...}},
            {"patient_id": "P-1025", "features": {...}}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'patients' not in data:
            return jsonify({'error': 'patients 필드 필요'}), 400
        
        results = []
        for patient in data['patients']:
            patient_id = patient.get('patient_id', 'unknown')
            features = patient.get('features', {})
            
            result = predictor.predict(features)
            shap_top5 = shap_explainer.get_top_features(features, 'composite', top_n=5)
            
            results.append({
                'patient_id': patient_id,
                'predictions': result['predictions'],
                'risk_levels': result['risk_levels'],
                'shap_top5': shap_top5
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/features', methods=['GET'])
def get_features():
    """필요한 피처 목록 반환"""
    return jsonify({
        'feature_cols': predictor.feature_cols,
        'n_features': len(predictor.feature_cols)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)