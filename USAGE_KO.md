# BioinfoMCP 사용 가이드

## 1. 환경 설치 (한 번만)

```shell
cd BioinfoMCP
bash setup.sh
```

또는 수동으로:

```shell
conda create -n bioinfomcp-env python=3.10 -y
conda activate bioinfomcp-env
pip install -r requirements.txt
```

## 2. API 키 설정

`.env` 파일에서 사용할 LLM 백엔드에 맞게 설정:

```env
# 사용할 모델 이름
MODEL_NAME=gemini-2.5-pro        # 또는 gpt-4o-mini, gpt-4.1-mini 등

# 아래 중 사용할 백엔드의 키만 입력하면 됨
OPENAI_API_KEY=sk-...            # OpenAI 사용 시
GEMINI_API_KEY=AIzaSy...         # Gemini 사용 시
AZURE_OPENAI_KEY=...             # Azure 사용 시
```

## 3. MCP 서버 생성 (main.py)

### 두 가지 모드

| 모드 | 언제 사용? | 도구 설치 필요? |
|---|---|---|
| **PDF 모드** | 매뉴얼 PDF가 있을 때 | 불필요 |
| **--help 모드** | 도구가 이미 설치되어 있을 때 | 필요 |

---

### 모드 A: PDF 매뉴얼 제공 (도구 설치 불필요, 권장)

도구가 설치되어 있지 않아도 됩니다. PDF 매뉴얼만 있으면 LLM이 분석해서 MCP 서버 코드를 생성합니다.

```shell
conda activate bioinfomcp-env
cd src

python -m main \
    --name "qiime_tools_import" \
    --manual /path/to/tool_manual.pdf \
    --output_location ./mcp-servers/ \
    --model gemini
```

- qiime2처럼 설치가 복잡한 도구도 **PDF만 있으면 바로 변환 가능**
- 호스트 환경과 도구 환경의 충돌 걱정 없음

### 모드 B: --help 명령 실행 (도구가 설치되어 있어야 함)

도구가 현재 conda 환경에 설치되어 있을 때, 도구의 `--help` 출력을 직접 읽어서 변환합니다.

```shell
conda activate bioinfomcp-env
conda install -c bioconda fastqc   # 도구 먼저 설치
cd src

python -m main \
    --name fastqc \
    --manual="--help" \
    --run_help_command True \
    --output_location ./mcp-servers/ \
    --model gemini
```

- 주의: `--manual="--help"` 처럼 `=`로 연결해야 argparse가 올바르게 인식
- 도구가 설치 안 되어 있으면 `is not installed!` 에러 발생

---

### 전체 옵션 요약

```
python -m main \
    --name <도구이름>              # 필수: 생성할 MCP 서버 도구 이름
    --manual <PDF경로 또는 --help>  # 필수: 매뉴얼 소스
    --run_help_command True        # --help 모드일 때만 True
    --output_location <출력폴더>    # 필수: 결과물 저장 경로
    --model <openai|azure|gemini>  # LLM 백엔드 선택 (기본: openai)
    --is_pipeline                  # 파이프라인 모드 (docker-compose 미생성)
```

## 4. 생성 결과물

실행이 완료되면 출력 폴더에 다음 파일이 생성됩니다:

```
mcp-servers/mcp_<도구이름>/
├── app/
│   └── <도구이름>_server.py    ← MCP 서버 코드 (핵심)
├── Dockerfile                  ← Docker 이미지 빌드용
├── docker-compose.yml          ← Docker 실행 설정
├── environment.yaml            ← conda 의존성 (bioconda에서 도구 설치)
└── requirements.txt            ← pip 의존성 (fastmcp)
```

## 5. 생성된 MCP 서버 실행하기

### 방법 A: Docker로 실행 (권장, 환경 충돌 없음)

Docker가 도구를 자동 설치하므로, 호스트에 도구를 설치할 필요가 없습니다.

```shell
# 1. Docker 이미지 빌드 + 컨테이너 실행
cd mcp-servers/mcp_<도구이름>/
docker compose up --build

# 2. AI Agent (Claude Desktop 등) 설정 파일에 추가:
```

```json
{
  "mcpServers": {
    "<도구이름>": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/내/데이터/경로:/app/workspace",
        "mcp-<도구이름>:latest"
      ]
    }
  }
}
```

- `/내/데이터/경로` 부분을 분석할 데이터가 있는 실제 폴더로 변경
- 컨테이너 안에서는 `/app/workspace/`에서 데이터에 접근 가능

### 방법 B: 직접 실행 (도구가 호스트에 설치되어 있어야 함)

```shell
# 1. 도구 설치
conda activate bioinfomcp-env
conda install -c bioconda <도구이름>

# 2. AI Agent 설정 파일에 추가:
```

```json
{
  "<도구이름>": {
    "command": "bash",
    "args": [
      "-c",
      "source ~/miniconda3/etc/profile.d/conda.sh && conda activate bioinfomcp-env && python /path/to/mcp_<도구이름>/app/<도구이름>_server.py"
    ]
  }
}
```

---

## 요약: PDF 모드 vs --help 모드

```
PDF 모드:   매뉴얼 PDF만 있으면 OK → 도구 설치 불필요 → 환경 충돌 없음
--help 모드: 도구가 설치되어 있어야 함 → 환경 충돌 가능성 있음

→ 대부분의 경우 PDF 모드를 권장합니다.
→ 실행은 Docker로 하면 환경 충돌을 완전히 피할 수 있습니다.
```
