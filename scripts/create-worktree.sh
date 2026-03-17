#!/bin/bash
# ============================================================================
# create-worktree.sh — Faz çalışması için git worktree oluşturur
# ============================================================================
#
# Kullanım:
#   ./create-worktree.sh <faz-no> <feature-name>
#
# Örnekler:
#   ./create-worktree.sh 3 ba-document
#   ./create-worktree.sh 6 backend-api
#
# İşlev:
#   1. develop branch'inden yeni branch oluşturur: agent/faz-<no>/<feature>
#   2. Git worktree oluşturur: ~/ai-dev-team/worktrees/faz-<no>-<feature>/
#   3. Worktree'ye gerekli dizin yapısını kopyalar
#   4. Başarılı olursa log mesajı yazdırır
#
# ============================================================================
set -euo pipefail

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# ---- Branch zaten var mı? ----
cd "$PROJECT_ROOT"
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo -e "${YELLOW}Uyarı: Branch '${BRANCH_NAME}' zaten mevcut${NC}"
    echo -e "${YELLOW}Mevcut branch üzerinden worktree oluşturuluyor...${NC}"
else
    # develop'tan yeni branch oluştur
    echo -e "${CYAN}Branch oluşturuluyor: ${BRANCH_NAME}${NC}"
    git branch "${BRANCH_NAME}" develop
fi

# ---- Worktree zaten var mı? ----
if [ -d "$WORKTREE_DIR" ]; then
    echo -e "${RED}Hata: Worktree dizini zaten mevcut: ${WORKTREE_DIR}${NC}"
    echo "Önce cleanup-worktree.sh çalıştırın."
    exit 1
fi

# ---- Worktree oluştur ----
echo -e "${CYAN}Worktree oluşturuluyor: ${WORKTREE_DIR}${NC}"
mkdir -p "$WORKTREE_BASE"
git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"

# ---- Gerekli dizin yapısını oluştur ----
echo -e "${CYAN}Dizin yapısı oluşturuluyor...${NC}"
mkdir -p "$WORKTREE_DIR/analysis"
mkdir -p "$WORKTREE_DIR/docs"
mkdir -p "$WORKTREE_DIR/design/components"
mkdir -p "$WORKTREE_DIR/backend"
mkdir -p "$WORKTREE_DIR/ios"
mkdir -p "$WORKTREE_DIR/tests/backend"
mkdir -p "$WORKTREE_DIR/tests/ios"
mkdir -p "$WORKTREE_DIR/infra"

# ---- Pipeline dosyalarını kopyala (varsa) ----
if [ -d "$PROJECT_ROOT/pipeline" ]; then
    cp -r "$PROJECT_ROOT/pipeline" "$WORKTREE_DIR/pipeline" 2>/dev/null || true
fi

# ---- Başarı mesajı ----
echo ""
echo -e "${GREEN}✅ Worktree oluşturuldu!${NC}"
echo -e "   Branch:   ${CYAN}${BRANCH_NAME}${NC}"
echo -e "   Dizin:    ${CYAN}${WORKTREE_DIR}${NC}"
echo -e "   Kaynak:   develop ($(git rev-parse --short develop))"
echo ""
echo -e "Kullanım:"
echo -e "   cd ${WORKTREE_DIR}"
echo -e "   # ... çalışmalarınızı yapın ..."
echo -e "   git add -A && git commit -m 'Faz ${FAZ_NO}: ${FEATURE}'"
