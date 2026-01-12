import pickle
import json
import numpy as np
import os

class Predictor:
    def __init__(self, model_dir='models', version='v1'):
        self.model_dir = model_dir
        self.version = version
        self.models = {}
        self.feature_cols = []
        self.thresholds = {
            'death': 0.20,
            'vent': 0.30,
            'pressor': 0.20,
            'composite': 0.30
        }
        self._load_models()
        self._load_feature_cols()
    
    def _load_models(self):
        """pkl 모델 로드"""
        model_paths = {
            'death': f'{self.model_dir}/death.pkl',
            'vent': f'{self.model_dir}/vent.pkl',
            'pressor': f'{self.model_dir}/pressor.pkl',
            'composite': f'{self.model_dir}/composite.pkl'
        }
        
        for name, path in model_paths.items():
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    self.models[name] = pickle.load(f)
                print(f"  ✓ {name} 모델 로드: {path}")
            else:
                print(f"  ✗ {name} 모델 없음: {path}")
    
    def _load_feature_cols(self):
        """피처 목록 로드"""
        path = f'{self.model_dir}/feature_cols.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.feature_cols = json.load(f)
            print(f"  ✓ 피처 목록 로드: {len(self.feature_cols)}개")
        else:
            print(f"  ✗ feature_cols.json 없음")
    
    def _get_risk_level(self, prob, threshold):
        """확률 → 위험 등급"""
        if prob >= threshold * 1.5:
            return 'critical'
        elif prob >= threshold:
            return 'high'
        elif prob >= threshold * 0.5:
            return 'warning'
        else:
            return 'stable'
    
    def predict(self, features_dict):
        """
        단일 환자 예측
        
        Parameters:
        -----------
        features_dict : dict
            35개 피처 딕셔너리
        
        Returns:
        --------
        dict : predictions, risk_levels
        """
        # 피처 순서 맞추기
        try:
            X = np.array([[features_dict.get(col, 0) for col in self.feature_cols]])
        except Exception as e:
            return {'error': f'피처 변환 실패: {str(e)}'}
        
        predictions = {}
        risk_levels = {}
        
        for name, model in self.models.items():
            try:
                prob = model.predict_proba(X)[0, 1]
                predictions[name] = round(float(prob), 4)
                risk_levels[name] = self._get_risk_level(prob, self.thresholds[name])
            except Exception as e:
                predictions[name] = None
                risk_levels[name] = 'error'
        
        return {
            'predictions': predictions,
            'risk_levels': risk_levels
        }
    
    def predict_batch(self, features_list):
        """
        배치 예측
        
        Parameters:
        -----------
        features_list : list of dict
            여러 환자의 피처 리스트
        
        Returns:
        --------
        list : 각 환자별 예측 결과
        """
        results = []
        for features_dict in features_list:
            result = self.predict(features_dict)
            results.append(result)
        return results