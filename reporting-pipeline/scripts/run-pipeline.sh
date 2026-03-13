#!/bin/bash
# ============================================================================
# run-pipeline.sh — Reporting Pipeline Çalıştırıcı
# ============================================================================
#
# Kullanım:
#   ./run-pipeline.sh                           # Tüm pipeline (varsayılan hafta)
#   ./run-pipeline.sh --week "2026-03-02"       # Belirli hafta
#   ./run-pipeline.sh --phase 1 --parallel      # Sadece Faz 1 (paralel)
#   ./run-pipeline.sh --phase 3                 # Sadece Faz 3
#   ./run-pipeline.sh --dry-run                 # Test modu (API çağrısı yapmaz)
#
# ============================================================================
set -euo pipefail

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Proje dizini
PIPELINE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PIPELINE_ROOT/logs"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Varsayılan parametreler
WEEK_START=""
PHASE=""
PARALLEL=false
DRY_RUN=false

# ---- Argüman parse ----
while [[ $# -gt 0 ]]; do
    case $1 in
        --week)
            WEEK_START="$2"
            shift 2
            ;;
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Kullanım: $0 [--week YYYY-MM-DD] [--phase N] [--parallel] [--dry-run]"
            exit 0
            ;;
        *)
            echo -e "${RED}Bilinmeyen parametre: $1${NC}"
            exit 1
            ;;
    esac
done

# Hafta başlangıcı hesapla (varsayılan: geçen Pazartesi)
if [ -z "$WEEK_START" ]; then
    # Geçen Pazartesi'yi bul
    if [[ "$(uname)" == "Darwin" ]]; then
        WEEK_START=$(date -v-monday "+%Y-%m-%d")
    else
        WEEK_START=$(date -d "last monday" "+%Y-%m-%d")
    fi
fi

# Log dizini
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pipeline-${TIMESTAMP}.log"

# ---- Banner ----
echo "" | tee -a "$LOG_FILE"
echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
echo -e "${BOLD}║   📊 SunExpress Reporting Pipeline                   ║${NC}" | tee -a "$LOG_FILE"
echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${CYAN}Hafta:${NC}     $WEEK_START" | tee -a "$LOG_FILE"
echo -e "${CYAN}Faz:${NC}       ${PHASE:-tümü}" | tee -a "$LOG_FILE"
echo -e "${CYAN}Paralel:${NC}   $PARALLEL" | tee -a "$LOG_FILE"
echo -e "${CYAN}Dry Run:${NC}   $DRY_RUN" | tee -a "$LOG_FILE"
echo -e "${CYAN}Log:${NC}       $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ---- Credential kontrolü ----
CRED_FILE="$PIPELINE_ROOT/config/credentials.json"
if [ ! -f "$CRED_FILE" ] && [ "$DRY_RUN" = false ]; then
    echo -e "${RED}HATA: credentials.json bulunamadı!${NC}" | tee -a "$LOG_FILE"
    echo -e "Şablon: ${CYAN}$PIPELINE_ROOT/config/credentials.example.json${NC}" | tee -a "$LOG_FILE"
    echo -e "Kopyala ve düzenle: ${CYAN}cp credentials.example.json credentials.json${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

# ---- Claude CLI kontrolü ----
if ! command -v claude &>/dev/null; then
    echo -e "${RED}HATA: claude CLI kurulu değil veya PATH'te değil${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

# ---- Faz çalıştırma fonksiyonu ----
run_phase() {
    local phase_num=$1
    local phase_name=$2
    local prompt=$3
    
    echo -e "${CYAN}━━━ Faz $phase_num: $phase_name ━━━${NC}" | tee -a "$LOG_FILE"
    echo -e "Başlangıç: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] Prompt: ${prompt:0:100}...${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}✅ Faz $phase_num (dry run) tamamlandı${NC}" | tee -a "$LOG_FILE"
        return 0
    fi
    
    local phase_log="$LOG_DIR/phase-${phase_num}-${TIMESTAMP}.log"
    
    if claude --print "$prompt" 2>&1 | tee -a "$phase_log"; then
        echo -e "${GREEN}✅ Faz $phase_num tamamlandı${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}❌ Faz $phase_num başarısız${NC}" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo -e "Bitiş: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# ---- Prompt'lar ----
PROMPT_1A="data-collector subagent'ını kullan. App Store Connect API'den SunExpress iOS uygulamasının $WEEK_START haftası metriklerini topla. Çıktıyı ~/ai-dev-team/reporting-pipeline/data/raw/ dizinine kaydet."

PROMPT_1B="data-collector subagent'ını kullan. Google Play Console API'den SunExpress Android uygulamasının $WEEK_START haftası metriklerini topla. Çıktıyı ~/ai-dev-team/reporting-pipeline/data/raw/ dizinine kaydet."

PROMPT_1C="data-collector subagent'ını kullan. Firebase Crashlytics'ten SunExpress iOS ve Android crash verilerini $WEEK_START haftası için topla. Çıktıyı ~/ai-dev-team/reporting-pipeline/data/raw/ dizinine kaydet."

PROMPT_2="data-processor subagent'ını kullan. ~/ai-dev-team/reporting-pipeline/data/raw/ dizinindeki tüm JSON dosyalarını oku, normalize et ve birleştir. Çıktıyı ~/ai-dev-team/reporting-pipeline/data/processed/ dizinine kaydet."

PROMPT_3="trend-analyzer subagent'ını kullan. ~/ai-dev-team/reporting-pipeline/data/processed/ dizinindeki CSV dosyalarını oku. Trend analizi, anomali tespiti ve insight üretimi yap. Çıktıyı aynı dizine JSON olarak kaydet."

PROMPT_4="report-reviewer subagent'ını kullan. ~/ai-dev-team/reporting-pipeline/data/ dizinini uçtan uca doğrula. Raw vs processed cross-check yap. Kalite raporunu ~/ai-dev-team/reporting-pipeline/reports/$WEEK_START/quality-report.md olarak kaydet."

# ---- Pipeline çalıştır ----

# Tek faz modu
if [ -n "$PHASE" ]; then
    case $PHASE in
        1)
            if [ "$PARALLEL" = true ]; then
                echo -e "${CYAN}Faz 1: Paralel veri toplama başlatılıyor...${NC}" | tee -a "$LOG_FILE"
                
                if command -v tmux &>/dev/null; then
                    "$PIPELINE_ROOT/../scripts/parallel-run.sh" "$PROMPT_1A" "$PROMPT_1B"
                    # 1c ayrı çalıştır
                    run_phase "1c" "Crashlytics Toplama" "$PROMPT_1C"
                else
                    echo -e "${YELLOW}tmux yok — sıralı çalıştırılıyor${NC}" | tee -a "$LOG_FILE"
                    run_phase "1a" "iOS Veri Toplama" "$PROMPT_1A"
                    run_phase "1b" "Android Veri Toplama" "$PROMPT_1B"
                    run_phase "1c" "Crashlytics Toplama" "$PROMPT_1C"
                fi
            else
                run_phase "1a" "iOS Veri Toplama" "$PROMPT_1A"
                run_phase "1b" "Android Veri Toplama" "$PROMPT_1B"
                run_phase "1c" "Crashlytics Toplama" "$PROMPT_1C"
            fi
            ;;
        2) run_phase 2 "Veri İşleme" "$PROMPT_2" ;;
        3) run_phase 3 "Trend Analizi" "$PROMPT_3" ;;
        4) run_phase 4 "Kalite Kontrol" "$PROMPT_4" ;;
        *)
            echo -e "${RED}Geçersiz faz: $PHASE (1-4 arası olmalı)${NC}"
            exit 1
            ;;
    esac
    exit 0
fi

# Tam pipeline modu
echo -e "${BOLD}Tam pipeline başlatılıyor...${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Faz 1: Veri Toplama
if [ "$PARALLEL" = true ] && command -v tmux &>/dev/null; then
    echo -e "${CYAN}Faz 1: Paralel veri toplama...${NC}" | tee -a "$LOG_FILE"
    "$PIPELINE_ROOT/../scripts/parallel-run.sh" "$PROMPT_1A" "$PROMPT_1B"
    run_phase "1c" "Crashlytics Toplama" "$PROMPT_1C"
else
    run_phase "1a" "iOS Veri Toplama" "$PROMPT_1A"
    run_phase "1b" "Android Veri Toplama" "$PROMPT_1B"
    run_phase "1c" "Crashlytics Toplama" "$PROMPT_1C"
fi

# Faz 2: Veri İşleme
run_phase 2 "Veri İşleme" "$PROMPT_2"

# Faz 3: Trend Analizi
run_phase 3 "Trend Analizi" "$PROMPT_3"

# Faz 4: Kalite Kontrol
mkdir -p "$PIPELINE_ROOT/reports/$WEEK_START"
run_phase 4 "Kalite Kontrol" "$PROMPT_4"

# ---- Sonuç ----
echo "" | tee -a "$LOG_FILE"
echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
echo -e "${BOLD}║   ✅ Pipeline tamamlandı                             ║${NC}" | tee -a "$LOG_FILE"
echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${CYAN}Hafta:${NC}     $WEEK_START" | tee -a "$LOG_FILE"
echo -e "${CYAN}Veriler:${NC}   $PIPELINE_ROOT/data/processed/" | tee -a "$LOG_FILE"
echo -e "${CYAN}Rapor:${NC}     $PIPELINE_ROOT/reports/$WEEK_START/" | tee -a "$LOG_FILE"
echo -e "${CYAN}Log:${NC}       $LOG_FILE" | tee -a "$LOG_FILE"
