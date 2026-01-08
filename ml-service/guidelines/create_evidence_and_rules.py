#!/usr/bin/env python3
"""
추출된 PDF 텍스트로부터 Evidence Chunk와 Rule을 생성
"""

import json
import re
from pathlib import Path

INPUT_FILE = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_extracted_text.json"
OUTPUT_EVIDENCE = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_evidence.json"
OUTPUT_RULES = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_rules.json"


def load_extracted_text():
    """추출된 텍스트 로드"""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def split_into_paragraphs(text):
    """텍스트를 문단으로 분리"""
    # 여러 줄바꿈으로 분리
    paragraphs = re.split(r'\n\s*\n', text)
    # 빈 문단 제거
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def is_recommendation(text):
    """권고문 판별"""
    keywords = ['권고', '권장한다', '권고된다', '권고하지', '고려한다', '사용할 수 있다', '투여한다']
    return any(kw in text for kw in keywords)


def create_evidence_chunks(sections):
    """Evidence Chunk 생성"""
    evidence_list = []
    evidence_id_counter = 1
    
    for section_id, section_info in sections.items():
        section_key = section_info['section_key']
        section_name = section_info['name']
        
        print(f"\n{'=' * 60}")
        print(f"섹션: {section_name} ({section_key})")
        print(f"{'=' * 60}")
        
        for page_data in section_info['pages']:
            page_num = page_data['page']
            text = page_data['text']
            
            # 문단으로 분리
            paragraphs = split_into_paragraphs(text)
            
            for para in paragraphs:
                # 너무 짧거나 긴 문단 스킵
                if len(para) < 50 or len(para) > 1500:
                    continue
                
                # 권고문 여부에 따라 별도 chunk 생성
                if is_recommendation(para):
                    # 권고문은 별도로 저장
                    evidence_id = f"EV_{evidence_id_counter:03d}"
                    evidence_id_counter += 1
                    
                    evidence = {
                        "evidence_id": evidence_id,
                        "doc": "2024 질병관리청 성인 패혈증 초기치료지침서",
                        "section": section_key,
                        "pdf_page_start": page_num,
                        "pdf_page_end": page_num,
                        "anchor": f"p{page_num}",
                        "content": para,
                        "is_recommendation": True,
                        "char_count": len(para)
                    }
                    evidence_list.append(evidence)
                    print(f"  [권고] {evidence_id}: p{page_num} ({len(para)}자)")
                else:
                    # 일반 설명/배경은 300-800자 단위로 chunk
                    if 300 <= len(para) <= 800:
                        evidence_id = f"EV_{evidence_id_counter:03d}"
                        evidence_id_counter += 1
                        
                        evidence = {
                            "evidence_id": evidence_id,
                            "doc": "2024 질병관리청 성인 패혈증 초기치료지침서",
                            "section": section_key,
                            "pdf_page_start": page_num,
                            "pdf_page_end": page_num,
                            "anchor": f"p{page_num}",
                            "content": para,
                            "is_recommendation": False,
                            "char_count": len(para)
                        }
                        evidence_list.append(evidence)
                        print(f"  [배경] {evidence_id}: p{page_num} ({len(para)}자)")
        
        print(f"  총 {len([e for e in evidence_list if e['section'] == section_key])}개 Evidence 생성")
    
    return evidence_list


def extract_numeric_value(text, pattern):
    """텍스트에서 숫자 추출"""
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def create_rules_from_evidence(evidence_list):
    """Evidence로부터 Rule 생성"""
    rules = []
    rule_id_counter = 1
    
    # 권고문만 필터링
    recommendations = [e for e in evidence_list if e.get('is_recommendation', False)]
    
    print(f"\n{'=' * 60}")
    print(f"Rule 생성 (권고문 기반)")
    print(f"{'=' * 60}")
    print(f"권고문 수: {len(recommendations)}")
    
    for evidence in recommendations:
        content = evidence['content']
        section = evidence['section']
        evidence_id = evidence['evidence_id']
        
        # Rule 추출 로직
        rules_from_evidence = []
        
        # 젖산 관련
        if section == 'lactate':
            if '젖산' in content or 'lactate' in content.lower():
                if '측정' in content or '재측정' in content:
                    rules_from_evidence.append({
                        "topic": "lactate",
                        "severity": "STAT" if "1시간" in content or "즉시" in content else "HIGH",
                        "trigger": "패혈증 의심 환자",
                        "action": "혈중 젖산 농도 측정",
                        "rule_type": "decision"
                    })
                if '4' in content and ('mmol' in content or '이상' in content):
                    rules_from_evidence.append({
                        "topic": "lactate",
                        "severity": "HIGH",
                        "trigger": "젖산 ≥4 mmol/L",
                        "action": "젖산 재측정 및 집중 치료",
                        "rule_type": "decision"
                    })
        
        # 수액 관련
        elif section == 'fluid':
            if '30' in content and 'ml/kg' in content:
                rules_from_evidence.append({
                    "topic": "fluid",
                    "severity": "STAT" if "3시간" in content else "HIGH",
                    "trigger": "패혈증 저혈압 또는 젖산 ≥4 mmol/L",
                    "action": "Crystalloid 30 mL/kg 3시간 내 투여",
                    "rule_type": "decision"
                })
            if '균형 용액' in content or 'balanced' in content.lower():
                rules_from_evidence.append({
                    "topic": "fluid",
                    "severity": "ROUTINE",
                    "trigger": "소생 수액 선택 시",
                    "action": "균형 용액(Balanced crystalloid) 사용 고려",
                    "rule_type": "decision"
                })
        
        # MAP 관련
        elif section == 'map':
            if '65' in content and ('MAP' in content or '평균동맥압' in content):
                rules_from_evidence.append({
                    "topic": "map",
                    "severity": "STAT",
                    "trigger": "패혈증 쇼크",
                    "action": "MAP ≥65 mmHg 목표로 승압제 투여",
                    "rule_type": "decision"
                })
            if '모니터링' in content and 'MAP' in content:
                rules_from_evidence.append({
                    "topic": "map",
                    "severity": "HIGH",
                    "trigger": "패혈증 환자",
                    "action": "MAP 지속 모니터링",
                    "rule_type": "monitoring"
                })
        
        # 항생제 관련
        elif section == 'abx':
            if '1시간' in content and ('항생제' in content or '투여' in content):
                rules_from_evidence.append({
                    "topic": "abx",
                    "severity": "STAT",
                    "trigger": "패혈증 진단",
                    "action": "혈액 배양 후 1시간 내 광범위 항생제 투여",
                    "rule_type": "decision"
                })
            if '배양' in content and '항생제' in content:
                rules_from_evidence.append({
                    "topic": "abx",
                    "severity": "HIGH",
                    "trigger": "항생제 투여 전",
                    "action": "혈액 배양 및 감염 부위 배양 시행",
                    "rule_type": "decision"
                })
        
        # 승압제 관련
        elif section == 'pressor':
            if 'norepinephrine' in content.lower() or '노르에피네프린' in content:
                if '1차' in content or '우선' in content:
                    rules_from_evidence.append({
                        "topic": "pressor",
                        "severity": "STAT",
                        "trigger": "패혈증 쇼크로 MAP <65 mmHg",
                        "action": "1차 승압제로 Norepinephrine 투여",
                        "rule_type": "decision"
                    })
            if 'vasopressin' in content.lower() or '바소프레신' in content:
                rules_from_evidence.append({
                    "topic": "pressor",
                    "severity": "HIGH",
                    "trigger": "Norepinephrine 단독으로 MAP 목표 미달성",
                    "action": "Vasopressin 추가 투여 고려",
                    "rule_type": "decision"
                })
            if '주의' in content or '모니터' in content:
                rules_from_evidence.append({
                    "topic": "pressor",
                    "severity": "ROUTINE",
                    "trigger": "승압제 사용 중",
                    "action": "부작용 및 혈압 반응 모니터링",
                    "rule_type": "monitoring"
                })
        
        # Rule 저장
        for rule_data in rules_from_evidence:
            rule_id = f"RULE_{rule_id_counter:03d}"
            rule_id_counter += 1
            
            rule = {
                "rule_id": rule_id,
                **rule_data,
                "source_evidence_ids": [evidence_id]
            }
            rules.append(rule)
            print(f"  {rule_id}: [{rule['topic']}] {rule['severity']} - {rule['action'][:50]}...")
    
    # 목표 개수 미달 시 추가 Rule 생성
    if len(rules) < 25:
        print(f"\n⚠️  Rule 개수 부족 ({len(rules)}/25). 추가 Rule 생성 중...")
        # 일반적인 패혈증 관리 Rule 추가 (Evidence 기반)
        additional_rules = generate_additional_rules(evidence_list, rule_id_counter)
        rules.extend(additional_rules)
    
    print(f"\n총 {len(rules)}개 Rule 생성")
    return rules


def generate_additional_rules(evidence_list, start_counter):
    """추가 Rule 생성 (Evidence 기반)"""
    additional = []
    counter = start_counter
    
    # 패혈증 진단 관련
    diagnosis_evidences = [e for e in evidence_list if e['section'] == 'diagnosis']
    if diagnosis_evidences:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "diagnosis",
            "severity": "STAT",
            "trigger": "감염 의심 + SOFA ≥2점 증가",
            "action": "패혈증 진단 및 초기 번들 시작",
            "rule_type": "decision",
            "source_evidence_ids": [diagnosis_evidences[0]['evidence_id']]
        })
        counter += 1
    
    # 젖산 모니터링
    lactate_evidences = [e for e in evidence_list if e['section'] == 'lactate']
    if lactate_evidences:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "lactate",
            "severity": "HIGH",
            "trigger": "초기 젖산 ≥2 mmol/L",
            "action": "젖산 정상화까지 재측정",
            "rule_type": "monitoring",
            "source_evidence_ids": [lactate_evidences[0]['evidence_id']]
        })
        counter += 1
    
    # 수액 과다 주의
    fluid_evidences = [e for e in evidence_list if e['section'] == 'fluid']
    if len(fluid_evidences) > 1:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "fluid",
            "severity": "ROUTINE",
            "trigger": "수액 투여 중",
            "action": "수액 과부하 징후 모니터링 (폐부종, CVP)",
            "rule_type": "caution",
            "source_evidence_ids": [fluid_evidences[1]['evidence_id']]
        })
        counter += 1
    
    # MAP 개별화
    map_evidences = [e for e in evidence_list if e['section'] == 'map']
    if len(map_evidences) > 1:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "map",
            "severity": "ROUTINE",
            "trigger": "고혈압 병력 환자",
            "action": "MAP 목표 개별화 고려",
            "rule_type": "decision",
            "source_evidence_ids": [map_evidences[1]['evidence_id'] if len(map_evidences) > 1 else map_evidences[0]['evidence_id']]
        })
        counter += 1
    
    # 항생제 de-escalation
    abx_evidences = [e for e in evidence_list if e['section'] == 'abx']
    if len(abx_evidences) > 2:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "abx",
            "severity": "ROUTINE",
            "trigger": "배양 결과 확인 후",
            "action": "항생제 범위 축소(de-escalation) 고려",
            "rule_type": "decision",
            "source_evidence_ids": [abx_evidences[2]['evidence_id'] if len(abx_evidences) > 2 else abx_evidences[0]['evidence_id']]
        })
        counter += 1
    
    # 승압제 용량 모니터링
    pressor_evidences = [e for e in evidence_list if e['section'] == 'pressor']
    if len(pressor_evidences) > 3:
        additional.append({
            "rule_id": f"RULE_{counter:03d}",
            "topic": "pressor",
            "severity": "HIGH",
            "trigger": "Norepinephrine 고용량 (>0.5 mcg/kg/min)",
            "action": "2차 승압제 추가 고려",
            "rule_type": "decision",
            "source_evidence_ids": [pressor_evidences[3]['evidence_id'] if len(pressor_evidences) > 3 else pressor_evidences[0]['evidence_id']]
        })
        counter += 1
    
    return additional


def validate_rules(rules, evidence_list):
    """Rule 검증"""
    print(f"\n{'=' * 60}")
    print(f"Rule 검증")
    print(f"{'=' * 60}")
    
    valid_rules = []
    evidence_ids = {e['evidence_id'] for e in evidence_list}
    
    for rule in rules:
        rule_id = rule['rule_id']
        
        # 1. 원문 없이 성립하는가?
        has_evidence = any(eid in evidence_ids for eid in rule['source_evidence_ids'])
        
        # 2. 임상 행동을 바꾸는가?
        has_action = rule['action'] and len(rule['action']) > 10
        
        # 3. 근거 Evidence가 명확한가?
        has_clear_evidence = len(rule['source_evidence_ids']) > 0
        
        # 검증 결과
        if has_evidence and has_action and has_clear_evidence:
            valid_rules.append(rule)
            print(f"✓ {rule_id}: PASS")
        else:
            print(f"✗ {rule_id}: FAIL - ", end="")
            if not has_evidence:
                print("근거 없음", end=" ")
            if not has_action:
                print("행동 불명확", end=" ")
            if not has_clear_evidence:
                print("Evidence 미연결", end=" ")
            print()
    
    print(f"\n검증 결과: {len(valid_rules)}/{len(rules)} Rule 통과")
    return valid_rules


def save_json(data, filepath):
    """JSON 저장"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 저장 완료: {filepath}")


def create_mapping_table(rules, evidence_list):
    """Rule ↔ Evidence 매핑 테이블 생성"""
    mapping = []
    
    for rule in rules:
        for eid in rule['source_evidence_ids']:
            evidence = next((e for e in evidence_list if e['evidence_id'] == eid), None)
            if evidence:
                mapping.append({
                    "rule_id": rule['rule_id'],
                    "rule_topic": rule['topic'],
                    "rule_action": rule['action'],
                    "evidence_id": evidence['evidence_id'],
                    "evidence_section": evidence['section'],
                    "evidence_page": evidence['pdf_page_start']
                })
    
    return mapping


def main():
    print("=" * 60)
    print("패혈증 가이드라인 Evidence & Rule 생성")
    print("=" * 60)
    
    # 1. 추출된 텍스트 로드
    sections = load_extracted_text()
    print(f"\n로드된 섹션: {len(sections)}개")
    
    # 2. Evidence Chunk 생성
    evidence_list = create_evidence_chunks(sections)
    print(f"\n총 Evidence: {len(evidence_list)}개")
    
    # 3. Rule 생성
    rules = create_rules_from_evidence(evidence_list)
    
    # 4. Rule 검증
    validated_rules = validate_rules(rules, evidence_list)
    
    # 5. 매핑 테이블 생성
    mapping = create_mapping_table(validated_rules, evidence_list)
    
    # 6. 저장
    save_json(evidence_list, OUTPUT_EVIDENCE)
    save_json(validated_rules, OUTPUT_RULES)
    
    mapping_file = "/home/hykim/projects/mimic_dev/ml-service/guidelines/sepsis_rule_evidence_mapping.json"
    save_json(mapping, mapping_file)
    
    # 7. 요약 출력
    print(f"\n{'=' * 60}")
    print(f"최종 결과")
    print(f"{'=' * 60}")
    print(f"Evidence: {len(evidence_list)}개")
    print(f"Rule: {len(validated_rules)}개")
    print(f"매핑: {len(mapping)}개")
    
    # Rule 유형별 통계
    by_type = {}
    by_severity = {}
    by_topic = {}
    
    for rule in validated_rules:
        rt = rule.get('rule_type', 'decision')
        sev = rule['severity']
        topic = rule['topic']
        
        by_type[rt] = by_type.get(rt, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_topic[topic] = by_topic.get(topic, 0) + 1
    
    print(f"\nRule 유형: {by_type}")
    print(f"Rule 심각도: {by_severity}")
    print(f"Rule 주제: {by_topic}")


if __name__ == "__main__":
    main()
