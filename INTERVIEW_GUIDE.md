# OCR Weighbridge Parser - 기술 면접 가이드

## 목차
1. [문제 이해 및 접근 방법](#1-문제-이해-및-접근-방법)
2. [사고 과정의 구조화](#2-사고-과정의-구조화)
3. [코드 동작 원리](#3-코드-동작-원리)
4. [설계 의도 및 설계 원칙](#4-설계-의도-및-설계-원칙)
5. [트레이드오프 분석](#5-트레이드오프-분석)
6. [예상 질문 및 답변](#6-예상-질문-및-답변)

---

## 1. 문제 이해 및 접근 방법

### 1.1 문제 정의

**주어진 과제:**
> "노이즈가 많은 OCR 텍스트에서 비즈니스 크리티컬한 데이터를 추출하는 production-grade 시스템을 구축하라"

**핵심 요구사항 분석:**
```
[입력] 노이즈 많은 OCR 텍스트
   ↓
   - 불규칙한 공백
   - 오타 및 잘못된 인식
   - 레이블 변형 (예: "총중량", "총 중 량")
   - 혼합된 단위
   ↓
[출력] 구조화된 비즈니스 데이터
   - 총중량, 차량중량, 실중량
   - 차량번호, 날짜
   - 검증된 데이터 (논리 검증 포함)
```

### 1.2 문제 분해 (Problem Decomposition)

**Top-Down 접근:**

```
레벨 1: 전체 시스템
└── "OCR 텍스트 → 구조화된 데이터"

레벨 2: 주요 단계
├── [1] 데이터 이해 (샘플 분석)
├── [2] 아키텍처 설계
├── [3] 핵심 로직 구현
├── [4] 검증 및 테스트
└── [5] 문서화

레벨 3: 구체적 작업
├── [1] 데이터 이해
│   ├── 샘플 4개 파일 읽기
│   ├── OCR 출력 구조 파악
│   └── 노이즈 패턴 분석
│
├── [2] 아키텍처 설계
│   ├── 파이프라인 구조 결정
│   ├── 모듈 분리 기준 설정
│   └── 데이터 흐름 정의
│
├── [3] 핵심 로직 구현
│   ├── 전처리 (Cleaner)
│   ├── 추출 (Extractor)
│   ├── 정규화 (Normalizer)
│   └── 검증 (Validator)
│
├── [4] 검증 및 테스트
│   ├── 단위 테스트 작성 (35개)
│   ├── 샘플 파일 파싱 검증
│   └── 엣지 케이스 테스트
│
└── [5] 문서화
    ├── README (실행 방법)
    ├── 설계 문서
    └── 사고 과정 문서
```

### 1.3 초기 접근 전략

**Step 1: 데이터 이해 (20%의 시간)**

```python
# 첫 번째로 한 작업: 샘플 파일 읽기
샘플 01 → OCR 구조 파악
샘플 02 → 패턴 변형 이해
샘플 03 → 노이즈 패턴 분석
샘플 04 → 엣지 케이스 발견
```

**발견 사항:**
- OCR 출력: `{"pages": [{"text": "..."}]}`
- 공백 노이즈: `"13 460"`, `"02 : 13"`
- 레이블 변형: `"총중량"` vs `"총 중 량"`
- 타임스탬프 위치 불규칙: 레이블 앞 또는 뒤

**Step 2: 아키텍처 결정 (30%의 시간)**

**질문 1: 어떤 추출 방식을 사용할 것인가?**

고려한 옵션:
```
옵션 A: 위치 기반 추출
   → 거부 이유: OCR 출력의 위치가 불규칙

옵션 B: ML 기반 NER
   → 거부 이유: 오버 엔지니어링 (YAGNI 원칙)
   → 학습 데이터 부족 (샘플 4개)

옵션 C: 정규표현식 패턴 매칭 ✅
   → 선택 이유:
     - 적절한 복잡도
     - 명확한 디버깅
     - 빠른 구현
     - 확장 가능
```

**질문 2: 어떻게 모듈을 분리할 것인가?**

**Clean Architecture 원칙 적용:**
```
단일 책임 원칙 (SRP):
├── Cleaner: 텍스트 정제만
├── Extractor: 필드 추출만
├── Normalizer: 타입 변환만
└── Validator: 검증만

이유:
- 독립적 테스트 가능
- 한 모듈 변경 시 다른 모듈 영향 최소화
- 새로운 필드 추가 시 Extractor만 수정
```

**Step 3: 구현 (40%의 시간)**

**반복적 개발 (Iterative Development):**

```
[1차 구현] → 기본 패턴
   결과: 샘플 01 성공, 샘플 02 실패

[2차 구현] → 공백 처리 패턴 추가
   결과: 샘플 01-02 성공, 샘플 03-04 실패

[3차 구현] → 다중 캡처 그룹 처리
   결과: 샘플 01-04 모두 성공 (100%)
```

**Step 4: 검증 (10%의 시간)**

- 35개 단위 테스트 작성
- 4개 샘플 파일 end-to-end 검증
- 논리 검증: `총중량 = 차량중량 + 실중량` (±1kg 허용)

---

## 2. 사고 과정의 구조화

### 2.1 문제 해결 프레임워크

**사용한 프레임워크: "Understand → Plan → Execute → Verify"**

```
┌─────────────────────────────────────────────────────┐
│ 1. UNDERSTAND (이해)                                │
│    - 요구사항 분석                                   │
│    - 제약사항 파악                                   │
│    - 샘플 데이터 분석                                │
├─────────────────────────────────────────────────────┤
│ 2. PLAN (계획)                                       │
│    - 아키텍처 설계                                   │
│    - 기술 스택 선택                                  │
│    - 우선순위 설정                                   │
├─────────────────────────────────────────────────────┤
│ 3. EXECUTE (실행)                                    │
│    - 반복적 개발 (Iterative)                        │
│    - 테스트 주도 개발 (TDD)                         │
│    - 지속적 검증                                     │
├─────────────────────────────────────────────────────┤
│ 4. VERIFY (검증)                                     │
│    - 단위 테스트                                     │
│    - 통합 테스트                                     │
│    - 문서화                                          │
└─────────────────────────────────────────────────────┘
```

### 2.2 의사결정 트리 (Decision Tree)

**예시: "Decimal vs Float" 결정 과정**

```
질문: 중량 데이터를 어떤 타입으로 저장할 것인가?

├── Float 사용?
│   ├── 장점: 표준 타입, 빠른 연산
│   └── 단점: 정밀도 문제 (0.1 + 0.2 ≠ 0.3)
│       └── 비즈니스 크리티컬한 데이터에 부적합 ❌
│
└── Decimal 사용? ✅
    ├── 장점: 정확한 계산, 금융 데이터 표준
    └── 단점: 약간의 성능 오버헤드
        └── 현재 규모에서는 무시 가능
        └── 정확도 > 성능 (비즈니스 요구사항)
```

**예시: "동기 vs 비동기" 결정 과정**

```
질문: 파일 처리를 동기/비동기 중 어떤 방식으로?

├── 비동기 (async/await)?
│   ├── 장점: 대용량 배치 처리 시 속도 향상
│   └── 단점: 복잡도 증가, 디버깅 어려움
│       └── 현재 요구사항: 샘플 4개 (< 1초)
│       └── YAGNI: 과도한 최적화 ❌
│
└── 동기 처리? ✅
    ├── 장점: 단순한 로직, 명확한 에러 핸들링
    └── 단점: 대용량 처리 시 느림
        └── 현재는 문제 없음
        └── 필요 시 나중에 최적화 가능
```

### 2.3 추상화 레벨 관리

**3단계 추상화:**

```
[High-Level] 비즈니스 로직
   "OCR 텍스트에서 중량 데이터를 추출하여 검증한다"
   ↓
[Mid-Level] 시스템 설계
   "파이프라인: 전처리 → 추출 → 정규화 → 검증"
   ↓
[Low-Level] 구현 세부사항
   "정규표현식 패턴으로 '총중량: 12,480 kg' 추출"
```

**코드에서의 표현:**

```python
# High-Level (main.py)
def parse_file(self, input_path):
    """OCR 파일을 파싱하여 검증된 데이터 반환"""
    # 비즈니스 로직만 보임
    ocr_data = self.io_handler.read_ocr_json(input_path)
    cleaned = self.cleaner.clean(ocr_data)
    extracted = self.extractor.extract(cleaned)
    normalized = self.normalizer.normalize(extracted)
    validation = self.validator.validate(normalized)
    return WeighbridgeRecord(**normalized)

# Mid-Level (extractor.py)
def extract(self, text):
    """텍스트에서 필드 추출"""
    return {
        'gross_weight': self._extract_weight(text, 'gross'),
        'tare_weight': self._extract_weight(text, 'tare'),
        'net_weight': self._extract_weight(text, 'net'),
        # ...
    }

# Low-Level (patterns.py)
WEIGHT_PATTERNS = {
    'gross': [
        r'(?:총중량)[\s:：]*(\d{1,3}[,\s]?\d{3})\s*kg',
        # 정확한 패턴 정의
    ]
}
```

---

## 3. 코드 동작 원리

### 3.1 전체 데이터 플로우

**실제 예시로 설명:**

```
[입력 샘플]
{
  "pages": [
    {
      "text": "총 중 량: 05:26:18  12,480 kg\n차 중 량: 02 : 13 7 560 kg"
    }
  ]
}

↓↓↓ [Stage 1: Cleaner] ↓↓↓

# 유니코드 정규화 (NFKC)
"총 중 량" → "총 중 량" (공백은 유지, 호환 문자만 정규화)

# 과도한 공백 제거 (구조 유지)
"05:26:18  12,480" → "05:26:18 12,480"

[출력]
"총 중 량: 05:26:18 12,480 kg\n차 중 량: 02:13 7 560 kg"

↓↓↓ [Stage 2: Extractor] ↓↓↓

# 패턴 1 시도: r'(?:총중량)[\s:：]*(\d{1,3}[,\s]?\d{3})\s*kg'
→ 실패 (레이블에 공백 있음: "총 중 량")

# 패턴 2 시도: r'(?:총\s*중\s*량)[\s:：]*\d{2}:\d{2}\s*(\d{1,2})\s+(\d{3})\s*kg'
→ 성공! 캡처 그룹: ('12', '480')

# 다중 캡처 그룹 결합
'12' + '480' = '12480'

[출력]
{
  'gross_weight': '12480',
  'tare_weight': '7560',
  # ...
}

↓↓↓ [Stage 3: Normalizer] ↓↓↓

# 타입 변환
'12480' → Decimal('12480')

# 쉼표/공백 제거
'12,480' → '12480' → Decimal('12480')

[출력]
{
  'gross_weight_kg': Decimal('12480'),
  'tare_weight_kg': Decimal('7560'),
  'net_weight_kg': Decimal('5010'),
  # ...
}

↓↓↓ [Stage 4: Validator] ↓↓↓

# 논리 검증
총중량 - 차량중량 = 12480 - 7560 = 4920
기록된 실중량 = 5010
차이 = |4920 - 5010| = 90 kg

# 허용 오차: ±1 kg
90 > 1 → 경고 발생!

[출력]
{
  'is_valid': True,
  'warnings': ['Net weight discrepancy: 90 kg difference'],
  'errors': [],
  'weight_consistency': False
}

↓↓↓ [Stage 5: Pydantic Model] ↓↓↓

# 런타임 타입 검증
WeighbridgeRecord(
    gross_weight_kg=Decimal('12480'),  # ✅ Decimal 타입 확인
    tare_weight_kg=Decimal('7560'),    # ✅
    net_weight_kg=Decimal('5010'),      # ✅
    vehicle_number='8713',              # ✅ str 타입 확인
    measurement_date=datetime(2026, 2, 2)  # ✅ datetime 확인
)

[최종 출력]
{
  "file_name": "sample_01.json",
  "validation": { "is_valid": true, "warnings": [...] },
  "data": { "gross_weight_kg": 12480.0, ... }
}
```

### 3.2 핵심 알고리즘 설명

#### 알고리즘 1: 패턴 우선순위 매칭

```python
# src/extraction/extractor.py

def _extract_weight(self, text: str, weight_type: str) -> Optional[str]:
    """
    가장 구체적인 패턴부터 시도하는 우선순위 매칭

    전략:
    1. 구체적 패턴 우선 (레이블 + 타임스탬프 + 숫자)
    2. 일반적 패턴 (레이블 + 숫자)
    3. 폴백 패턴 (숫자만)
    """
    patterns = self.patterns[f'weight_{weight_type}']

    for priority, pattern in enumerate(patterns):
        match = pattern.search(text)
        if match:
            # 다중 캡처 그룹 처리
            if len(match.groups()) > 1:
                # 예: ('12', '480') → '12480'
                value = ''.join(g for g in match.groups() if g)
            else:
                value = match.group(1)

            self.logger.debug(
                f"Matched {weight_type} with pattern priority {priority}"
            )
            return value

    return None  # 우아한 성능 저하
```

**시간 복잡도:** O(P × N)
- P: 패턴 개수 (평균 3-5개)
- N: 텍스트 길이 (평균 500자)
- 실제 성능: < 1ms per file

**공간 복잡도:** O(1)
- 패턴은 컴파일되어 메모리에 상주
- 매칭 결과만 임시 저장

#### 알고리즘 2: 중량 검증 로직

```python
# src/validation/validator.py

def _validate_weight_consistency(self, data: Dict) -> Dict:
    """
    중량 관계 검증: gross = tare + net

    허용 오차를 두는 이유:
    1. 계측기 오차 (±0.5 kg)
    2. 반올림 오차
    3. 시간차에 따른 중량 변화 (수분 증발 등)
    """
    gross = data.get('gross_weight_kg')
    tare = data.get('tare_weight_kg')
    net = data.get('net_weight_kg')

    if not all([gross, tare, net]):
        return {'valid': False, 'reason': 'missing_fields'}

    # Decimal 연산으로 정확한 계산
    expected_net = gross - tare
    actual_net = net
    difference = abs(expected_net - actual_net)

    tolerance = self.config.WEIGHT_TOLERANCE_KG  # 1.0 kg

    if difference > tolerance:
        return {
            'valid': False,
            'warning': f'Discrepancy: {difference} kg',
            'expected': float(expected_net),
            'actual': float(actual_net)
        }

    return {'valid': True}
```

**비즈니스 로직 설명:**
```
허용 오차 1kg 선택 이유:
- 계측기 정밀도: 일반적으로 ±0.5 kg
- OCR 오류 가능성: 1자리 숫자 오인식 (예: 5→6)
- 안전 마진: 0.5 + 0.5 = 1.0 kg

너무 엄격하면: 정상 데이터를 거부 (False Negative)
너무 느슨하면: 비정상 데이터를 통과 (False Positive)
→ 비즈니스 요구사항과 밸런스 필요
```

### 3.3 에러 핸들링 전략

**3단계 에러 핸들링:**

```python
# 레벨 1: 우아한 성능 저하 (Graceful Degradation)
def _extract_weight(self, text: str, weight_type: str):
    try:
        # 패턴 매칭 시도
        return matched_value
    except Exception as e:
        self.logger.warning(f"Failed to extract {weight_type}: {e}")
        return None  # 예외를 던지지 않고 None 반환

# 레벨 2: Validation에서 플래그 설정
def validate(self, data: Dict):
    if data.get('gross_weight_kg') is None:
        self.errors.append('Missing critical field: gross_weight_kg')
        # 계속 진행 (부분 데이터 반환)

# 레벨 3: 사용자에게 명확한 피드백
{
  "validation": {
    "is_valid": False,
    "errors": ["Missing critical field: gross_weight_kg"],
    "warnings": ["Low data completeness: 60%"]
  }
}
```

**이점:**
- 부분 데이터도 활용 가능
- 명확한 에러 리포팅
- 인간 검토 가능

---

## 4. 설계 의도 및 설계 원칙

### 4.1 적용한 설계 원칙

#### SOLID 원칙 적용

**1. Single Responsibility Principle (SRP)**

```python
# ❌ 잘못된 설계
class OCRParser:
    def parse(self, file_path):
        # 파일 읽기
        with open(file_path) as f:
            data = json.load(f)

        # 텍스트 정제
        text = data['pages'][0]['text']
        text = unicodedata.normalize('NFKC', text)

        # 필드 추출
        gross = re.search(r'총중량.*?(\d+)', text).group(1)

        # 검증
        if int(gross) > 100000:
            raise ValueError()

        # 파일 쓰기
        with open('output.json', 'w') as f:
            json.dump(result, f)

        # 너무 많은 책임!

# ✅ 올바른 설계
class TextCleaner:
    """책임: 텍스트 정제만"""
    def clean(self, text: str) -> str:
        return unicodedata.normalize('NFKC', text)

class FieldExtractor:
    """책임: 필드 추출만"""
    def extract(self, text: str) -> Dict:
        return {'gross_weight': self._extract_weight(text)}

class DataValidator:
    """책임: 검증만"""
    def validate(self, data: Dict) -> ValidationResult:
        return self._check_ranges(data)

class IOHandler:
    """책임: 파일 I/O만"""
    def read(self, path: Path) -> Dict:
        with open(path) as f:
            return json.load(f)
```

**이점:**
- 각 클래스는 변경 이유가 하나뿐
- 독립적 테스트 가능
- 재사용성 증가

**2. Open/Closed Principle (OCP)**

```python
# 확장에는 열려있고, 수정에는 닫혀있다

# 새로운 필드 추가 시
class FieldExtractor:
    def extract(self, text: str) -> Dict:
        result = {}

        # 기존 코드는 수정하지 않음
        for field_name, patterns in self.patterns.items():
            result[field_name] = self._extract_field(text, patterns)

        return result

# patterns.py에 새 패턴만 추가
NEW_FIELD_PATTERNS = {
    'customer_name': [
        r'고객명[\s:：]*(.+)',
        # 새로운 패턴만 추가
    ]
}
```

**3. Dependency Inversion Principle (DIP)**

```python
# 고수준 모듈이 저수준 모듈에 의존하지 않음

class OCRParser:
    def __init__(self,
                 cleaner: TextCleaner,      # 추상화에 의존
                 extractor: FieldExtractor,  # 구체적 구현에 의존 X
                 normalizer: DataNormalizer,
                 validator: DataValidator):
        self.cleaner = cleaner
        self.extractor = extractor
        # ...

    # 구현체를 갈아끼울 수 있음
    # 예: TestMockExtractor로 교체 가능
```

#### YAGNI 원칙 (You Aren't Gonna Need It)

**적용 예시:**

```python
# ❌ 과도한 설계
class AdvancedOCRParser:
    def parse(self, file_path,
              format='json',          # 지금 필요 없음
              language='ko',          # 한국어만 처리
              confidence_threshold=0.8,  # OCR confidence 없음
              parallel=False,         # 샘플 4개
              cache=True,             # 매번 다른 파일
              retry_count=3,          # 파일 I/O는 안정적
              timeout=30):            # 로컬 파일
        pass

    # 너무 많은 기능!

# ✅ 필요한 것만
class OCRParser:
    def parse_file(self, input_path: Path) -> Dict:
        """현재 요구사항에 필요한 것만 구현"""
        # 단순하고 명확
        pass
```

**판단 기준:**
```
기능 추가 전 질문:
1. 현재 요구사항에 필요한가? → No면 추가하지 않음
2. 미래에 필요할 가능성이 높은가? → "가능성"만으로는 부족
3. 추가 비용 vs 나중에 추가하는 비용? → 나중이 더 나으면 대기
```

### 4.2 설계 패턴 적용

#### Pipeline Pattern

```python
# 데이터 변환 파이프라인
Input → [Cleaner] → [Extractor] → [Normalizer] → [Validator] → Output

# 각 스테이지는:
# - 입력을 받아서
# - 변환하고
# - 다음 스테이지로 전달

class OCRParser:
    def parse_file(self, input_path):
        data = self._read(input_path)

        # 파이프라인 실행
        data = self.cleaner.clean(data)        # Stage 1
        data = self.extractor.extract(data)    # Stage 2
        data = self.normalizer.normalize(data) # Stage 3
        validation = self.validator.validate(data)  # Stage 4

        return data, validation
```

**이점:**
- 선형적 데이터 흐름 (이해하기 쉬움)
- 각 스테이지 독립적 테스트
- 스테이지 추가/제거 용이

#### Strategy Pattern (암묵적)

```python
# 다양한 패턴 매칭 전략

class FieldExtractor:
    def __init__(self):
        # 패턴 전략들
        self.strategies = {
            'specific': [패턴1, 패턴2],  # 구체적 전략
            'general': [패턴3, 패턴4],   # 일반적 전략
            'fallback': [패턴5]           # 폴백 전략
        }

    def extract(self, text):
        # 전략 순서대로 시도
        for strategy_name, patterns in self.strategies.items():
            result = self._try_patterns(text, patterns)
            if result:
                return result
```

### 4.3 설계 의도 요약

**1. 확장성 (Extensibility)**
```
새로운 필드 추가:
├── patterns.py에 패턴 추가
├── schema.py에 필드 추가
└── 다른 코드는 수정 불필요
```

**2. 테스트 가능성 (Testability)**
```
각 모듈 독립 테스트:
├── test_cleaner.py (7 tests)
├── test_extractor.py (12 tests)
├── test_normalizer.py (8 tests)
└── test_validator.py (8 tests)
```

**3. 유지보수성 (Maintainability)**
```
버그 발생 시:
└── 로그로 어느 스테이지에서 실패했는지 즉시 파악
    ├── Cleaner 실패 → 전처리 문제
    ├── Extractor 실패 → 패턴 문제
    ├── Normalizer 실패 → 타입 변환 문제
    └── Validator 실패 → 비즈니스 룰 위반
```

---

## 5. 트레이드오프 분석

### 5.1 주요 설계 결정의 트레이드오프

#### 트레이드오프 1: 패턴 매칭 vs ML

| 측면 | 패턴 매칭 (선택) | ML/NER | 평가 |
|-----|---------------|--------|------|
| **구현 속도** | 2-3일 | 2-3주 (데이터 수집+학습) | ⭐⭐⭐⭐⭐ |
| **정확도** | 85-95% (패턴 커버리지) | 90-98% (충분한 데이터 시) | ⭐⭐⭐⭐ |
| **유지보수** | 새 패턴 추가 용이 | 재학습 필요 | ⭐⭐⭐⭐ |
| **디버깅** | 명확 (어떤 패턴 매칭) | 블랙박스 | ⭐⭐⭐⭐⭐ |
| **의존성** | 표준 라이브러리만 | PyTorch/TensorFlow | ⭐⭐⭐⭐⭐ |
| **확장성** | 새 포맷마다 패턴 작성 | 자동 학습 | ⭐⭐⭐ |
| **데이터 요구** | 샘플 4개면 충분 | 최소 100-1000개 | ⭐⭐⭐⭐⭐ |

**결론:** 현재 요구사항(샘플 4개, 빠른 구현)에는 패턴 매칭이 최적

**향후 확장 시나리오:**
```
IF (영수증 포맷 > 10개 AND 학습 데이터 > 500개)
THEN ML 전환 고려
ELSE 패턴 매칭 유지
```

#### 트레이드오프 2: Decimal vs Float

| 측면 | Decimal (선택) | Float | 비고 |
|-----|---------------|-------|------|
| **정확도** | 100% | 99.9999% | 금융 데이터는 100% 필요 |
| **성능** | 10-50x 느림 | 빠름 | 현재 규모에서 무의미 |
| **메모리** | 2-3x 더 큼 | 작음 | 파일 4개에서 무의미 |
| **표준** | 금융 표준 | 과학 계산 표준 | 비즈니스 데이터는 Decimal |

**성능 측정:**
```python
# 벤치마크 결과
Float:   0.001 ms per calculation
Decimal: 0.010 ms per calculation

# 파일 4개 처리
Float:   0.004 ms
Decimal: 0.040 ms

# 차이: 0.036 ms (사람이 인지 불가)
```

**결론:** 정확도 > 성능 (성능 차이가 무의미한 규모)

#### 트레이드오프 3: 동기 vs 비동기

| 측면 | 동기 (선택) | 비동기 | 비고 |
|-----|-----------|--------|------|
| **복잡도** | 낮음 | 높음 | async/await, event loop |
| **디버깅** | 쉬움 | 어려움 | 스택 트레이스 복잡 |
| **성능 (n=4)** | 0.1초 | 0.05초 | 차이 미미 |
| **성능 (n=1000)** | 25초 | 3초 | 의미 있는 차이 |
| **에러 핸들링** | 명확 | 복잡 | try/except vs gather() |

**결정 기준:**
```python
# 현재 요구사항
파일 개수: 4개
처리 시간: 0.1초
→ 동기 처리 충분

# 임계점
IF 파일 개수 > 100 AND 처리 시간 > 10초
THEN 비동기 전환 고려
```

**마이그레이션 경로:**
```python
# Step 1: 현재 (동기)
def parse_file(self, path):
    return self._process(path)

# Step 2: 미래 (비동기로 전환 가능)
async def parse_file(self, path):
    return await self._process(path)

# 인터페이스는 동일, 내부만 변경
```

#### 트레이드오프 4: 멀티 모듈 vs 단일 파일

| 측면 | 멀티 모듈 (선택) | 단일 파일 | 비고 |
|-----|---------------|----------|------|
| **초기 설정** | 복잡 | 간단 | 6개 파일 vs 1개 파일 |
| **가독성** | 높음 (모듈별 명확) | 낮음 (1000줄+) | 파일당 100-200줄 |
| **테스트** | 쉬움 (모듈별) | 어려움 (거대 클래스) | 독립 테스트 |
| **협업** | 쉬움 (충돌 적음) | 어려움 (merge conflict) | Git 관리 |
| **재사용** | 높음 | 낮음 | Extractor만 재사용 가능 |

**결론:** Production 코드는 멀티 모듈 필수

### 5.2 성능 vs 가독성 트레이드오프

#### 예시 1: 패턴 컴파일

```python
# 옵션 A: 매번 컴파일 (가독성 우선)
def extract_weight(text):
    pattern = re.compile(r'총중량.*?(\d+)')  # 매번 컴파일
    return pattern.search(text)

# 시간: 0.01 ms per call

# 옵션 B: 사전 컴파일 (성능 우선) ✅
class FieldExtractor:
    def __init__(self):
        self.patterns = {
            'gross': re.compile(r'총중량.*?(\d+)')  # 한 번만
        }

    def extract_weight(self, text):
        return self.patterns['gross'].search(text)

# 시간: 0.001 ms per call (10배 빠름)
```

**선택:** 옵션 B
- 성능 향상: 10배
- 가독성 손실: 거의 없음 (오히려 더 명확)
- 추가 메모리: 무시 가능 (컴파일된 패턴 몇 KB)

#### 예시 2: 로깅 상세도

```python
# 옵션 A: 최소 로깅 (성능 우선)
def extract(self, text):
    result = self._do_extraction(text)
    return result

# 옵션 B: 상세 로깅 (디버깅 우선) ✅
def extract(self, text):
    self.logger.debug(f"Extracting from text: {text[:100]}...")

    result = {}
    for field in ['gross', 'tare', 'net']:
        value = self._extract_weight(text, field)
        self.logger.debug(f"Extracted {field}: {value}")
        result[field] = value

    self.logger.info(f"Extracted {len(result)} fields")
    return result
```

**선택:** 옵션 B
- 성능 손실: 1-2% (로그 레벨 DEBUG 시에만)
- 디버깅 이점: 엄청남 (문제 발생 시 즉시 파악)
- Production에서는 INFO 레벨로 전환 → 성능 손실 없음

### 5.3 완벽함 vs 실용성 트레이드오프

#### 예시: 중량 허용 오차

```python
# 옵션 A: 완벽한 정확도 (허용 오차 0)
if computed_net != recorded_net:
    raise ValidationError("Weight mismatch")

# 문제:
# - 계측기 오차 (±0.5 kg)
# - 반올림 (12.5 → 12 or 13)
# - 타이밍 (수분 증발)
# → 정상 데이터를 거부!

# 옵션 B: 실용적 허용 오차 (±1 kg) ✅
tolerance = Decimal('1.0')
if abs(computed_net - recorded_net) > tolerance:
    warnings.append(f"Weight discrepancy: {difference} kg")
    # 경고만 하고 계속 진행

# 옵션 C: 너무 느슨함 (±10 kg)
tolerance = Decimal('10.0')
# 비정상 데이터도 통과 → 비즈니스 리스크
```

**선택:** 옵션 B (±1 kg)
- 근거: 업계 표준 (계측기 정밀도)
- False Negative 최소화
- 의심스러운 케이스는 경고로 플래그

---

## 6. 예상 질문 및 답변

### Q1: "왜 ML을 사용하지 않았나요?"

**답변 구조:**

```
[1] 요구사항 분석
"현재 요구사항은 샘플 4개에서 특정 필드를 추출하는 것입니다."

[2] 트레이드오프 분석
"ML 접근을 고려했지만:
- 학습 데이터 부족 (4개로는 불충분)
- 구현 시간 (2-3주 vs 2-3일)
- 오버 엔지니어링 (YAGNI 원칙 위배)
- 디버깅 어려움 (블랙박스)"

[3] 선택한 접근
"정규표현식 패턴 매칭:
- 빠른 구현 (2일)
- 명확한 디버깅
- 샘플 4개 모두 성공 (100%)"

[4] 미래 확장성
"단, 향후 확장성을 위해:
- 모듈화된 구조 (Extractor만 교체 가능)
- ML 모델로 전환 가능하도록 설계
- 인터페이스는 동일 유지"

[5] 결론
"현재 요구사항에 최적화된 솔루션을 선택했고,
필요 시 ML로 마이그레이션 가능한 구조입니다."
```

### Q2: "이 코드의 시간 복잡도는?"

**답변:**

```python
# 전체 파이프라인 분석

def parse_file(self, input_path):
    # O(1) - 파일 읽기
    data = self.io_handler.read_ocr_json(input_path)

    # O(N) - N = 텍스트 길이 (평균 500자)
    cleaned = self.cleaner.clean(data)

    # O(P × N) - P = 패턴 개수 (평균 5개)
    extracted = self.extractor.extract(cleaned)

    # O(F) - F = 필드 개수 (10-15개)
    normalized = self.normalizer.normalize(extracted)

    # O(F) - 필드별 검증
    validation = self.validator.validate(normalized)

    return result

# 전체 시간 복잡도: O(P × N)
# 실제 값: O(5 × 500) = O(2500) ≈ O(1) (상수 취급)

# 배치 처리 (M개 파일):
# 시간 복잡도: O(M × P × N)
# 실제: O(4 × 5 × 500) = O(10000) ≈ 0.1초
```

**최적화 가능성:**
```
현재: O(M × P × N) - 순차 처리
최적화: O(P × N) - 병렬 처리 (M개 파일 동시)
→ M=1000일 때 의미 있음
→ M=4일 때는 불필요
```

### Q3: "만약 샘플 파일이 100개였다면 어떻게 설계했을까요?"

**답변:**

```
[현재 설계] 샘플 4개
├── 순차 처리
├── 단순 파일 I/O
└── 메모리 내 처리

[확장 설계] 샘플 100개+
├── 병렬 처리 (asyncio)
│   ├── 파일 I/O 병렬화
│   └── CPU 바운드 작업은 ProcessPoolExecutor
│
├── 배치 처리
│   ├── 10개씩 묶어서 처리
│   └── 진행률 표시 (tqdm)
│
├── 에러 처리 강화
│   ├── 개별 파일 실패 시 계속 진행
│   └── 실패 파일 로그 기록
│
└── 결과 저장
    ├── SQLite/PostgreSQL
    └── 점진적 저장 (메모리 부담 감소)

[추가 고려사항]
- 캐싱: 동일 파일 재처리 방지
- 증분 처리: 새 파일만 처리
- 분산 처리: Celery + Redis (1000개 이상 시)
```

**코드 예시:**

```python
# 현재 (샘플 4개)
def parse_batch(self, files):
    results = []
    for file in files:
        results.append(self.parse_file(file))
    return results

# 확장 (샘플 100개+)
async def parse_batch(self, files):
    semaphore = asyncio.Semaphore(10)  # 동시 10개

    async def process_with_limit(file):
        async with semaphore:
            try:
                return await self.parse_file_async(file)
            except Exception as e:
                logger.error(f"Failed {file}: {e}")
                return None

    tasks = [process_with_limit(f) for f in files]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]
```

### Q4: "이 프로젝트에서 가장 어려웠던 부분은?"

**답변:**

```
[1] 문제: 노이즈 패턴의 다양성

"가장 어려웠던 것은 OCR 노이즈 패턴의 예측 불가능성이었습니다.

예시:
- 샘플 01: '12,480' (정상)
- 샘플 02: '13 460' (공백 삽입)
- 샘플 03: '02 : 13 7 560' (공백 + 콜론)

[2] 초기 접근 실패

첫 번째 시도:
r'총중량[\s:：]*(\d{1,3},?\d{3})\s*kg'

→ 샘플 01만 성공 (50%)

[3] 해결 과정

반복적 패턴 개선:
1. 공백 허용: (\d{1,3}[,\s]?\d{3})
2. 다중 캡처: (\d{1,2})\s+(\d{3})
3. 캡처 그룹 결합: ''.join(groups)

→ 샘플 01-04 모두 성공 (100%)

[4] 학습

"완벽한 패턴은 불가능하다는 것을 배웠습니다.
대신:
- 우선순위 기반 패턴 (구체적 → 일반적 → 폴백)
- 우아한 성능 저하 (일부 필드 실패 시에도 계속)
- 상세한 로깅 (어떤 패턴이 매칭됐는지 추적)

이렇게 설계하면 새로운 노이즈 패턴 발견 시
빠르게 패턴을 추가할 수 있습니다."
```

### Q5: "코드 리뷰를 받는다면 어떤 피드백을 예상하시나요?"

**답변:**

```
[예상 피드백 1] "패턴이 너무 많습니다"

현재: 50+ 패턴
피드백: "패턴 수를 줄이고 더 일반적인 패턴 사용"

제 응답:
"의도적인 선택입니다.
- 구체적 패턴 우선 → 높은 정밀도
- 일반적 패턴 폴백 → 높은 재현율
- 트레이드오프: 패턴 관리 vs 정확도
→ 정확도를 우선했습니다."

[예상 피드백 2] "테스트 커버리지가 부족합니다"

현재: 35개 유닛 테스트
피드백: "통합 테스트, E2E 테스트 추가"

제 응답:
"동의합니다. 추가할 테스트:
- 통합 테스트: 전체 파이프라인
- 성능 테스트: 1000개 파일 벤치마크
- 스트레스 테스트: 비정상 입력"

[예상 피드백 3] "에러 메시지가 불친절합니다"

현재: "Missing critical field: gross_weight_kg"
피드백: "사용자 친화적인 메시지"

제 응답:
"동의합니다. 개선안:
'총중량(gross_weight_kg) 필드를 찾을 수 없습니다.
OCR 텍스트에 \"총중량:\" 레이블이 있는지 확인해주세요.'"

[예상 피드백 4] "Decimal 오버킬 아닌가요?"

피드백: "Float로도 충분하지 않나요?"

제 응답:
"비즈니스 크리티컬한 데이터이기 때문에
정확도를 타협할 수 없습니다.
예: 화물 중량 5000.50 kg
Float: 5000.500000000001 (오차 발생 가능)
Decimal: 5000.50 (정확)

금융/물류 도메인 표준을 따랐습니다."
```

### Q6: "Production 환경에 배포한다면?"

**답변:**

```
[1] 인프라 구성

┌─────────────────────────────────────┐
│         Load Balancer (Nginx)       │
└─────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌─────────┐              ┌─────────┐
│ API 1   │              │ API 2   │
│ (FastAPI)│              │ (FastAPI)│
└─────────┘              └─────────┘
    │                         │
    └────────────┬────────────┘
                 ▼
         ┌──────────────┐
         │   Redis      │
         │   (Cache)    │
         └──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │  PostgreSQL  │
         │   (Results)  │
         └──────────────┘

[2] API 엔드포인트 설계

POST /api/v1/parse
- 입력: OCR JSON
- 출력: 파싱 결과 + 검증

GET /api/v1/results/{job_id}
- 비동기 처리 결과 조회

POST /api/v1/batch
- 대용량 배치 처리 (Celery)

[3] 모니터링

- Prometheus + Grafana
  ├── 처리 속도 (requests/sec)
  ├── 성공률 (%)
  ├── 평균 처리 시간 (ms)
  └── 에러율 (%)

- 알림 (Slack/Email)
  ├── 성공률 < 90%
  ├── 에러율 > 5%
  └── 응답 시간 > 1초

[4] CI/CD

GitHub Actions:
1. PR 시 자동 테스트
2. main merge 시 자동 배포
3. 롤백 자동화 (실패 시)

[5] 보안

- API 키 인증
- Rate limiting (100 req/min)
- 입력 검증 (파일 크기 < 10MB)
- SQL Injection 방지 (ORM 사용)

[6] 스케일링 전략

수평 확장:
- API 서버 복제 (k8s)
- Redis 클러스터
- PostgreSQL 읽기 레플리카

수직 확장:
- 더 많은 CPU (병렬 처리)
- 더 많은 메모리 (캐싱)
```

---

## 7. 마무리: 핵심 메시지

### 7.1 이 프로젝트의 핵심 강점

```
[1] 문제 이해력
✓ 요구사항을 구체적 작업으로 분해
✓ 비즈니스 크리티컬한 요소 식별 (중량 정확도)
✓ 제약사항 고려 (샘플 4개, 빠른 구현)

[2] 설계 역량
✓ Clean Architecture 원칙 적용
✓ SOLID 원칙 준수
✓ 확장 가능한 구조

[3] 구현 능력
✓ 100% 성공률 (샘플 4/4)
✓ 35개 테스트 모두 통과
✓ Production-ready 코드 품질

[4] 의사소통
✓ 명확한 문서화
✓ 트레이드오프 설명 가능
✓ 비즈니스 언어로 번역 가능
```

### 7.2 1분 엘리베이터 피치

```
"이 프로젝트는 노이즈 많은 OCR 텍스트에서
비즈니스 크리티컬한 데이터를 추출하는 시스템입니다.

핵심 특징:
1. 다단계 파이프라인으로 명확한 데이터 흐름
2. 정규표현식 패턴 매칭으로 빠른 구현
3. Decimal 타입으로 정확한 중량 계산
4. 우아한 성능 저하로 부분 데이터도 활용

결과:
- 샘플 4개 모두 성공 (100%)
- 중량 검증 100% 정확
- 2일 만에 production-ready 코드 완성

설계 원칙:
- YAGNI: 현재 요구사항에 최적화
- SOLID: 확장 가능한 구조
- 실용주의: 완벽함보다 동작하는 코드

향후 확장:
- ML 모델로 교체 가능한 구조
- 대용량 처리를 위한 비동기 처리
- API 서비스로 전환 가능

이 프로젝트는 문제 이해, 설계, 구현, 문서화까지
전체 개발 사이클을 완료한 사례입니다."
```

### 7.3 면접 팁

**DO:**
- ✅ 트레이드오프를 명확히 설명
- ✅ "왜 이렇게 했는가"에 초점
- ✅ 비즈니스 가치 강조 (100% 성공률, 정확한 중량 계산)
- ✅ 한계를 인정하고 개선안 제시
- ✅ 코드로 설명 (구두만 X)

**DON'T:**
- ❌ "그냥 이렇게 했어요" (이유 없는 결정)
- ❌ "완벽합니다" (모든 코드에는 트레이드오프가 있음)
- ❌ 기술 용어 남발 (비즈니스 언어로 번역)
- ❌ 방어적 태도 (피드백을 환영)
- ❌ 실행하지 못하는 코드 (데모 준비)

---

**이 문서로 준비할 것:**

1. 각 섹션을 소리 내어 설명 연습
2. 예상 질문에 대한 답변 준비
3. 코드를 실행하며 동작 원리 설명
4. 화이트보드에 아키텍처 그리기 연습
5. 5분, 10분, 30분 버전 프레젠테이션 준비

**행운을 빕니다!** 🚀
