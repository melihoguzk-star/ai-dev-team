#!/bin/bash
# ============================================================================
# pre-merge-check.sh — Merge öncesi conflict ve değişiklik kontrolü
# ============================================================================
#
# Kullanım:
#   ./pre-merge-check.sh <branch-name>
#
# Örnekler:
#   ./pre-merge-check.sh agent/faz-3/ba-document
#   ./pre-merge-check.sh agent/faz-6/backend-api
#
# İşlev:
#   1. Branch'te kaç dosya değişmiş kontrol eder
#   2. develop ile conflict var mı test eder (dry-run merge)
#   3. Conflict varsa dosyaları listeler
#   4. Sonucu rapor eder
#
# Not: Bu script develop branch'e merge YAPMAZ, sadece kontrol eder.
#
# ============================================================================
set -euo pipefail

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Proje kök dizini
PROJECT_ROOT="$HOME/ai-dev-team"

# ---- Argüman kontrolü ----
if [ $# -ne 1 ]; then
    echo -e "${RED}Hata: Eksik argüman${NC}"
    echo ""
    echo "Kullanım: $0 <branch-name>"
    echo "Örnek:    $0 agent/faz-3/ba-document"
    exit 1
fi

BRANCH_NAME="$1"

# ---- Proje dizini kontrolü ----
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${RED}Hata: $PROJECT_ROOT bir git repository değil${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# ---- Branch mevcut mu? ----
if ! git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo -e "${RED}Hata: Branch bulunamadı: ${BRANCH_NAME}${NC}"
    echo ""
    echo "Mevcut branch'ler:"
    git branch --list 'agent/*' 'review/*' 'merge/*' 2>/dev/null || git branch
    exit 1
fi

echo "============================================"
echo -e " ${CYAN}Pre-Merge Check: ${BRANCH_NAME}${NC}"
echo "============================================"
echo ""

# ---- 1. Değişen dosya sayısı ----
echo -e "${CYAN}📊 Değişen Dosyalar (develop ile karşılaştırma):${NC}"
echo ""

CHANGED_FILES=$(git diff --name-only develop..."${BRANCH_NAME}" 2>/dev/null || true)
CHANGED_COUNT=0

if [ -n "$CHANGED_FILES" ]; then
    CHANGED_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
    
    # Değişiklik tiplerini say
    ADDED=$(git diff --diff-filter=A --name-only develop..."${BRANCH_NAME}" 2>/dev/null | wc -l | tr -d ' ')
    MODIFIED=$(git diff --diff-filter=M --name-only develop..."${BRANCH_NAME}" 2>/dev/null | wc -l | tr -d ' ')
    DELETED=$(git diff --diff-filter=D --name-only develop..."${BRANCH_NAME}" 2>/dev/null | wc -l | tr -d ' ')
    
    echo -e "   Toplam:    ${CHANGED_COUNT} dosya"
    echo -e "   Eklenen:   ${GREEN}+${ADDED}${NC}"
    echo -e "   Değişen:   ${YELLOW}~${MODIFIED}${NC}"
    echo -e "   Silinen:   ${RED}-${DELETED}${NC}"
    echo ""
    
    # Dosya listesi
    echo -e "   Dosyalar:"
    echo "$CHANGED_FILES" | while read -r file; do
        echo -e "   • $file"
    done
else
    echo -e "   ${YELLOW}Hiç değişiklik yok.${NC}"
fi

echo ""

# ---- 2. Commit farkı ----
AHEAD=$(git rev-list --count develop.."${BRANCH_NAME}" 2>/dev/null || echo "0")
BEHIND=$(git rev-list --count "${BRANCH_NAME}"..develop 2>/dev/null || echo "0")

echo -e "${CYAN}📈 Commit Durumu:${NC}"
echo -e "   develop'un ${GREEN}${AHEAD}${NC} commit ilerisinde"
echo -e "   develop'un ${YELLOW}${BEHIND}${NC} commit gerisinde"
echo ""

# ---- 3. Conflict kontrolü (dry-run merge) ----
echo -e "${CYAN}🔍 Conflict Kontrolü:${NC}"
echo ""

# Mevcut branch'i kaydet
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Geçici stash (dirty working tree varsa)
STASHED=false
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    git stash push -m "pre-merge-check temp stash" --quiet
    STASHED=true
fi

# develop'a geçip dry-run merge dene
git checkout develop --quiet 2>/dev/null

MERGE_RESULT=0
CONFLICT_FILES=""

if git merge --no-commit --no-ff "${BRANCH_NAME}" >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Conflict yok — temiz merge yapılabilir${NC}"
else
    MERGE_RESULT=1
    CONFLICT_FILES=$(git diff --name-only --diff-filter=U 2>/dev/null || true)
    echo -e "   ${RED}❌ CONFLICT TESPİT EDİLDİ!${NC}"
    echo ""
    if [ -n "$CONFLICT_FILES" ]; then
        echo -e "   Conflict olan dosyalar:"
        echo "$CONFLICT_FILES" | while read -r file; do
            echo -e "   ${RED}✗${NC} $file"
        done
    fi
fi

# Merge'i geri al
git merge --abort 2>/dev/null || true
git checkout "$CURRENT_BRANCH" --quiet 2>/dev/null

# Stash'i geri al
if [ "$STASHED" = true ]; then
    git stash pop --quiet 2>/dev/null || true
fi

echo ""

# ---- 4. Özet ----
echo "============================================"
if [ "$MERGE_RESULT" -eq 0 ] && [ "$CHANGED_COUNT" -gt 0 ]; then
    echo -e " ${GREEN}✅ MERGE HAZIR${NC}"
    echo -e " ${CHANGED_COUNT} dosya değişmiş, conflict yok."
    echo ""
    echo -e " Merge komutu:"
    echo -e "   git checkout develop"
    echo -e "   git merge --no-ff ${BRANCH_NAME}"
elif [ "$MERGE_RESULT" -ne 0 ]; then
    echo -e " ${RED}❌ CONFLICT VAR — merge öncesi çözülmeli${NC}"
    echo ""
    echo -e " Çözüm:"
    echo -e "   git checkout ${BRANCH_NAME}"
    echo -e "   git merge develop"
    echo -e "   # conflict'leri çöz"
    echo -e "   git add -A && git commit"
else
    echo -e " ${YELLOW}⚠️  Değişiklik yok — merge gereksiz${NC}"
fi
echo "============================================"
