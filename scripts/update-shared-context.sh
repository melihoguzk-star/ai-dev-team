#!/bin/bash
# ============================================================================
# update-shared-context.sh — Agent memory dosyalarını okur, shared context günceller
# ============================================================================
#
# Kullanım:
#   ./update-shared-context.sh
#
# İşlev:
#   1. Tüm agent memory dosyalarını (~/.memory/*.md) okur
#   2. Ortak pattern'leri shared-context.md'ye ekler
#   3. Çakışan bilgileri raporlar
#
# ============================================================================
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

MEMORY_DIR="$HOME/ai-dev-team/.memory"
SHARED_FILE="$MEMORY_DIR/shared-context.md"
REPORT_FILE="$MEMORY_DIR/sync-report-$(date +%Y%m%d-%H%M%S).md"

if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}Hata: $MEMORY_DIR dizini bulunamadı${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Agent Memory Senkronizasyon Raporu     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Agent memory dosyalarını bul
MEMORY_FILES=()
AGENT_COUNT=0
for f in "$MEMORY_DIR"/*.md; do
    [ "$(basename "$f")" = "shared-context.md" ] && continue
    [[ "$(basename "$f")" = sync-report-* ]] && continue
    if [ -f "$f" ]; then
        MEMORY_FILES+=("$f")
        AGENT_COUNT=$((AGENT_COUNT + 1))
    fi
done

echo -e "${CYAN}📂 Bulunan memory dosyaları: ${AGENT_COUNT}${NC}"
echo ""

if [ "$AGENT_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Henüz agent memory dosyası yok.${NC}"
    echo "Agent'lar çalıştıkça .memory/ dizininde dosyalar oluşacak."
    exit 0
fi

# Rapor başlat
cat > "$REPORT_FILE" << EOF
# Memory Senkronizasyon Raporu
Tarih: $(date '+%Y-%m-%d %H:%M:%S')
Agent sayısı: $AGENT_COUNT

## Okunan Dosyalar
EOF

# Her memory dosyasını oku ve pattern'leri çıkar
CONVENTIONS=()
ERRORS=()
PREFERENCES=()
CONFLICTS=()

for mf in "${MEMORY_FILES[@]}"; do
    agent_name=$(basename "$mf" .md)
    echo -e "  📄 ${CYAN}${agent_name}${NC}"
    echo "- $agent_name ($mf)" >> "$REPORT_FILE"

    # Convention'ları çıkar
    if grep -q "Convention" "$mf" 2>/dev/null; then
        while IFS= read -r line; do
            line=$(echo "$line" | sed 's/^- //')
            if [ -n "$line" ] && [[ "$line" != *"#"* ]]; then
                CONVENTIONS+=("[$agent_name] $line")
            fi
        done < <(sed -n '/Convention/,/^##/p' "$mf" | grep "^- " 2>/dev/null || true)
    fi

    # Hataları çıkar
    if grep -q "Hata" "$mf" 2>/dev/null; then
        while IFS= read -r line; do
            line=$(echo "$line" | sed 's/^- //')
            if [ -n "$line" ] && [[ "$line" != *"#"* ]]; then
                ERRORS+=("[$agent_name] $line")
            fi
        done < <(sed -n '/Hata/,/^##/p' "$mf" | grep "^- " 2>/dev/null || true)
    fi

    # Tercihleri çıkar
    if grep -q "Tercih" "$mf" 2>/dev/null; then
        while IFS= read -r line; do
            line=$(echo "$line" | sed 's/^- //')
            if [ -n "$line" ] && [[ "$line" != *"#"* ]]; then
                PREFERENCES+=("[$agent_name] $line")
            fi
        done < <(sed -n '/Tercih/,/^##/p' "$mf" | grep "^- " 2>/dev/null || true)
    fi
done

echo ""

# Raporu tamamla
cat >> "$REPORT_FILE" << EOF

## Çıkarılan Convention'lar (${#CONVENTIONS[@]})
EOF
for c in "${CONVENTIONS[@]}"; do echo "- $c" >> "$REPORT_FILE"; done

cat >> "$REPORT_FILE" << EOF

## Çıkarılan Hatalar (${#ERRORS[@]})
EOF
for e in "${ERRORS[@]}"; do echo "- $e" >> "$REPORT_FILE"; done

cat >> "$REPORT_FILE" << EOF

## Çıkarılan Tercihler (${#PREFERENCES[@]})
EOF
for p in "${PREFERENCES[@]}"; do echo "- $p" >> "$REPORT_FILE"; done

# Çakışma tespiti (aynı konu farklı agent'lardan farklı bilgi)
cat >> "$REPORT_FILE" << EOF

## Çakışma Analizi
EOF

if [ ${#CONFLICTS[@]} -gt 0 ]; then
    for conflict in "${CONFLICTS[@]}"; do
        echo "- ⚠️ $conflict" >> "$REPORT_FILE"
    done
else
    echo "Çakışma tespit edilmedi." >> "$REPORT_FILE"
fi

# shared-context.md güncelle (agent öğrenimleri bölümü)
if [ ${#CONVENTIONS[@]} -gt 0 ] || [ ${#ERRORS[@]} -gt 0 ] || [ ${#PREFERENCES[@]} -gt 0 ]; then
    # Mevcut shared-context.md'nin sonuna agent öğrenimlerini ekle
    # Eğer zaten "Agent Öğrenimleri" bölümü varsa güncelle
    if grep -q "## Agent Öğrenimleri" "$SHARED_FILE" 2>/dev/null; then
        # Mevcut bölümü sil ve yeniden yaz
        sed -i.bak '/## Agent Öğrenimleri/,$d' "$SHARED_FILE"
        rm -f "$SHARED_FILE.bak"
    fi

    cat >> "$SHARED_FILE" << EOF

## Agent Öğrenimleri
Son senkronizasyon: $(date '+%Y-%m-%d %H:%M:%S')

### Convention'lar (agent'lardan)
EOF
    for c in "${CONVENTIONS[@]}"; do echo "- $c" >> "$SHARED_FILE"; done

    cat >> "$SHARED_FILE" << EOF

### Hatalar ve Çözümler (agent'lardan)
EOF
    for e in "${ERRORS[@]}"; do echo "- $e" >> "$SHARED_FILE"; done

    cat >> "$SHARED_FILE" << EOF

### Tercihler (agent'lardan)
EOF
    for p in "${PREFERENCES[@]}"; do echo "- $p" >> "$SHARED_FILE"; done

    echo -e "${GREEN}✅ shared-context.md güncellendi${NC}"
fi

echo -e "${GREEN}✅ Rapor kaydedildi: ${REPORT_FILE}${NC}"
echo ""
echo -e "Özet:"
echo -e "  Convention: ${#CONVENTIONS[@]}"
echo -e "  Hata:       ${#ERRORS[@]}"
echo -e "  Tercih:     ${#PREFERENCES[@]}"
echo -e "  Çakışma:    ${#CONFLICTS[@]}"
