import shap
import numpy as np

class ShapExplainer:
    def __init__(self, predictor):
        self.predictor = predictor
        self.explainers = {}
        self._init_explainers()
    
    def _init_explainers(self):
        """SHAP TreeExplainer 초기화"""
        for name, model in self.predictor.models.items():
            try:
                self.explainers[name] = shap.TreeExplainer(model)
                print(f"  ✓ {name} SHAP explainer 초기화")
            except Exception as e:
                print(f"  ✗ {name} SHAP 초기화 실패: {e}")
    
    def get_top_features(self, features_dict, model_name='composite', top_n=5):
        """
        SHAP 기여도 상위 N개 피처 반환
        
        Parameters:
        -----------
        features_dict : dict
            35개 피처 딕셔너리
        model_name : str
            모델 이름 (death, vent, pressor, composite)
        top_n : int
            상위 N개
        
        Returns:
        --------
        list : [{'feature': 'lactate', 'contribution': 0.23}, ...]
        """
        if model_name not in self.explainers:
            return []
        
        try:
            # 피처 배열 생성
            X = np.array([[features_dict.get(col, 0) for col in self.predictor.feature_cols]])
            
            # SHAP 값 계산
            shap_values = self.explainers[model_name].shap_values(X)
            
            # XGBoost는 shap_values가 array일 수 있음
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # positive class
            
            shap_values = shap_values[0]  # 첫 번째 샘플
            
            # 절대값 기준 상위 N개
            indices = np.argsort(np.abs(shap_values))[::-1][:top_n]
            
            result = []
            for idx in indices:
                result.append({
                    'feature': self.predictor.feature_cols[idx],
                    'contribution': round(float(shap_values[idx]), 4)
                })
            
            return result
        
        except Exception as e:
            print(f"SHAP 계산 실패: {e}")
            return []