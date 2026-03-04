#!/bin/bash
# ============================================================================
# curate-memory.sh — Agent memory dosyalarını temizler ve yönetir
# ============================================================================
#
# Kullanım:
#   ./curate-memory.sh
#
# İşlev:
#   1. ~/.memory/ dizinindeki tüm .md dosyalarını tarar
#   2. 50 satırı aşanları tespit eder
#   3. Eski versiyonu arşivler, dosyayı kırpar
#   4. CLAUDE.md dosyasını kontrol eder (200 satır limiti)
#   5. Rapor üretir
#
# ============================================================================
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PROJECT_ROOT="$HOME/ai-dev-team"
MEMORY_DIR="$PROJECT_ROOT/.memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"
CLAUDE_FILE="$PROJECT_ROOT/CLAUDE.md"
MEMORY_LIMIT=50
CLAUDE_LIMIT=200
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║      🧹 Memory Curation Tool             ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# Arşiv dizini oluştur
mkdir -p "$ARCHIVE_DIR"

TOTAL_FILES=0
CURATED_FILES=0
TOTAL_LINES_BEFORE=0
TOTAL_LINES_AFTER=0

# ---- 1. Agent Memory Dosyalarını Tara ----
echo -e "${CYAN}📂 Agent Memory Dosyaları:${NC}"
echo ""

for mf in "$MEMORY_DIR"/*.md; do
    [ ! -f "$mf" ] && continue
    basename_f=$(basename "$mf")

    # shared-context ve sync-report atla
    [[ "$basename_f" == "shared-context.md" ]] && continue
    [[ "$basename_f" =~ ^sync-report ]] && continue

    TOTAL_FILES=$((TOTAL_FILES + 1))
    LINE_COUNT=$(wc -l < "$mf" | tr -d ' ')
    TOTAL_LINES_BEFORE=$((TOTAL_LINES_BEFORE + LINE_COUNT))

    if [ "$LINE_COUNT" -gt "$MEMORY_LIMIT" ]; then
        agent_name=$(basename "$mf" .md)
        echo -e "  ${YELLOW}⚠️  ${agent_name}${NC} — ${LINE_COUNT} satır (limit: ${MEMORY_LIMIT})"

        # Arşivle
        archive_name="${agent_name}-${TIMESTAMP}.md"
        cp "$mf" "$ARCHIVE_DIR/$archive_name"
        echo -e "     Arşivlendi: ${CYAN}archive/${archive_name}${NC}"

        # Dosyayı kırp: başlık + son 40 satır (en güncel bilgiler)
        # Strateji: İlk 5 satır (başlık) + son 40 satır (güncel) = 45 satır
        HEADER=$(head -5 "$mf")
        RECENT=$(tail -40 "$mf")

        cat > "$mf" << TRIMEOF
${HEADER}

<!-- Otomatik kırpıldı: ${TIMESTAMP} | Orijinal: ${LINE_COUNT} satır | Arşiv: archive/${archive_name} -->

${RECENT}
TRIMEOF

        NEW_LINES=$(wc -l < "$mf" | tr -d ' ')
        TOTAL_LINES_AFTER=$((TOTAL_LINES_AFTER + NEW_LINES))
        CURATED_FILES=$((CURATED_FILES + 1))
        REDUCED=$((LINE_COUNT - NEW_LINES))
        echo -e "     Kırpıldı: ${GREEN}${LINE_COUNT} → ${NEW_LINES} satır (−${REDUCED})${NC}"
    else
        TOTAL_LINES_AFTER=$((TOTAL_LINES_AFTER + LINE_COUNT))
        echo -e "  ${GREEN}✅ $(basename "$mf" .md)${NC} — ${LINE_COUNT} satır"
    fi
done

if [ "$TOTAL_FILES" -eq 0 ]; then
    echo -e "  ${YELLOW}Henüz agent memory dosyası yok.${NC}"
fi

echo ""

# ---- 2. shared-context.md Kontrol ----
echo -e "${CYAN}📋 shared-context.md:${NC}"
if [ -f "$MEMORY_DIR/shared-context.md" ]; then
    SC_LINES=$(wc -l < "$MEMORY_DIR/shared-context.md" | tr -d ' ')
    if [ "$SC_LINES" -gt 100 ]; then
        echo -e "  ${YELLOW}⚠️  ${SC_LINES} satır — biraz uzun, gözden geçirmelisiniz${NC}"
    else
        echo -e "  ${GREEN}✅ ${SC_LINES} satır${NC}"
    fi
else
    echo -e "  ${YELLOW}Dosya yok${NC}"
fi
echo ""

# ---- 3. CLAUDE.md Kontrol ----
echo -e "${CYAN}📄 CLAUDE.md:${NC}"

if [ -f "$CLAUDE_FILE" ]; then
    CL_LINES=$(wc -l < "$CLAUDE_FILE" | tr -d ' ')
    if [ "$CL_LINES" -gt "$CLAUDE_LIMIT" ]; then
        echo -e "  ${YELLOW}⚠️  ${CL_LINES} satır (limit: ${CLAUDE_LIMIT})${NC}"

        # Arşivle
        cp "$CLAUDE_FILE" "$ARCHIVE_DIR/CLAUDE-${TIMESTAMP}.md"
        echo -e "     Arşivlendi: ${CYAN}archive/CLAUDE-${TIMESTAMP}.md${NC}"

        # Kırp: ilk 10 satır (başlık) + son 180 satır
        HEADER=$(head -10 "$CLAUDE_FILE")
        RECENT=$(tail -180 "$CLAUDE_FILE")

        cat > "$CLAUDE_FILE" << TRIMEOF
${HEADER}

<!-- Otomatik kırpıldı: ${TIMESTAMP} | Orijinal: ${CL_LINES} satır -->

${RECENT}
TRIMEOF

        NEW_CL=$(wc -l < "$CLAUDE_FILE" | tr -d ' ')
        echo -e "     Kırpıldı: ${GREEN}${CL_LINES} → ${NEW_CL} satır${NC}"
    else
        echo -e "  ${GREEN}✅ ${CL_LINES} satır${NC}"
    fi
else
    echo -e "  ${YELLOW}CLAUDE.md bulunamadı — oluşturulacak${NC}"
    echo -e "  ${RED}Oluşturma işlemi bu scriptin kapsamı dışında.${NC}"
    echo -e "  ${RED}Proje kökünde CLAUDE.md dosyasını manuel oluşturun.${NC}"
fi

echo ""

# ---- 4. Arşiv Temizliği ----
echo -e "${CYAN}🗄️  Arşiv:${NC}"
ARCHIVE_COUNT=$(find "$ARCHIVE_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)
echo -e "  Dosya: ${ARCHIVE_COUNT}"
echo -e "  Boyut: ${ARCHIVE_SIZE}"

# 30 günden eski arşivleri temizle
OLD_ARCHIVES=$(find "$ARCHIVE_DIR" -name "*.md" -mtime +30 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_ARCHIVES" -gt 0 ]; then
    echo -e "  ${YELLOW}30 günden eski ${OLD_ARCHIVES} arşiv dosyası silinebilir${NC}"
    echo -e "  Silmek için: ${CYAN}find $ARCHIVE_DIR -name '*.md' -mtime +30 -delete${NC}"
fi

echo ""

# ---- 5. Özet ----
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo -e "  Memory dosyası:   ${TOTAL_FILES}"
echo -e "  Temizlenen:       ${CURATED_FILES}"
if [ "$TOTAL_FILES" -gt 0 ] && [ "$CURATED_FILES" -gt 0 ]; then
    SAVED=$((TOTAL_LINES_BEFORE - TOTAL_LINES_AFTER))
    echo -e "  Satır (önce):     ${TOTAL_LINES_BEFORE}"
    echo -e "  Satır (sonra):    ${TOTAL_LINES_AFTER}"
    echo -e "  Kazanç:           ${GREEN}−${SAVED} satır${NC}"
fi
echo -e "${BOLD}══════════════════════════════════════════${NC}"
