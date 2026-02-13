# BioinfoMCP 클라이언트 설정 가이드

QIIME 2 MCP 서버 68종을 Docker로 빌드하고, Claude Desktop / Cursor 등 MCP 클라이언트에 등록하는 방법을 안내합니다.

---

## 1. Docker 데몬 시작

```bash
# systemd 기반 (Ubuntu / Debian)
sudo systemctl start docker
sudo systemctl enable docker   # 부팅 시 자동 시작

# 실행 확인
docker info
```

> 권한 오류(`permission denied`) 발생 시:
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```

---

## 2. 전체 Docker 이미지 빌드

### 2-1. 전체 한번에 빌드

```bash
cd /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/src/mcp-servers

for dir in mcp_qiime_*/; do
  image_name=$(echo "${dir%/}" | sed 's/_/-/g')
  echo "=== Building ${image_name}:latest ==="
  docker build -t "${image_name}:latest" "$dir"
done
```

### 2-2. 개별 빌드 (특정 도구만)

```bash
cd /home/ubuntu/bionexus/jgy/biomcp/BioinfoMCP/src/mcp-servers

# 예: tools-import만 빌드
docker build -t mcp-qiime-tools-import:latest mcp_qiime_tools_import/

# 예: dada2-denoise-paired만 빌드
docker build -t mcp-qiime-dada2-denoise-paired:latest mcp_qiime_dada2_denoise_paired/
```

### 2-3. 빌드 확인

```bash
docker images | grep mcp-qiime
```

---

## 3. 단독 실행 및 테스트

MCP 서버는 **stdio(표준입출력)** 로 JSON-RPC 메시지를 주고받습니다.

```bash
# 도구 목록 조회
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  docker run --rm -i \
    -v $(pwd)/workspace:/app/workspace \
    mcp-qiime-tools-import:latest
```

---

## 4. MCP 클라이언트 등록

### 4-1. Claude Desktop

설정 파일 경로:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 4-2. Cursor

설정 파일 경로:
- `~/.cursor/mcp.json`

### 4-3. Claude Code (CLI)

설정 파일 경로:
- 프로젝트별: `.claude/settings.json`
- 전역: `~/.claude/settings.json`

---

## 5. 전체 등록 설정 (mcpServers)

아래 JSON을 위 설정 파일에 붙여넣으세요.
`$(pwd)/workspace` 부분을 **실제 데이터 경로**로 변경하세요.

```json
{
  "mcpServers": {
    "qiime-alignment-mafft": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-alignment-mafft:latest"]
    },
    "qiime-alignment-mask": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-alignment-mask:latest"]
    },
    "qiime-composition-add-pseudocount": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-composition-add-pseudocount:latest"]
    },
    "qiime-composition-ancom": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-composition-ancom:latest"]
    },
    "qiime-composition-ancombc": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-composition-ancombc:latest"]
    },
    "qiime-cutadapt-demux-paired": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-cutadapt-demux-paired:latest"]
    },
    "qiime-cutadapt-demux-single": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-cutadapt-demux-single:latest"]
    },
    "qiime-cutadapt-trim-paired": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-cutadapt-trim-paired:latest"]
    },
    "qiime-cutadapt-trim-single": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-cutadapt-trim-single:latest"]
    },
    "qiime-dada2-denoise-paired": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-dada2-denoise-paired:latest"]
    },
    "qiime-dada2-denoise-pyro": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-dada2-denoise-pyro:latest"]
    },
    "qiime-dada2-denoise-single": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-dada2-denoise-single:latest"]
    },
    "qiime-deblur-denoise-16S": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-deblur-denoise-16S:latest"]
    },
    "qiime-deblur-denoise-other": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-deblur-denoise-other:latest"]
    },
    "qiime-deblur-visualize-stats": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-deblur-visualize-stats:latest"]
    },
    "qiime-decontam": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-decontam:latest"]
    },
    "qiime-demux-emp-paired": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-demux-emp-paired:latest"]
    },
    "qiime-demux-emp-single": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-demux-emp-single:latest"]
    },
    "qiime-demux-filter-samples": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-demux-filter-samples:latest"]
    },
    "qiime-demux-summarize": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-demux-summarize:latest"]
    },
    "qiime-diversity-alpha": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-alpha:latest"]
    },
    "qiime-diversity-alpha-phylogenetic": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-alpha-phylogenetic:latest"]
    },
    "qiime-diversity-beta": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-beta:latest"]
    },
    "qiime-diversity-beta-phylogenetic": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-beta-phylogenetic:latest"]
    },
    "qiime-diversity-core-metrics-phylogenetic": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-core-metrics-phylogenetic:latest"]
    },
    "qiime-diversity-lib-faith-pd": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-lib-faith-pd:latest"]
    },
    "qiime-diversity-lib-shannon": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-lib-shannon:latest"]
    },
    "qiime-diversity-lib-unifrac": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-diversity-lib-unifrac:latest"]
    },
    "qiime-emperor-biplot": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-emperor-biplot:latest"]
    },
    "qiime-emperor-plot": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-emperor-plot:latest"]
    },
    "qiime-feature-classifier-classify-consensus-blast": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-classifier-classify-consensus-blast:latest"]
    },
    "qiime-feature-classifier-classify-consensus-vsearch": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-classifier-classify-consensus-vsearch:latest"]
    },
    "qiime-feature-classifier-classify-sklearn": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-classifier-classify-sklearn:latest"]
    },
    "qiime-feature-classifier-fit-classifier-naive-bayes": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-classifier-fit-classifier-naive-bayes:latest"]
    },
    "qiime-feature-table-filter-features": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-filter-features:latest"]
    },
    "qiime-feature-table-filter-samples": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-filter-samples:latest"]
    },
    "qiime-feature-table-group": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-group:latest"]
    },
    "qiime-feature-table-merge": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-merge:latest"]
    },
    "qiime-feature-table-merge-seqs": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-merge-seqs:latest"]
    },
    "qiime-feature-table-subsample": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-subsample:latest"]
    },
    "qiime-feature-table-summarize": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-feature-table-summarize:latest"]
    },
    "qiime-fragment-insertion-sepp": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-fragment-insertion-sepp:latest"]
    },
    "qiime-longitudinal-linear-mixed-effects": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-longitudinal-linear-mixed-effects:latest"]
    },
    "qiime-longitudinal-pairwise-differences": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-longitudinal-pairwise-differences:latest"]
    },
    "qiime-longitudinal-pairwise-distances": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-longitudinal-pairwise-distances:latest"]
    },
    "qiime-longitudinal-volatility": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-longitudinal-volatility:latest"]
    },
    "qiime-metadata-distance-matrix": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-metadata-distance-matrix:latest"]
    },
    "qiime-metadata-tabulate": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-metadata-tabulate:latest"]
    },
    "qiime-moshpit": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-moshpit:latest"]
    },
    "qiime-phylogeny-fasttree": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-phylogeny-fasttree:latest"]
    },
    "qiime-phylogeny-iqtree": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-phylogeny-iqtree:latest"]
    },
    "qiime-phylogeny-midpoint-root": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-phylogeny-midpoint-root:latest"]
    },
    "qiime-phylogeny-raxml": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-phylogeny-raxml:latest"]
    },
    "qiime-picrust2": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-picrust2:latest"]
    },
    "qiime-quality-filter-q-score": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-quality-filter-q-score:latest"]
    },
    "qiime-rescript": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-rescript:latest"]
    },
    "qiime-sample-classifier-classify-samples": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-sample-classifier-classify-samples:latest"]
    },
    "qiime-sample-classifier-heatmap": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-sample-classifier-heatmap:latest"]
    },
    "qiime-sample-classifier-regress-samples": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-sample-classifier-regress-samples:latest"]
    },
    "qiime-taxa-barplot": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-taxa-barplot:latest"]
    },
    "qiime-taxa-collapse": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-taxa-collapse:latest"]
    },
    "qiime-taxa-filter-seqs": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-taxa-filter-seqs:latest"]
    },
    "qiime-taxa-filter-table": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-taxa-filter-table:latest"]
    },
    "qiime-tools-cast-metadata": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-cast-metadata:latest"]
    },
    "qiime-tools-citations": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-citations:latest"]
    },
    "qiime-tools-export": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-export:latest"]
    },
    "qiime-tools-extract": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-extract:latest"]
    },
    "qiime-tools-import": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-import:latest"]
    },
    "qiime-tools-inspect-metadata": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-inspect-metadata:latest"]
    },
    "qiime-tools-peek": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-peek:latest"]
    },
    "qiime-tools-validate": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-validate:latest"]
    },
    "qiime-tools-view": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-tools-view:latest"]
    },
    "qiime-vsearch-cluster-features-closed-reference": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-vsearch-cluster-features-closed-reference:latest"]
    },
    "qiime-vsearch-cluster-features-de-novo": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-vsearch-cluster-features-de-novo:latest"]
    },
    "qiime-vsearch-cluster-features-open-reference": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-vsearch-cluster-features-open-reference:latest"]
    },
    "qiime-vsearch-dereplicate-sequences": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "$(pwd)/workspace:/app/workspace", "mcp-qiime-vsearch-dereplicate-sequences:latest"]
    }
  }
}
```

---

## 6. 도구 목록 (카테고리별 68종)

| 카테고리 | 도구 | 설명 |
|---|---|---|
| **Alignment** | `qiime-alignment-mafft` | MAFFT 다중 서열 정렬 |
| | `qiime-alignment-mask` | 정렬된 서열 마스킹 |
| **Composition** | `qiime-composition-add-pseudocount` | 유사카운트 추가 |
| | `qiime-composition-ancom` | ANCOM 차등 풍부도 분석 |
| | `qiime-composition-ancombc` | ANCOM-BC 차등 풍부도 분석 |
| **Cutadapt** | `qiime-cutadapt-demux-paired` | Paired-end 디멀티플렉싱 |
| | `qiime-cutadapt-demux-single` | Single-end 디멀티플렉싱 |
| | `qiime-cutadapt-trim-paired` | Paired-end 어댑터 트리밍 |
| | `qiime-cutadapt-trim-single` | Single-end 어댑터 트리밍 |
| **DADA2** | `qiime-dada2-denoise-paired` | Paired-end 노이즈 제거 |
| | `qiime-dada2-denoise-pyro` | Pyrosequencing 노이즈 제거 |
| | `qiime-dada2-denoise-single` | Single-end 노이즈 제거 |
| **Deblur** | `qiime-deblur-denoise-16S` | 16S 노이즈 제거 |
| | `qiime-deblur-denoise-other` | 기타 마커 노이즈 제거 |
| | `qiime-deblur-visualize-stats` | Deblur 통계 시각화 |
| **Decontam** | `qiime-decontam` | 오염 서열 제거 |
| **Demux** | `qiime-demux-emp-paired` | EMP Paired-end 디멀티플렉싱 |
| | `qiime-demux-emp-single` | EMP Single-end 디멀티플렉싱 |
| | `qiime-demux-filter-samples` | 디멀티플렉싱 샘플 필터링 |
| | `qiime-demux-summarize` | 디멀티플렉싱 요약 |
| **Diversity** | `qiime-diversity-alpha` | 알파 다양성 계산 |
| | `qiime-diversity-alpha-phylogenetic` | 계통 기반 알파 다양성 |
| | `qiime-diversity-beta` | 베타 다양성 계산 |
| | `qiime-diversity-beta-phylogenetic` | 계통 기반 베타 다양성 |
| | `qiime-diversity-core-metrics-phylogenetic` | 핵심 계통 다양성 지표 |
| **Diversity-lib** | `qiime-diversity-lib-faith-pd` | Faith PD 지수 |
| | `qiime-diversity-lib-shannon` | Shannon 지수 |
| | `qiime-diversity-lib-unifrac` | UniFrac 거리 |
| **Emperor** | `qiime-emperor-biplot` | Emperor 바이플롯 |
| | `qiime-emperor-plot` | Emperor PCoA 플롯 |
| **Feature Classifier** | `qiime-feature-classifier-classify-consensus-blast` | BLAST 합의 분류 |
| | `qiime-feature-classifier-classify-consensus-vsearch` | VSEARCH 합의 분류 |
| | `qiime-feature-classifier-classify-sklearn` | sklearn 기반 분류 |
| | `qiime-feature-classifier-fit-classifier-naive-bayes` | Naive Bayes 분류기 학습 |
| **Feature Table** | `qiime-feature-table-filter-features` | 피처 필터링 |
| | `qiime-feature-table-filter-samples` | 샘플 필터링 |
| | `qiime-feature-table-group` | 피처 테이블 그룹화 |
| | `qiime-feature-table-merge` | 피처 테이블 병합 |
| | `qiime-feature-table-merge-seqs` | 서열 병합 |
| | `qiime-feature-table-subsample` | 서브샘플링 |
| | `qiime-feature-table-summarize` | 피처 테이블 요약 |
| **Fragment Insertion** | `qiime-fragment-insertion-sepp` | SEPP 단편 삽입 |
| **Longitudinal** | `qiime-longitudinal-linear-mixed-effects` | 선형 혼합 효과 모델 |
| | `qiime-longitudinal-pairwise-differences` | 쌍별 차이 분석 |
| | `qiime-longitudinal-pairwise-distances` | 쌍별 거리 분석 |
| | `qiime-longitudinal-volatility` | 변동성 플롯 |
| **Metadata** | `qiime-metadata-distance-matrix` | 메타데이터 거리 행렬 |
| | `qiime-metadata-tabulate` | 메타데이터 테이블화 |
| **Moshpit** | `qiime-moshpit` | 메타게놈 분석 |
| **Phylogeny** | `qiime-phylogeny-fasttree` | FastTree 계통수 |
| | `qiime-phylogeny-iqtree` | IQ-TREE 계통수 |
| | `qiime-phylogeny-midpoint-root` | 중간점 루팅 |
| | `qiime-phylogeny-raxml` | RAxML 계통수 |
| **PICRUSt2** | `qiime-picrust2` | 기능 예측 |
| **Quality Filter** | `qiime-quality-filter-q-score` | Q-score 기반 품질 필터링 |
| **RESCRIPt** | `qiime-rescript` | 참조 DB 관리 |
| **Sample Classifier** | `qiime-sample-classifier-classify-samples` | 샘플 분류 |
| | `qiime-sample-classifier-heatmap` | 분류 히트맵 |
| | `qiime-sample-classifier-regress-samples` | 샘플 회귀 |
| **Taxa** | `qiime-taxa-barplot` | 분류 막대 그래프 |
| | `qiime-taxa-collapse` | 분류 수준 축소 |
| | `qiime-taxa-filter-seqs` | 분류 기반 서열 필터링 |
| | `qiime-taxa-filter-table` | 분류 기반 테이블 필터링 |
| **Tools** | `qiime-tools-cast-metadata` | 메타데이터 타입 변환 |
| | `qiime-tools-citations` | 인용 정보 조회 |
| | `qiime-tools-export` | 아티팩트 내보내기 |
| | `qiime-tools-extract` | 아티팩트 추출 |
| | `qiime-tools-import` | 데이터 가져오기 |
| | `qiime-tools-inspect-metadata` | 메타데이터 검사 |
| | `qiime-tools-peek` | 아티팩트 미리보기 |
| | `qiime-tools-validate` | 아티팩트 유효성 검사 |
| | `qiime-tools-view` | 시각화 보기 |
| **VSEARCH** | `qiime-vsearch-cluster-features-closed-reference` | Closed-reference 클러스터링 |
| | `qiime-vsearch-cluster-features-de-novo` | De novo 클러스터링 |
| | `qiime-vsearch-cluster-features-open-reference` | Open-reference 클러스터링 |
| | `qiime-vsearch-dereplicate-sequences` | 서열 중복 제거 |

---

## 7. 문제 해결

| 증상 | 해결 |
|---|---|
| `Cannot connect to the Docker daemon` | `sudo systemctl start docker` |
| `permission denied` | `sudo usermod -aG docker $USER && newgrp docker` |
| 이미지 빌드 실패 (conda timeout) | `docker build --network=host -t <이미지명> <경로>` |
| MCP 서버 연결 안 됨 | `docker run --rm -i <이미지>` 로 직접 실행 후 JSON-RPC 테스트 |
| 데이터 파일을 못 찾음 | `-v` 마운트 경로가 정확한지 확인 |
