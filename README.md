# DevRunDev
- DevRunDev는 IT 및 개발자를 위한 온라인 교육 플랫폼입니다.
- 강사들은 실무 중심의 강의를 제작하고 수강생들은 최신 기술을 배우며 성장할 수 있도록 지원합니다.
- 또한 강의 진행률, 평가 시스템, 강의 별 퀴즈 등의 기능을 통해 효율적인 학습 경험을 제공합니다.

## 1. 🎯 주요 기능
### 1) 사용자 관리

- 역할 기반 사용자 시스템: 학생, 강사, 관리자 역할 구분
- 강사 신청: 강사 자격 신청 및 관리자 승인 기능

### 2) 강의 관리

- 섹션 및 레슨 구조: 체계적인 강의 구조 제공
- 강의 승인 프로세스: 품질 관리를 위한 강의 승인 워크플로우
- 강의 검색 및 필터링: 사용자 친화적인 강의 탐색 기능
- 강의 수정 및 관리: 강사가 직접 강의 콘텐츠 관리

### 3) 학습 기능

- 강의 진행률 추적: 학습 현황 및 진행률 확인
- 퀴즈 및 평가: 학습 이해도 확인을 위한 퀴즈 시스템
- 수료증 발급: 강의 완료 시 수료증 발급 기능
- 강의 리뷰 및 평가: 강의 품질을 위한 리뷰 시스템
- QnA : 레슨 별 QnA 기능

### 4) 수강 관리

- 장바구니 기능: 여러 강의 동시 수강 신청
- 강사 대시보드 : 수강 현황, 강의, 강의별 평균 평점, 리뷰, 총 수익 관리
- 강의 결제 기능 : 결제를 통한 수강 신청

## 2. 🛠️ 기술 스택

### 1) Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![githubactions](https://img.shields.io/badge/githubactions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

### 2) 백엔드

![Django](https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white)

Django 주요 패키지:

django-allauth: 소셜 로그인 지원 (Google, Kakao, Naver)

django-environ: 환경 변수 관리

django-extensions: 개발 유틸리티

django-debug-toolbar: 개발 디버깅 도구

Authentication: Django Authentication + django-allauth

### 3) Database
![SQLite3](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=SQLite&logoColor=white)

### 4) 프론트엔드

![HTMX](https://img.shields.io/badge/htmx-3366CC?style=for-the-badge&logo=htmx&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS](https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white)

## 🌐 로컬 개발 환경 셋업 가이드

다음 절차에 따라 로컬 개발 환경을 구성할 수 있습니다.

### 1. 레포지트리 클론

```bash
git clone https://github.com/DevRunDev-DRF/DevRunDev-DRF.git
cd devrundev-drf
```

### 2. uv 설치 (처음 한 번만)

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

설치 확인:

```bash
uv --version
```

### 3. 가상환경 생성

```bash
uv venv
```

### 4. 가상환경 활성화

- **Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

> PowerShell 실행 결차에 따라 `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` 명령이 필요할 수 있습니다.

- **Windows CMD**

```cmd
.\.venv\Scripts\activate.bat
```

- **Git Bash / WSL / macOS / Linux**

```bash
source .venv/bin/activate
```

또는 가상환경을 활성화하지 않고도 아래와 같이 uv run, uv pip 명령어를 사용하여 실행 및 패키지 관리를 할 수 있습니다:
```bash
uv run python manage.py runserver
uv pip list
```

### 5. 의존성 설치

```bash
uv sync
```

> `pyproject.toml`과 `uv.lock`을 기준으로 모든 패키지가 설치됩니다.

### 6. .env에 필요한 설정 추가
```sh
cp env.dev.example .env
```

### 7. migration
```sh
uv run python manage.py migrate
```

### 8. seed_data command

```sh
uv run python manage.py seed_data
```

---

## 4.📝 API 문서

### 1. 사용자 관리 API (accounts)

#### 인증 및 계정 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/accounts/register/` | 사용자 회원가입 폼/처리 | ❌ | 없음 |
| GET/POST | `/accounts/login/` | 사용자 로그인 폼/처리 | ❌ | 없음 |
| GET/POST | `/accounts/logout/` | 사용자 로그아웃 | ✅ | 로그인 사용자 |
| GET | `/accounts/profile/` | 사용자 프로필 조회 | ✅ | 로그인 사용자 |
| GET | `/accounts/user/me/` | 사용자 정보 조회 (API) | ✅ | 로그인 사용자 |
| PATCH/PUT | `/accounts/user/me/` | 사용자 정보 수정 (API) | ✅ | 로그인 사용자 |

#### 강사 신청

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/accounts/instructor-application-form/` | 강사 신청 폼 보기 | ✅ | 학생 |
| POST | `/api/instructor-applications/` | 강사 신청하기 | ✅ | 학생 |
| GET | `/api/instructor-applications/` | 강사 신청 목록 보기 | ✅ | 관리자, 본인 신청 조회 |
| GET | `/api/instructor-applications/{id}/` | 강사 신청 상세 보기 | ✅ | 관리자, 본인 신청만 조회 |

### 2. 강의 관리 API (courses)

#### 강의 검색 및 조회

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/courses/` | 강의 목록 조회 | ❌ | 없음 (승인된 강의만) |
| GET | `/courses/{id}/` | 강의 상세 조회 | ❌ | 없음 (승인된 강의만) |
| GET | `/courses/search/` | 강의 검색 | ❌ | 없음 (승인된 강의만) |
| GET | `/api/courses/` | 강의 목록 조회 (API) | ❌ | 없음 (승인된 강의만) |
| GET | `/api/courses/{id}/` | 강의 상세 조회 (API) | ❌ | 없음 (승인된 강의만) |

#### 강의 생성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/courses/create/` | 강의 생성 폼/처리 | ✅ | 강사 |
| GET/POST | `/courses/{id}/edit/` | 강의 수정 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/{id}/delete/` | 강의 삭제 확인/처리 | ✅ | 강의 소유 강사 |
| POST | `/api/courses/{id}/enroll/` | 강의 수강 신청 | ✅ | 로그인 사용자 |

#### 섹션 및 레슨 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/courses/sections/create/` | 섹션 생성 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/sections/{id}/edit/` | 섹션 수정 폼/처리 | ✅ | 강의 소유 강사 |
| POST | `/courses/sections/{id}/delete/` | 섹션 삭제 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/lessons/create/` | 레슨 생성 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/lessons/{id}/edit/` | 레슨 수정 폼/처리 | ✅ | 강의 소유 강사 |
| POST | `/courses/lessons/{id}/delete/` | 레슨 삭제 | ✅ | 강의 소유 강사 |
| GET | `/courses/lessons/{id}/` | 레슨 상세 조회 및 시청 | ✅ | 수강 학생, 강의 소유 강사 |

#### 강사 대시보드

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/courses/instructor/dashboard/` | 강사 대시보드 | ✅ | 강사 |

### 3. 수강 관리 API (enrollments)

#### 수강 신청 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/enrollments/my-courses/` | 내 수강 강의 목록 | ✅ | 로그인 사용자 |
| GET | `/api/enrollments/` | 내 수강 신청 목록 (API) | ✅ | 로그인 사용자 |
| GET | `/api/enrollments/{id}/` | 수강 신청 상세 (API) | ✅ | 본인 수강, 강의 소유 강사 |
| POST | `/api/enrollments/{id}/reset_progress/` | 수강 진행 상태 초기화 | ✅ | 본인 수강만 |

#### 수료증 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/enrollments/my-certificates/` | 내 수료증 목록 | ✅ | 로그인 사용자 |
| GET | `/enrollments/certificate/{certificate_id}/` | 수료증 상세 보기 | ✅ | 본인 수료증 |
| GET | `/enrollments/certificate/{certificate_id}/print/` | 수료증 인쇄 | ✅ | 본인 수료증 |
| POST | `/api/enrollments/{id}/generate_certificate/` | 수료증 발급 | ✅ | 본인 수강, 강의 완료 필요 |

#### 장바구니 및 결제

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/enrollments/cart-view/` | 장바구니 페이지 | ✅ | 로그인 사용자 |
| POST | `/api/cart/` | 장바구니에 강의 추가 | ✅ | 로그인 사용자 |
| DELETE | `/api/cart/{id}/` | 장바구니에서 강의 제거 | ✅ | 본인 장바구니만 |
| POST | `/api/cart/checkout/` | 장바구니 결제 | ✅ | 로그인 사용자 |
| POST | `/enrollments/checkout-free/` | 무료 강의 수강 신청 | ✅ | 로그인 사용자 |
| POST | `/enrollments/payments/prepare/` | 결제 준비 | ✅ | 로그인 사용자 |
| POST | `/enrollments/payments/verify/` | 결제 검증 | ✅ | 로그인 사용자 |
| POST | `/enrollments/payments/cancel/` | 결제 취소 | ✅ | 로그인 사용자 |

#### 학습 진행 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| POST | `/api/progress/mark_completed/` | 레슨 완료 표시 | ✅ | 수강 학생만 |
| POST | `/api/progress/update_last_watched/` | 마지막 시청 시간 갱신 | ✅ | 수강 학생만 |

### 4. 퀴즈 관리 API (quizzes)

#### 퀴즈 조회 및 응시

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/quizzes/` | 퀴즈 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/` | 퀴즈 상세 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/attempt/` | 퀴즈 시도 | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/quizzes/{id}/submit/` | 퀴즈 제출 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/result/` | 퀴즈 결과 | ✅ | 수강 학생, 강의 소유 강사 |

#### 퀴즈 생성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/quizzes/create/` | 퀴즈 생성 폼/처리 | ✅ | 강사 |
| GET/POST | `/quizzes/{id}/edit/` | 퀴즈 수정 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/{id}/delete/` | 퀴즈 삭제 확인/처리 | ✅ | 퀴즈 소유 강사 |

#### 문제 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/quizzes/question/create/` | 문제 생성 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/question/{id}/edit/` | 문제 수정 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/question/{id}/delete/` | 문제 삭제 확인/처리 | ✅ | 퀴즈 소유 강사 |

### 5. 리뷰 관리 API (reviews)

#### 리뷰 조회 및 작성

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/api/reviews/` | 리뷰 목록 조회 | ❌ | 없음 (공개 리뷰만) |
| GET | `/api/reviews/{id}/` | 리뷰 상세 조회 | ❌ | 없음 (공개 리뷰만) |
| POST | `/api/reviews/` | 리뷰 작성 | ✅ | 수강 학생만 |
| PUT/PATCH | `/api/reviews/{id}/` | 리뷰 수정 | ✅ | 본인 리뷰만 |
| DELETE | `/api/reviews/{id}/` | 리뷰 삭제 | ✅ | 본인 리뷰만 |
| GET/POST | `/reviews/{review_id}/edit/` | 리뷰 수정 폼/처리 | ✅ | 본인 리뷰만 |
| GET/POST | `/reviews/{review_id}/delete/` | 리뷰 삭제 확인/처리 | ✅ | 본인 리뷰만 |

### 6. 질문 답변 API (qna)

#### 질문 조회 및 작성

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/qna/` | 질문 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/qna/course/{course_id}/` | 강의별 질문 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/qna/{id}/` | 질문 상세 | ✅ | 수강 학생, 강의 소유 강사 |
| GET/POST | `/qna/create/` | 질문 작성 폼/처리 | ✅ | 수강 학생 |
| GET/POST | `/qna/{id}/edit/` | 질문 수정 폼/처리 | ✅ | 본인 질문만 |
| GET/POST | `/qna/{id}/delete/` | 질문 삭제 확인/처리 | ✅ | 본인 질문만 |

#### 답변 작성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| POST | `/qna/{id}/` | 답변 작성 | ✅ | 수강 학생, 강의 소유 강사 |
| GET/POST | `/qna/answer/{id}/edit/` | 답변 수정 폼/처리 | ✅ | 본인 답변만 |
| GET/POST | `/qna/answer/{id}/delete/` | 답변 삭제 확인/처리 | ✅ | 본인 답변만 |
| POST | `/qna/answer/{id}/accept/` | 답변 채택 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/answer/{id}/unaccept/` | 답변 채택 취소 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/{id}/mark-resolved/` | 질문 해결됨 표시 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/{id}/mark-unresolved/` | 질문 미해결 표시 | ✅ | 질문 작성자, 강의 소유 강사 |

## 5. 📁프로젝트 구조

## 6. 💻 화면 설계

## 7. ERD

![DevRunDev-DRF-ERD](https://github.com/user-attachments/assets/c5905a90-e53d-405c-baea-7d64a9452d40)
