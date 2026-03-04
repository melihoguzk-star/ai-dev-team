#!/bin/bash
# ============================================================================
# cleanup-worktree.sh — Git worktree'yi temizler
# ============================================================================
#
# Kullanım:
#   ./cleanup-worktree.sh <faz-no> <feature-name>
#
# Örnekler:
#   ./cleanup-worktree.sh 3 ba-document
#   ./cleanup-worktree.sh 6 backend-api
#
# İşlev:
#   1. Git worktree'yi kaldırır (git worktree remove)
#   2. Branch'i silmez (merge sonrası elle silinecek)
#   3. Temizlik sonucunu loglar
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
WORKTREE_BASE="$PROJECT_ROOT/worktrees"

# ---- Argüman kontrolü ----
if [ $# -ne 2 ]; then
    echo -e "${RED}Hata: Eksik argüman${NC}"
    echo ""
    echo "Kullanım: $0 <faz-no> <feature-name>"
    echo "Örnek:    $0 3 ba-document"
    exit 1
fi

FAZ_NO="$1"
FEATURE="$2"
BRANCH_NAME="agent/faz-${FAZ_NO}/${FEATURE}"
WORKTREE_DIR="${WORKTREE_BASE}/faz-${FAZ_NO}-${FEATURE}"

# ---- Proje dizini kontrolü ----
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${RED}Hata: $PROJECT_ROOT bir git repository değil${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# ---- Worktree mevcut mu? ----
if [ ! -d "$WORKTREE_DIR" ]; then
    echo -e "${YELLOW}Uyarı: Worktree dizini bulunamadı: ${WORKTREE_DIR}${NC}"
    echo ""
    echo "Mevcut worktree'ler:"
    git worktree list
    exit 1
fi

# ---- Worktree'de commit edilmemiş değişiklik var mı? ----
cd "$WORKTREE_DIR"
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Uyarı: Worktree'de commit edilmemiş değişiklikler var!${NC}"
    echo ""
    git status --short
    echo ""
    read -p "Yine de silmek istiyor musunuz? (e/h): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ee]$ ]]; then
        echo -e "${YELLOW}İptal edildi.${NC}"
        exit 0
    fi
fi

# ---- Ana dizine dön ----
cd "$PROJECT_ROOT"

# ---- Worktree'yi kaldır ----
echo -e "${CYAN}Worktree kaldırılıyor: ${WORKTREE_DIR}${NC}"
git worktree remove "$WORKTREE_DIR" --force

# ---- Worktree dizini hala varsa sil ----
if [ -d "$WORKTREE_DIR" ]; then
    rm -rf "$WORKTREE_DIR"
fi

# ---- Prune ----
git worktree prune

# ---- Başarı mesajı ----
echo ""
echo -e "${GREEN}✅ Worktree temizlendi!${NC}"
echo -e "   Kaldırılan: ${CYAN}${WORKTREE_DIR}${NC}"
echo -e "   Branch:     ${CYAN}${BRANCH_NAME}${NC} (korundu — merge sonrası elle silin)"
echo ""
echo -e "Branch'i silmek için:"
echo -e "   git branch -d ${BRANCH_NAME}     # merge edildiyse"
echo -e "   git branch -D ${BRANCH_NAME}     # zorla sil"
