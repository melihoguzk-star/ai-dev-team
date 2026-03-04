#!/bin/bash
# ============================================================================
# pipeline-status.sh — Pipeline durumunu gösterir
# ============================================================================
#
# Kullanım:
#   ./pipeline-status.sh
#
# İşlev:
#   1. Aktif git worktree'leri listeler
#   2. Her branch'in son commit'ini gösterir
#   3. Pipeline status.json dosyasını okunabilir formatta gösterir
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

# Proje kök dizini
PROJECT_ROOT="$HOME/ai-dev-team"

# ---- Proje dizini kontrolü ----
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${RED}Hata: $PROJECT_ROOT bir git repository değil${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║        🚀 AI Dev Team Pipeline Durumu            ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ---- 1. Git Durum ----
echo -e "${CYAN}📌 Git Durum:${NC}"
echo -e "   Aktif branch: ${GREEN}$(git rev-parse --abbrev-ref HEAD)${NC}"
echo -e "   Son commit:   $(git log -1 --format='%h %s' 2>/dev/null)"
echo ""

# ---- 2. Branch'ler ----
echo -e "${CYAN}🌿 Branch'ler:${NC}"
echo ""

# Main
MAIN_COMMIT=$(git log main -1 --format='%h %s' 2>/dev/null || echo "yok")
echo -e "   ${GREEN}main${NC}      ${MAIN_COMMIT}"

# Develop
DEV_COMMIT=$(git log develop -1 --format='%h %s' 2>/dev/null || echo "yok")
echo -e "   ${GREEN}develop${NC}   ${DEV_COMMIT}"

# Agent branch'leri
AGENT_BRANCHES=$(git branch --list 'agent/*' 2>/dev/null | sed 's/^[ *]*//')
if [ -n "$AGENT_BRANCHES" ]; then
    echo ""
    echo -e "   ${YELLOW}Agent branch'leri:${NC}"
    while IFS= read -r branch; do
        COMMIT=$(git log "$branch" -1 --format='%h %s (%cr)' 2>/dev/null || echo "?")
        echo -e "   ${YELLOW}→${NC} $branch"
        echo -e "     ${COMMIT}"
    done <<< "$AGENT_BRANCHES"
fi

# Review branch'leri
REVIEW_BRANCHES=$(git branch --list 'review/*' 2>/dev/null | sed 's/^[ *]*//')
if [ -n "$REVIEW_BRANCHES" ]; then
    echo ""
    echo -e "   ${CYAN}Review branch'leri:${NC}"
    while IFS= read -r branch; do
        COMMIT=$(git log "$branch" -1 --format='%h %s (%cr)' 2>/dev/null || echo "?")
        echo -e "   ${CYAN}→${NC} $branch"
        echo -e "     ${COMMIT}"
    done <<< "$REVIEW_BRANCHES"
fi

echo ""

# ---- 3. Worktree'ler ----
echo -e "${CYAN}📂 Aktif Worktree'ler:${NC}"
echo ""

WORKTREES=$(git worktree list 2>/dev/null)
WORKTREE_COUNT=$(echo "$WORKTREES" | wc -l | tr -d ' ')

if [ "$WORKTREE_COUNT" -le 1 ]; then
    echo -e "   ${YELLOW}Aktif worktree yok (sadece ana dizin)${NC}"
else
    echo "$WORKTREES" | while IFS= read -r line; do
        echo -e "   $line"
    done
fi

echo ""

# ---- 4. Pipeline Status JSON ----
echo -e "${CYAN}📊 Pipeline Status:${NC}"
echo ""

# Status dosyasını ara (birkaç olası konum)
STATUS_FILE=""
for path in \
    "$PROJECT_ROOT/pilot-test/pipeline/status.json" \
    "$PROJECT_ROOT/pipeline/status.json" \
    ; do
    if [ -f "$path" ]; then
        STATUS_FILE="$path"
        break
    fi
done

if [ -n "$STATUS_FILE" ]; then
    echo -e "   Dosya: ${STATUS_FILE}"
    echo ""

    # JSON'u okunabilir formatta göster
    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys

with open('${STATUS_FILE}') as f:
    data = json.load(f)

print(f'   Proje URL:  {data.get(\"project_url\", \"?\")}')
print(f'   Durum:      {data.get(\"status\", \"?\")}')
print(f'   Aktif Faz:  {data.get(\"current_phase\", \"?\")}')
print(f'   Tamamlanan: {data.get(\"completed_phases\", [])}')
print(f'   Başarısız:  {data.get(\"failed_phases\", [])}')
print(f'   Atlanan:    {data.get(\"skipped_phases\", [])}')
print()

phases = data.get('phases', {})
if phases:
    print('   ┌─────┬──────────────────┬────────────────┬───────┬───────┐')
    print('   │ Faz │ Ad               │ Durum          │ Süre  │ Skor  │')
    print('   ├─────┼──────────────────┼────────────────┼───────┼───────┤')
    for key in sorted(phases.keys()):
        p = phases[key]
        name = p.get('name', '?')[:16].ljust(16)
        status = p.get('status', '?')[:14].ljust(14)
        dur = str(p.get('duration_minutes', '-')).ljust(5)
        score = str(p.get('quality_score', '-')).ljust(5)
        print(f'   │  {key}  │ {name} │ {status} │ {dur} │ {score} │')
    print('   └─────┴──────────────────┴────────────────┴───────┴───────┘')
" 2>/dev/null || cat "$STATUS_FILE"
    else
        cat "$STATUS_FILE"
    fi
else
    echo -e "   ${YELLOW}Pipeline status dosyası bulunamadı.${NC}"
    echo -e "   Beklenen konumlar:"
    echo -e "   • ~/ai-dev-team/pilot-test/pipeline/status.json"
    echo -e "   • ~/ai-dev-team/pipeline/status.json"
fi

echo ""

# ---- 5. Karar Logu ----
DECISIONS_FILE=""
for path in \
    "$PROJECT_ROOT/pilot-test/pipeline/decisions.json" \
    "$PROJECT_ROOT/pipeline/decisions.json" \
    ; do
    if [ -f "$path" ]; then
        DECISIONS_FILE="$path"
        break
    fi
done

if [ -n "$DECISIONS_FILE" ]; then
    if command -v python3 &>/dev/null; then
        DECISION_COUNT=$(python3 -c "
import json
with open('${DECISIONS_FILE}') as f:
    data = json.load(f)
print(len(data.get('decisions', [])))
" 2>/dev/null || echo "?")
        echo -e "${CYAN}📝 Karar Logu:${NC} ${DECISION_COUNT} karar kayıtlı"
        echo -e "   Dosya: ${DECISIONS_FILE}"
    fi
fi

echo ""
echo -e "${BOLD}══════════════════════════════════════════════════${NC}"
