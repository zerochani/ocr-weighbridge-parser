# OCR Weighbridge Parser

A production-grade pattern-based OCR text parsing system for extracting structured data from Korean weighbridge receipts.

## 실행 방법 (Execution Method)

### 환경 설정 (Environment Setup)

1. 프로젝트 디렉토리 이동:
```bash
cd ocr-weighbridge-parser
```

2. 가상환경 생성 및 활성화:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

### 사용법 (Usage)

**단일 파일 파싱:**
```bash
python -m src.main -i "path/to/sample_01.json"
```

**배치 파싱 (여러 파일):**
```bash
python -m src.main -i "path/to/sample_*.json"
```

**CSV 출력:**
```bash
python -m src.main -i "path/to/sample_*.json" -f csv -o output/results.csv
```

**디버그 로깅 활성화:**
```bash
python -m src.main -i "path/to/sample_*.json" --log-level DEBUG
```

### 테스트 실행 (Running Tests)

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트 파일
pytest tests/test_extractor.py -v
```

## 의존성/환경 (Dependencies & Environment)

### Python 버전
- **Python 3.8 이상** (권장: Python 3.10+)

### 필수 라이브러리 (Core Dependencies)

```txt
pydantic==2.5.0          # 데이터 검증 및 스키마 정의
python-dateutil==2.8.2   # 날짜/시간 파싱
```

### 개발/테스트 라이브러리 (Development Dependencies)

```txt
pytest==7.4.3            # 테스트 프레임워크
pytest-cov==4.1.0        # 코드 커버리지
```

### 표준 라이브러리 (Standard Library - No Installation Required)

- `re` - 정규표현식 패턴 매칭
- `json` - JSON 파일 처리
- `logging` - 구조화된 로깅
- `unicodedata` - 유니코드 정규화 (한글 처리)
- `decimal` - 고정밀도 소수점 연산
- `datetime` - 날짜/시간 처리
- `pathlib` - 파일 경로 처리
- `argparse` - CLI 인터페이스

### 시스템 요구사항 (System Requirements)

- **OS**: Linux, macOS, Windows
- **Memory**: 최소 512MB RAM
- **Disk**: 50MB (코드 + 의존성)

## 설계 및 주요 가정 (Design & Key Assumptions)

### 아키텍처 설계 원칙

#### 1. 멀티 스테이지 파이프라인 (Multi-Stage Pipeline)

```
Input (OCR JSON)
    ↓
[1] Cleaner (전처리)
    → 유니코드 정규화 (NFKC)
    → 공백 정규화
    → 노이즈 제거
    ↓
[2] Extractor (추출)
    → 50+ 정규표현식 패턴
    → 패턴 우선순위 기반 매칭
    ↓
[3] Normalizer (정규화)
    → 타입 변환 (str → Decimal/datetime)
    → 단위 표준화
    ↓
[4] Validator (검증)
    → 논리 검증 (총중량 = 차량중량 + 실중량)
    → 범위 검증 (0-100,000 kg)
    → 완전성 점수
    ↓
[5] Pydantic Model (스키마)
    → 타입 안전성
    → 런타임 검증
    ↓
Output (JSON/CSV)
```

**설계 이유:**
- **단일 책임 원칙** (SRP): 각 모듈은 하나의 명확한 역할
- **독립적 테스트 가능**: 각 스테이지를 격리하여 테스트
- **유지보수성**: 한 스테이지 수정 시 다른 스테이지 영향 최소화

#### 2. 패턴 기반 추출 (Pattern-Based Extraction)

**결정:** 정규표현식 패턴 매칭 사용 (위치 기반 X, ML 기반 X)

**이유:**
- OCR 출력의 불규칙한 공백, 오타, 레이블 변형 처리
- 영수증 포맷별 필드 위치 변동성 대응
- ML 대비 단순하고 해석 가능한 로직
- YAGNI 원칙 (You Aren't Gonna Need It): 현재 요구사항에는 패턴 매칭으로 충분

**트레이드오프:**
- ✅ 장점: 빠른 구현, 명확한 디버깅, 낮은 의존성
- ❌ 단점: 새로운 포맷 추가 시 패턴 수동 작성 필요

#### 3. Decimal 타입 사용 (vs. Float)

**결정:** 모든 중량 값에 `Decimal` 타입 사용

**이유:**
- 부동소수점 정밀도 문제 회피 (예: `0.1 + 0.2 != 0.3`)
- 금융/비즈니스 계산에서 정확도 필수
- 파이프라인 전체에서 정밀도 유지

**트레이드오프:**
- ✅ 장점: 정확한 계산, 금융 데이터 표준
- ❌ 단점: 약간의 성능 오버헤드 (현재 규모에서는 무시 가능)

#### 4. 우아한 성능 저하 (Graceful Degradation)

**결정:** 부분 데이터도 추출하며, 예외 대신 `None` 반환

**이유:**
- OCR 출력은 완전하지 않을 수 있음
- 부분 데이터라도 비즈니스 가치 존재
- Validation 레이어에서 불완전/무효 데이터 플래그 표시
- 인간 검토 가능한 결과 제공

**트레이드오프:**
- ✅ 장점: 로버스트한 처리, 부분 결과 활용 가능
- ❌ 단점: Validation 로직 복잡도 증가

### 주요 가정 (Key Assumptions)

1. **입력 포맷:** OCR API (예: Naver Clova OCR)의 JSON 출력
   - `pages[].text` 필드에 추출된 텍스트 포함
   - 단일 페이지 문서

2. **언어:** 한국어 계량증명서
   - 필드 레이블: "총중량", "차량중량", "실중량" 등
   - 유니코드 NFKC 정규화 적용

3. **단위:** 모든 중량은 킬로그램 (kg)
   - 톤 단위는 자동 변환하지 않음

4. **중량 관계:** `총중량 = 차량중량 + 실중량`
   - 허용 오차: ±1kg (계측기 오차 고려)

5. **날짜 범위:** 최근 10년 이내 계량 데이터
   - 2016-01-01 ~ 현재

6. **필수 필드:** 총중량, 차량중량, 실중량
   - 이 3개 필드가 없으면 경고 발생

7. **파일 크기:** OCR JSON 파일 < 10MB
   - 대용량 배치 처리는 고려하지 않음

### 검증 로직 (Validation Logic)

**3단계 검증:**

1. **오류 (Errors):** 치명적 문제
   - 필수 필드 누락 (총중량, 차량중량, 실중량)
   - 논리적 모순 (총중량 < 차량중량)
   - 범위 초과 (중량 > 100,000 kg)

2. **경고 (Warnings):** 의심스러운 데이터
   - 중량 계산 불일치 (±1kg 초과)
   - 중요 필드 누락 (차량번호, 날짜)

3. **정보 (Info):** 완전성 점수
   - 추출된 필드 수 / 전체 필드 수

## 한계 및 개선 아이디어 (Limitations & Future Improvements)

### 현재 한계 (Current Limitations)

#### 기능적 한계

1. **단일 페이지만 처리**
   - 여러 페이지 문서의 경우 첫 페이지만 분석
   - 영향: 다중 페이지 영수증 처리 불가

2. **한국어 특화 패턴**
   - 패턴이 한국어 계량증명서에 최적화
   - 영향: 영어/중국어 영수증은 파싱 실패 가능

3. **OCR 수행 안 함**
   - 이미 OCR 처리된 텍스트만 입력 가능
   - 영향: 이미지 파일 직접 처리 불가

4. **레이블 의존성**
   - "총중량:", "차량번호:" 등 레이블 필요
   - 영향: 레이블 없는 숫자만 있는 영수증은 추출 실패

5. **고정된 패턴**
   - 새로운 필드 타입 추가 시 코드 수정 필요
   - 영향: 동적 필드 추가 불가

#### 알려진 엣지 케이스

1. **손글씨 텍스트**
   - OCR 품질 저하로 추출 실패 가능

2. **비표준 레이아웃**
   - 일반적이지 않은 영수증 구조는 파싱 실패

3. **언어 혼합**
   - 한국어와 영어가 섞인 경우 패턴 혼선

4. **매우 큰 숫자**
   - 1백만 이상 숫자는 포맷 오류 가능

### 개선 아이디어 (Future Improvements)

#### Short-Term (빠른 개선)

1. **신뢰도 점수 추가**
   - OCR API의 confidence score를 필드별로 저장
   - 낮은 신뢰도 필드 자동 플래그

2. **패턴 확장**
   - 더 많은 영수증 포맷 커버
   - 영어/중국어 레이블 지원

3. **OCR 오류 자동 보정**
   - 일반적인 오류 패턴 수정 (예: O→0, l→1)
   - Levenshtein distance 기반 레이블 매칭

4. **Excel 출력 지원**
   - `.xlsx` 포맷 지원 (openpyxl 사용)
   - 컬러 코딩으로 경고/오류 표시

5. **진행률 표시**
   - 배치 처리 시 tqdm 진행률 바

#### Medium-Term (중기 개선)

1. **ML 기반 추출**
   - Named Entity Recognition (NER) 모델 훈련
   - 한국어 BERT 모델 활용 (KoBERT)
   - 레이블 없이도 필드 추출 가능

2. **템플릿 학습**
   - 영수증 레이아웃을 자동으로 학습
   - Few-shot learning으로 새로운 포맷 빠르게 추가

3. **멀티 페이지 지원**
   - 여러 페이지에 걸친 영수증 처리
   - 페이지 간 필드 연결

4. **데이터베이스 출력**
   - PostgreSQL/MySQL 직접 저장
   - SQLAlchemy ORM 활용

5. **웹 인터페이스**
   - FastAPI + React 기반 웹 UI
   - 드래그&드롭 파일 업로드
   - 실시간 결과 미리보기

#### Long-Term (장기 비전)

1. **컴퓨터 비전 통합**
   - 이미지 전처리 (회전 보정, 노이즈 제거)
   - OpenCV 활용
   - 직접 이미지 파일 입력 가능

2. **능동 학습 (Active Learning)**
   - 인간 피드백으로 모델 개선
   - 불확실한 케이스 우선 검토

3. **다국어 지원**
   - 영어, 중국어, 일본어 영수증
   - 언어 자동 감지

4. **실시간 API**
   - REST API 엔드포인트
   - 마이크로서비스 아키텍처
   - Docker/Kubernetes 배포

5. **비즈니스 룰 엔진**
   - 코드 수정 없이 검증 규칙 변경
   - YAML/JSON 기반 설정

#### 성능 최적화 (Performance Optimization)

1. **비동기 처리**
   - `asyncio` 기반 병렬 파일 처리
   - 대용량 배치 처리 속도 향상

2. **캐싱**
   - 컴파일된 정규표현식 캐싱
   - LRU 캐시로 중복 계산 방지

3. **분산 처리**
   - Celery 작업 큐
   - Redis 기반 결과 캐싱

---

## 프로젝트 구조 (Project Structure)

```
ocr-weighbridge-parser/
├── src/
│   ├── models/schema.py           # Pydantic 스키마
│   ├── preprocessing/cleaner.py   # 텍스트 전처리
│   ├── extraction/
│   │   ├── patterns.py            # 정규표현식 패턴
│   │   └── extractor.py           # 패턴 매칭 엔진
│   ├── normalization/normalizer.py # 데이터 정규화
│   ├── validation/validator.py     # 검증 로직
│   ├── utils/
│   │   ├── logger.py              # 로깅
│   │   └── io_handler.py          # 파일 I/O
│   ├── config.py                  # 설정
│   └── main.py                    # CLI 진입점
├── tests/                         # 유닛 테스트 (35개)
├── output/                        # 출력 파일
├── requirements.txt               # 의존성
└── README.md                      # 이 문서
```

## 성공률 (Success Rate)

- ✅ **샘플 파일 4개 중 4개 성공 (100%)**
- ✅ **중량 계산 검증: 100% 정확**
- ✅ **유닛 테스트: 35개 모두 통과**

---

**Built for production-grade OCR data processing | ICT Internship Assignment**
