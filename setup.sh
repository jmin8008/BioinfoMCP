#!/bin/bash
# BioinfoMCP 환경 자동 설치 스크립트

set -e

ENV_NAME="bioinfomcp-env"

echo "=== BioinfoMCP 환경 설치 시작 ==="

# 1. conda 환경 생성 (이미 있으면 스킵)
if conda info --envs | grep -q "$ENV_NAME"; then
    echo "[스킵] conda 환경 '$ENV_NAME'이 이미 존재합니다."
else
    echo "[생성] conda 환경 '$ENV_NAME' 생성 중..."
    conda create -n "$ENV_NAME" python=3.10 -y
fi

# 2. 환경 활성화
echo "[활성화] conda 환경 '$ENV_NAME' 활성화..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# 3. pip 의존성 설치
echo "[설치] pip 패키지 설치 중..."
pip install -r requirements.txt

echo ""
echo "=== 설치 완료 ==="
echo "사용법: conda activate $ENV_NAME && cd src && python -m main --help"
