# DevRunddev-DRF

## 로컬 개발 환경 셋업 가이드

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

---
