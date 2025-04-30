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

### 8. 디렉토리 생성

```sh
uv run python setup_directories.py
```

### 9. seed_data command

```sh
uv run python manage.py seed_data
```

---

## 4.📝 API 문서
# 📝 DevRunDev 온라인 강의 플랫폼 - API 문서

## 목차
1. [사용자 관리 API (accounts)](#1-사용자-관리-api-accounts)
2. [강의 관리 API (courses)](#2-강의-관리-api-courses)
3. [수강 관리 API (enrollments)](#3-수강-관리-api-enrollments)
4. [퀴즈 관리 API (quizzes)](#4-퀴즈-관리-api-quizzes)
5. [리뷰 관리 API (reviews)](#5-리뷰-관리-api-reviews)
6. [질문 답변 API (qna)](#6-질문-답변-api-qna)
7. [관리자 대시보드 API (admin-dashboard)](#7-관리자-대시보드-api-admin-dashboard)

## 1. 사용자 관리 API (accounts)

### 인증 및 계정 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/accounts/register/` | 사용자 회원가입 폼/처리 | ❌ | 없음 |
| GET/POST | `/accounts/login/` | 사용자 로그인 폼/처리 | ❌ | 없음 |
| GET/POST | `/accounts/logout/` | 사용자 로그아웃 | ✅ | 로그인 사용자 |
| GET | `/accounts/profile/` | 사용자 프로필 조회 | ✅ | 로그인 사용자 |
| GET/PATCH/PUT  | `/accounts/user/me/` | 사용자 정보 조회 (API) | ✅ | 로그인 사용자 |
| PATCH/PUT | `/accounts/user/me/` | 사용자 정보 수정 (API) | ✅ | 로그인 사용자 |
| GET | `/api/users/` | 사용자 목록 조회 (API) | ✅ | 관리자 |
| GET | `/api/users/{id}/` | 사용자 상세 조회 (API) | ✅ | 관리자, 본인 |
| POST | `/admin-dashboard/instructor-applications/{id}/approve/` | 강사 신청 승인 | ✅ | 관리자 |
| POST | `/admin-dashboard/instructor-applications/{id}/reject/` | 강사 신청 거부 | ✅ | 관리자 |
| GET | `/admin/dashboard-data/` | 대시보드 데이터 API | ✅ | 관리자 |
| GET | `/admin-dashboard/analytics/` | 분석 데이터 | ✅ | 관리자 |
| GET | `/admin-dashboard/user-analytics/` | 사용자 분석 데이터 | ✅ | 관리자 |

### 커스텀 Django 관리자 대시보드

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/admin/` | Django 관리자 사이트 | ✅ | 관리자 |
| GET | `/admin/accounts/user/` | 사용자 관리 | ✅ | 관리자 |
| GET | `/admin/accounts/instructorapplication/` | 강사 신청 관리 | ✅ | 관리자 |
| GET | `/admin/courses/course/` | 강의 관리 | ✅ | 관리자 |
| GET | `/admin/courses/section/` | 섹션 관리 | ✅ | 관리자 |
| GET | `/admin/courses/lesson/` | 레슨 관리 | ✅ | 관리자 |
| GET | `/admin/enrollments/enrollment/` | 수강 신청 관리 | ✅ | 관리자 |
| GET | `/admin/enrollments/certificate/` | 수료증 관리 | ✅ | 관리자 |
| GET | `/admin/enrollments/payment/` | 결제 관리 | ✅ | 관리자 |
| GET | `/admin/quizzes/quiz/` | 퀴즈 관리 | ✅ | 관리자 |
| GET | `/admin/quizzes/quizattempt/` | 퀴즈 시도 관리 | ✅ | 관리자 |
| GET | `/admin/reviews/review/` | 리뷰 관리 | ✅ | 관리자 |
| GET | `/admin/qna/question/` | 질문 관리 | ✅ | 관리자 |
| GET | `/admin/qna/answer/` | 답변 관리 | ✅ | 관리자 |

### 소셜 로그인

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/accounts/google/login/` | Google 로그인 | ❌ | 없음 |
| GET/POST | `/accounts/kakao/login/` | Kakao 로그인 | ❌ | 없음 |
| GET/POST | `/accounts/naver/login/` | Naver 로그인 | ❌ | 없음 |

### 강사 신청

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/accounts/instructor-application-form/` | 강사 신청 폼 보기 | ✅ | 학생 |
| POST | `/api/instructor-applications/` | 강사 신청하기 | ✅ | 학생 |
| GET | `/api/instructor-applications/` | 강사 신청 목록 보기 | ✅ | 관리자, 본인 신청 조회 |
| GET | `/api/instructor-applications/{id}/` | 강사 신청 상세 보기 | ✅ | 관리자, 본인 신청만 조회 |
| PUT/PATCH | `/api/instructor-applications/{id}/` | 강사 신청 수정 | ✅ | 관리자, 본인 신청만 수정 |
| DELETE | `/api/instructor-applications/{id}/` | 강사 신청 삭제 | ✅ | 관리자, 본인 신청만 삭제 |

## 2. 강의 관리 API (courses)

### 강의 검색 및 조회

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/courses/` | 강의 목록 조회 | ❌ | 없음 (승인된 강의만) |
| GET | `/courses/{id}/` | 강의 상세 조회 | ❌ | 없음 (승인된 강의만) |
| GET | `/courses/search/` | 강의 검색 | ❌ | 없음 (승인된 강의만) |
| GET | `/api/courses/` | 강의 목록 조회 (API) | ❌ | 없음 (승인된 강의만) |
| GET | `/api/courses/{id}/` | 강의 상세 조회 (API) | ❌ | 없음 (승인된 강의만) |

### 강의 생성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/courses/create/` | 강의 생성 폼/처리 | ✅ | 강사 |
| GET/POST | `/courses/create-with-content/` | 강의와 콘텐츠 한번에 생성 | ✅ | 강사 |
| GET/POST | `/courses/{id}/edit/` | 강의 수정 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/{id}/delete/` | 강의 삭제 확인/처리 | ✅ | 강의 소유 강사 |
| POST | `/api/courses/{id}/enroll/` | 강의 수강 신청 | ✅ | 로그인 사용자 |
| POST | `/api/courses/` | 강의 생성 (API) | ✅ | 강사 |
| PUT/PATCH | `/api/courses/{id}/` | 강의 수정 (API) | ✅ | 강의 소유 강사 |
| DELETE | `/api/courses/{id}/` | 강의 삭제 (API) | ✅ | 강의 소유 강사 |
| POST | `/api/courses/create_with_content/` | 강의와 콘텐츠 한번에 생성 (API) | ✅ | 강사 |

### 섹션 및 레슨 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/courses/sections/create/` | 섹션 생성 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/sections/{id}/edit/` | 섹션 수정 폼/처리 | ✅ | 강의 소유 강사 |
| POST | `/courses/sections/{id}/delete/` | 섹션 삭제 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/lessons/create/` | 레슨 생성 폼/처리 | ✅ | 강의 소유 강사 |
| GET/POST | `/courses/lessons/{id}/edit/` | 레슨 수정 폼/처리 | ✅ | 강의 소유 강사 |
| POST | `/courses/lessons/{id}/delete/` | 레슨 삭제 | ✅ | 강의 소유 강사 |
| GET | `/courses/lessons/{id}/` | 레슨 상세 조회 및 시청 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/sections/` | 섹션 목록 조회 (API) | ❌ | 없음 (승인된 강의만) |
| GET | `/api/sections/{id}/` | 섹션 상세 조회 (API) | ❌ | 없음 (승인된 강의만) |
| POST | `/api/sections/` | 섹션 생성 (API) | ✅ | 강의 소유 강사 |
| PUT/PATCH | `/api/sections/{id}/` | 섹션 수정 (API) | ✅ | 강의 소유 강사 |
| DELETE | `/api/sections/{id}/` | 섹션 삭제 (API) | ✅ | 강의 소유 강사 |
| GET | `/api/lessons/` | 레슨 목록 조회 (API) | ❌ | 없음 (승인된 강의만) |
| GET | `/api/lessons/{id}/` | 레슨 상세 조회 (API) | ❌ | 없음 (승인된 강의만) |
| POST | `/api/lessons/` | 레슨 생성 (API) | ✅ | 강의 소유 강사 |
| PUT/PATCH | `/api/lessons/{id}/` | 레슨 수정 (API) | ✅ | 강의 소유 강사 |
| DELETE | `/api/lessons/{id}/` | 레슨 삭제 (API) | ✅ | 강의 소유 강사 |

### 강사 대시보드

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/courses/instructor/dashboard/` | 강사 대시보드 | ✅ | 강사 |

## 3. 수강 관리 API (enrollments)

### 수강 신청 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/enrollments/my-courses/` | 내 수강 강의 목록 | ✅ | 로그인 사용자 |
| GET | `/api/enrollments/` | 내 수강 신청 목록 (API) | ✅ | 로그인 사용자 |
| GET | `/api/enrollments/{id}/` | 수강 신청 상세 (API) | ✅ | 본인 수강, 강의 소유 강사 |
| POST | `/api/enrollments/` | 수강 신청 생성 (API) | ✅ | 로그인 사용자 |
| PUT/PATCH | `/api/enrollments/{id}/` | 수강 신청 수정 (API) | ✅ | 본인 수강, 강의 소유 강사 |
| DELETE | `/api/enrollments/{id}/` | 수강 신청 삭제 (API) | ✅ | 본인 수강, 강의 소유 강사 |
| POST | `/api/enrollments/{id}/reset_progress/` | 수강 진행 상태 초기화 | ✅ | 본인 수강만 |

### 수료증 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/enrollments/my-certificates/` | 내 수료증 목록 | ✅ | 로그인 사용자 |
| GET | `/enrollments/certificate/{certificate_id}/` | 수료증 상세 보기 | ✅ | 본인 수료증 |
| GET | `/enrollments/certificate/{certificate_id}/print/` | 수료증 인쇄 | ✅ | 본인 수료증 |
| POST | `/api/enrollments/{id}/generate_certificate/` | 수료증 발급 | ✅ | 본인 수강, 강의 완료 필요 |
| GET | `/api/certificates/` | 수료증 목록 조회 (API) | ✅ | 로그인 사용자 (본인 것만) |
| GET | `/api/certificates/{id}/` | 수료증 상세 조회 (API) | ✅ | 본인 수료증만 |

### 장바구니 및 결제

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
| GET | `/enrollments/my-payments/` | 결제 내역 | ✅ | 로그인 사용자 |
| POST | `/enrollments/payment/{id}/cancel-request/` | 결제 취소 요청 | ✅ | 로그인 사용자 |
| POST | `/enrollments/payment/cancel/` | 결제 취소 처리 | ✅ | 로그인 사용자 |
| GET | `/enrollments/payment/{id}/cancel-complete/` | 결제 취소 완료 | ✅ | 로그인 사용자 |
| GET | `/enrollments/cart/{id}/delete/` | 장바구니 항목 삭제 | ✅ | 본인 장바구니만 |
| GET | `/api/cart/` | 장바구니 목록 조회 (API) | ✅ | 로그인 사용자 |

### 학습 진행 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| POST | `/api/progress/mark_completed/` | 레슨 완료 표시 | ✅ | 수강 학생만 |
| POST | `/api/progress/update_last_watched/` | 마지막 시청 시간 갱신 | ✅ | 수강 학생만 |
| GET | `/api/progress/` | 학습 진행 상황 목록 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/progress/{id}/` | 학습 진행 상황 상세 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/api/progress/` | 학습 진행 상황 생성 (API) | ✅ | 수강 학생만 |
| PUT/PATCH | `/api/progress/{id}/` | 학습 진행 상황 수정 (API) | ✅ | 수강 학생만 |
| DELETE | `/api/progress/{id}/` | 학습 진행 상황 삭제 (API) | ✅ | 수강 학생만 |

## 4. 퀴즈 관리 API (quizzes)

### 퀴즈 조회 및 응시

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/quizzes/` | 퀴즈 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/` | 퀴즈 상세 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/attempt/` | 퀴즈 시도 | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/quizzes/{id}/submit/` | 퀴즈 제출 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/quizzes/{id}/result/` | 퀴즈 결과 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/quizzes/` | 퀴즈 목록 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/quizzes/{id}/` | 퀴즈 상세 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/api/quizzes/{id}/start-attempt/` | 퀴즈 시도 시작 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/api/quizzes/{id}/submit-attempt/` | 퀴즈 제출 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/attempts/` | 퀴즈 시도 목록 (API) | ✅ | 본인 시도, 강의 소유 강사 |
| GET | `/api/attempts/{id}/` | 퀴즈 시도 상세 (API) | ✅ | 본인 시도, 강의 소유 강사 |

### 퀴즈 생성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/quizzes/create/` | 퀴즈 생성 폼/처리 | ✅ | 강사 |
| GET/POST | `/quizzes/{id}/edit/` | 퀴즈 수정 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/{id}/delete/` | 퀴즈 삭제 확인/처리 | ✅ | 퀴즈 소유 강사 |
| POST | `/api/quizzes/` | 퀴즈 생성 (API) | ✅ | 강사 |
| PUT/PATCH | `/api/quizzes/{id}/` | 퀴즈 수정 (API) | ✅ | 퀴즈 소유 강사 |
| DELETE | `/api/quizzes/{id}/` | 퀴즈 삭제 (API) | ✅ | 퀴즈 소유 강사 |
| POST | `/api/quizzes/{id}/mark_as_resolved/` | 퀴즈 해결됨 표시 (API) | ✅ | 퀴즈 소유 강사 |
| POST | `/api/quizzes/{id}/mark_as_unresolved/` | 퀴즈 미해결 표시 (API) | ✅ | 퀴즈 소유 강사 |

### 문제 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET/POST | `/quizzes/question/create/` | 문제 생성 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/question/{id}/edit/` | 문제 수정 폼/처리 | ✅ | 퀴즈 소유 강사 |
| GET/POST | `/quizzes/question/{id}/delete/` | 문제 삭제 확인/처리 | ✅ | 퀴즈 소유 강사 |
| GET | `/api/questions/` | 문제 목록 조회 (API) | ✅ | 퀴즈 소유 강사 |
| GET | `/api/questions/{id}/` | 문제 상세 조회 (API) | ✅ | 퀴즈 소유 강사 |
| POST | `/api/questions/` | 문제 생성 (API) | ✅ | 퀴즈 소유 강사 |
| PUT/PATCH | `/api/questions/{id}/` | 문제 수정 (API) | ✅ | 퀴즈 소유 강사 |
| DELETE | `/api/questions/{id}/` | 문제 삭제 (API) | ✅ | 퀴즈 소유 강사 |

## 5. 리뷰 관리 API (reviews)

### 리뷰 조회 및 작성

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/api/reviews/` | 리뷰 목록 조회 | ❌ | 없음 (공개 리뷰만) |
| GET | `/api/reviews/{id}/` | 리뷰 상세 조회 | ❌ | 없음 (공개 리뷰만) |
| POST | `/api/reviews/` | 리뷰 작성 | ✅ | 수강 학생만 |
| PUT/PATCH | `/api/reviews/{id}/` | 리뷰 수정 | ✅ | 본인 리뷰만 |
| DELETE | `/api/reviews/{id}/` | 리뷰 삭제 | ✅ | 본인 리뷰만 |
| GET/POST | `/reviews/{review_id}/edit/` | 리뷰 수정 폼/처리 | ✅ | 본인 리뷰만 |
| GET/POST | `/reviews/{review_id}/delete/` | 리뷰 삭제 확인/처리 | ✅ | 본인 리뷰만 |

## 6. 질문 답변 API (qna)

### 질문 조회 및 작성

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/qna/` | 질문 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/qna/course/{course_id}/` | 강의별 질문 목록 | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/qna/{id}/` | 질문 상세 | ✅ | 수강 학생, 강의 소유 강사 |
| GET/POST | `/qna/create/` | 질문 작성 폼/처리 | ✅ | 수강 학생 |
| GET/POST | `/qna/{id}/edit/` | 질문 수정 폼/처리 | ✅ | 본인 질문만 |
| GET/POST | `/qna/{id}/delete/` | 질문 삭제 확인/처리 | ✅ | 본인 질문만 |
| GET | `/api/questions/` | 질문 목록 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/questions/{id}/` | 질문 상세 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/api/questions/` | 질문 생성 (API) | ✅ | 수강 학생 |
| PUT/PATCH | `/api/questions/{id}/` | 질문 수정 (API) | ✅ | 본인 질문만 |
| DELETE | `/api/questions/{id}/` | 질문 삭제 (API) | ✅ | 본인 질문만 |

### 답변 작성 및 관리

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| POST | `/qna/{id}/` | 답변 작성 | ✅ | 수강 학생, 강의 소유 강사 |
| GET/POST | `/qna/answer/{id}/edit/` | 답변 수정 폼/처리 | ✅ | 본인 답변만 |
| GET/POST | `/qna/answer/{id}/delete/` | 답변 삭제 확인/처리 | ✅ | 본인 답변만 |
| POST | `/qna/answer/{id}/accept/` | 답변 채택 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/answer/{id}/unaccept/` | 답변 채택 취소 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/{id}/mark-resolved/` | 질문 해결됨 표시 | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/qna/{id}/mark-unresolved/` | 질문 미해결 표시 | ✅ | 질문 작성자, 강의 소유 강사 |
| GET | `/api/answers/` | 답변 목록 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| GET | `/api/answers/{id}/` | 답변 상세 조회 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| POST | `/api/answers/` | 답변 생성 (API) | ✅ | 수강 학생, 강의 소유 강사 |
| PUT/PATCH | `/api/answers/{id}/` | 답변 수정 (API) | ✅ | 본인 답변만 |
| DELETE | `/api/answers/{id}/` | 답변 삭제 (API) | ✅ | 본인 답변만 |
| POST | `/api/answers/{id}/accept/` | 답변 채택 (API) | ✅ | 질문 작성자, 강의 소유 강사 |
| POST | `/api/answers/{id}/unaccept/` | 답변 채택 취소 (API) | ✅ | 질문 작성자, 강의 소유 강사 |

## 7. 관리자 대시보드 API (admin-dashboard)

### 관리자 대시보드

| 메서드 | URL 패턴 | 기능 | 로그인 필요 | 권한 |
|---|---|---|---|---|
| GET | `/admin-dashboard/dashboard/` | 관리자 대시보드 | ✅ | 관리자 |
| GET | `/admin-dashboard/users/` | 사용자 관리 | ✅ | 관리자 |
| GET | `/admin-dashboard/courses/` | 강의 관리 | ✅ | 관리자 |
| GET | `/admin-dashboard/instructor-applications/` | 강사 신청 관리 | ✅ | 관리자 |
| GET | `/admin-dashboard/payments/` | 결제 관리 | ✅ | 관리자 |

## 추가 정보

### API 인증
- 모든 API는 기본적으로 Django REST Framework의 인증 시스템을 사용합니다.
- API 호출 시 인증이 필요한 경우 다음과 같은 방법으로 인증할 수 있습니다:
  1. 토큰 인증: `Authorization: Token <token_key>`
  2. 세션 인증: 웹 브라우저에서 로그인 후 쿠키 사용

### 응답 형식
- 모든 API는 JSON 형식으로 응답합니다.
- 표준 HTTP 상태 코드를 사용합니다:
  - 200: 성공
  - 201: 생성 성공
  - 400: 잘못된 요청
  - 401: 인증 필요
  - 403: 권한 없음
  - 404: 리소스 없음
  - 500: 서버 오류

### 페이지네이션
- 목록 API는 기본적으로 페이지네이션을 지원합니다.
- 기본 페이지 크기는 10개입니다.
- 페이지네이션 매개변수:
  - `page`: 페이지 번호
  - `page_size`: 페이지 크기

### 필터링 및 검색
- 대부분의 목록 API는 필터링과 검색을 지원합니다.
- 필터링 예시: `?course=1&status=in_progress`
- 검색 예시: `?search=파이썬`
- 정렬 예시: `?ordering=-created_at`

### API 문서
- API 문서는 Swagger와 ReDoc을 통해 확인할 수 있습니다.
- Swagger: `/swagger/`
- ReDoc: `/redoc/` | `/api/users/` | 사용자 생성 (API) | ❌ | 없음 |
| PUT/PATCH | `/api/users/{id}/` | 사용자 수정 (API) | ✅ | 관리자, 본인 |
| DELETE | `/api/users/{id}/` | 사용자 삭제 (API) | ✅ | 관리자, 본인 |


## 5. 📁프로젝트 구조
```
📁 DevRunDev/
├── 📁 .github/workflows/      # GitHub CI/CD 워크플로우
│   └── 📄 django_ci.yml       # Django 테스트 자동화
│
├── 📁 accounts/               # 사용자 관리 앱
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # 계정 관련 템플릿
│   │   └── 📁 accounts/       # 계정 관련 템플릿
│   ├── 📁 templatetags/       # 커스텀 템플릿 태그
│   ├── 📄 __init__.py
│   ├── 📄 adapters.py         # 소셜 로그인 어댑터
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 forms.py            # 폼 정의
│   ├── 📄 models.py           # 모델 정의(User, InstructorApplication)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 courses/                # 강의 관리 앱
│   ├── 📁 management/         # 커스텀 명령어
│   │   └── 📁 commands/
│   │       └── 📄 seed_data.py # 샘플 데이터 생성
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # 강의 관련 템플릿
│   │   └── 📁 courses/        # 강의 관련 템플릿
│   ├── 📁 templatetags/       # 커스텀 템플릿 태그
│   │   ├── 📄 __init__.py
│   │   └── 📄 custom_filters.py # 커스텀 필터
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 forms.py            # 폼 정의
│   ├── 📄 models.py           # 모델 정의(Course, Section, Lesson)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 enrollments/            # 수강 신청 및 관리 앱
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # 수강 관련 템플릿
│   │   └── 📁 enrollments/    # 수강 관련 템플릿
│   ├── 📁 templatetags/       # 커스텀 템플릿 태그
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 models.py           # 모델 정의(Enrollment, LessonProgress, Certificate, CartItem, Payment)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   ├── 📄 utils.py            # 유틸리티 함수
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 quizzes/                # 퀴즈 관리 앱
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # 퀴즈 관련 템플릿
│   │   └── 📁 quizzes/        # 퀴즈 관련 템플릿
│   ├── 📁 templatetags/       # 커스텀 템플릿 태그
│   │   ├── 📄 __init__.py
│   │   └── 📄 quiz_filters.py # 퀴즈 관련 필터
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 models.py           # 모델 정의(Quiz, Question, Choice, QuizAttempt, Answer)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 reviews/                # 리뷰 관리 앱
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # 리뷰 관련 템플릿
│   │   └── 📁 reviews/        # 리뷰 관련 템플릿
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 models.py           # 모델 정의(Review)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 qna/                    # 질문 답변 앱
│   ├── 📁 migrations/         # 데이터베이스 마이그레이션
│   ├── 📁 templates/          # Q&A 관련 템플릿
│   │   └── 📁 qna/            # Q&A 관련 템플릿
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 관리자 인터페이스
│   ├── 📄 apps.py             # 앱 설정
│   ├── 📄 models.py           # 모델 정의(Question, Answer)
│   ├── 📄 permissions.py      # 권한 클래스
│   ├── 📄 serializers.py      # REST API 시리얼라이저
│   ├── 📄 tests.py            # 테스트 코드
│   ├── 📄 urls.py             # URL 라우팅
│   └── 📄 views.py            # 뷰 정의
│
├── 📁 config/                 # 프로젝트 설정
│   ├── 📄 __init__.py
│   ├── 📄 admin.py            # 커스텀 관리자 사이트 설정
│   ├── 📄 admin_views.py      # 관리자 대시보드 뷰
│   ├── 📄 asgi.py             # ASGI 설정
│   ├── 📄 settings.py         # 프로젝트 설정
│   ├── 📄 urls.py             # 메인 URL 설정
│   ├── 📄 urls_admin.py       # 관리자 대시보드 URL
│   ├── 📄 views.py            # 기본 뷰
│   ├── 📄 views_admin.py      # 관리자 대시보드 뷰
│   └── 📄 wsgi.py             # WSGI 설정
│
├── 📁 static/                 # 정적 파일
│   ├── 📁 css/                # CSS 파일
│   │   ├── 📄 tailwind.css    # Tailwind CSS
│   │   └── 📄 custom.css      # 커스텀 CSS
│   ├── 📁 js/                 # JavaScript 파일
│   │   ├── 📄 htmx.min.js     # HTMX 라이브러리
│   │   └── 📄 alpine.min.js   # Alpine.js 라이브러리
│   └── 📁 images/             # 이미지 파일
│       └── 📄 logo.svg        # 로고 이미지
│
├── 📁 templates/              # 공통 템플릿
│   ├── 📁 admin/              # 관리자 템플릿
│   │   ├── 📄 custom_index.html  # 커스텀 관리자 인덱스
│   │   ├── 📄 dashboard.html     # 관리자 대시보드
│   │   └── 📄 analytics.html     # 분석 페이지
│   ├── 📁 emails/             # 이메일 템플릿
│   │   ├── 📄 payment_cancel_email.html      # 결제 취소 이메일
│   │   └── 📄 payment_cancel_admin_email.html # 관리자 알림 이메일
│   ├── 📄 base.html           # 기본 템플릿
│   ├── 📄 home.html           # 홈페이지 템플릿
│   ├── 📄 navbar.html         # 네비게이션 바 템플릿
│   └── 📄 footer.html         # 푸터 템플릿
│
├── 📁 media/                  # 미디어 파일 저장 (사용자 업로드)
│   ├── 📁 courses/            # 강의 썸네일 이미지
│   └── 📁 profiles/           # 프로필 이미지
│
├── 📁 docs/                   # 프로젝트 문서
│   ├── 📄 api.md              # API 문서
│   ├── 📄 architecture.md     # 아키텍처 문서
│   ├── 📄 installation.md     # 설치 가이드
│   └── 📄 contribution.md     # 기여 가이드
│
├── 📄 .env.example            # 환경 변수 예시
├── 📄 .gitignore              # Git 무시 파일 설정
├── 📄 .pre-commit-config.yaml # pre-commit 설정
├── 📄 manage.py               # Django 관리 명령어
├── 📄 pytest.ini              # pytest 설정
├── 📄 requirements.txt        # 개발 및 프로덕션 의존성 패키지
├── 📄 requirements-dev.txt    # 개발 전용 의존성 패키지
└── 📄 README.md               # 프로젝트 설명
```

## 6. 💻 화면 설계

## 7. ERD
![DevRunDev_DRF_ERDpng](https://github.com/user-attachments/assets/a1680d19-529a-4b78-938d-1a9b7b58a64b)

