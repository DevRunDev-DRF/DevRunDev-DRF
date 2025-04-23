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

## 5. 📁프로젝트 구조

## 6. 💻 화면 설계
