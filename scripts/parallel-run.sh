#!/bin/bash
# ============================================================================
# parallel-run.sh — İki agent'ı tmux ile paralel çalıştırır
# ============================================================================
#
# Kullanım:
#   ./parallel-run.sh "<prompt1>" "<prompt2>"
#
# Örnekler:
#   ./parallel-run.sh \
#     "backend-developer subagent'ını kullan. Backend API'yi geliştir." \
#     "swift-expert subagent'ını kullan. iOS core modüllerini yaz."
#
# İşlev:
#   1. "ai-pipeline" tmux session oluşturur
#   2. Session'ı iki pane'e böler (vertical split)
#   3. Sol pane'de prompt1, sağ pane'de prompt2 çalıştırır
#   4. Çıktıları log dosyalarına yönlendirir
#   5. Her iki işlem bittiğinde tamamlanma mesajı gösterir
#
# Gereksinimler:
#   - tmux kurulu olmalı (brew install tmux)
#   - claude CLI kurulu olmalı
#
# Tmux kısayolları:
#   CTRL+B sonra ← veya → : Pane'ler arası geçiş
#   CTRL+B sonra z           : Aktif pane'i tam ekran yap/geri al
#   CTRL+B sonra d           : Session'dan ayrıl (arka planda devam eder)
#   tmux attach -t ai-pipeline : Tekrar bağlan
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
LOG_DIR="$PROJECT_ROOT/logs"
SESSION_NAME="ai-pipeline"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# ---- Argüman kontrolü ----
if [ $# -ne 2 ]; then
    echo -e "${RED}Hata: İki prompt argümanı gerekli${NC}"
    echo ""
    echo "Kullanım: $0 \"<prompt1>\" \"<prompt2>\""
    echo ""
    echo "Örnek:"
    echo "  $0 \\"
    echo "    \"backend-developer subagent'ını kullan. API'yi geliştir.\" \\"
    echo "    \"swift-expert subagent'ını kullan. iOS core yaz.\""
    exit 1
fi

PROMPT1="$1"
PROMPT2="$2"
LOG_LEFT="$LOG_DIR/parallel-${TIMESTAMP}-left.log"
LOG_RIGHT="$LOG_DIR/parallel-${TIMESTAMP}-right.log"

# ---- tmux kontrolü ----
if ! command -v tmux &>/dev/null; then
    echo -e "${RED}Hata: tmux kurulu değil${NC}"
    echo -e "Kurulum: ${CYAN}brew install tmux${NC}"
    echo ""
    echo -e "${YELLOW}Alternatif: Manuel paralel çalıştırma (aşağıya bak)${NC}"
    echo "============================================"
    echo ""
    echo "tmux olmadan manuel paralel çalıştırma:"
    echo ""
    echo "Terminal Tab 1:"
    echo "  claude --print \"$PROMPT1\" 2>&1 | tee $LOG_LEFT"
    echo ""
    echo "Terminal Tab 2:"
    echo "  claude --print \"$PROMPT2\" 2>&1 | tee $LOG_RIGHT"
    echo ""
    echo "============================================"
    exit 1
fi

# ---- Claude CLI kontrolü ----
if ! command -v claude &>/dev/null; then
    echo -e "${RED}Hata: claude CLI kurulu değil veya PATH'te değil${NC}"
    exit 1
fi

# ---- Log dizini oluştur ----
mkdir -p "$LOG_DIR"

# ---- Mevcut session varsa öldür ----
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Uyarı: '$SESSION_NAME' session'ı zaten var. Kapatılıyor...${NC}"
    tmux kill-session -t "$SESSION_NAME"
fi

# ---- Prompt'ları kısa göster ----
PROMPT1_SHORT="${PROMPT1:0:60}..."
PROMPT2_SHORT="${PROMPT2:0:60}..."

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       🚀 Paralel Agent Çalıştırma                ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Sol Pane:${NC}  $PROMPT1_SHORT"
echo -e "${CYAN}Sağ Pane:${NC} $PROMPT2_SHORT"
echo ""
echo -e "${CYAN}Log dosyaları:${NC}"
echo -e "  Sol: $LOG_LEFT"
echo -e "  Sağ: $LOG_RIGHT"
echo ""

# ---- Wrapper script'leri oluştur (log yönlendirme + tamamlanma mesajı) ----
LEFT_SCRIPT=$(mktemp /tmp/ai-parallel-left.XXXXXX.sh)
RIGHT_SCRIPT=$(mktemp /tmp/ai-parallel-right.XXXXXX.sh)

cat > "$LEFT_SCRIPT" << 'WRAPPER_EOF'
#!/bin/bash
PROMPT="$1"
LOG_FILE="$2"
DONE_FILE="$3"

echo "════════════════════════════════════════" | tee "$LOG_FILE"
echo "🤖 SOL PANE — Agent çalışıyor..."       | tee -a "$LOG_FILE"
echo "Başlangıç: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "════════════════════════════════════════" | tee -a "$LOG_FILE"
echo ""                                         | tee -a "$LOG_FILE"

# Claude CLI çalıştır
# --print: çıktıyı stdout'a yaz (non-interactive)
# Eğer --print desteklenmiyorsa -p dene
if claude --print "$PROMPT" 2>&1 | tee -a "$LOG_FILE"; then
    echo ""                                     | tee -a "$LOG_FILE"
    echo "✅ SOL PANE TAMAMLANDI"               | tee -a "$LOG_FILE"
else
    EXIT_CODE=$?
    echo ""                                     | tee -a "$LOG_FILE"
    echo "❌ SOL PANE HATA (exit: $EXIT_CODE)"  | tee -a "$LOG_FILE"
fi

echo "Bitiş: $(date '+%Y-%m-%d %H:%M:%S')"     | tee -a "$LOG_FILE"
touch "$DONE_FILE"

# Pane'de kal (kapanmasın)
echo ""
echo "Çıkmak için ENTER'a basın..."
read -r
WRAPPER_EOF

cat > "$RIGHT_SCRIPT" << 'WRAPPER_EOF'
#!/bin/bash
PROMPT="$1"
LOG_FILE="$2"
DONE_FILE="$3"

echo "════════════════════════════════════════" | tee "$LOG_FILE"
echo "🤖 SAĞ PANE — Agent çalışıyor..."       | tee -a "$LOG_FILE"
echo "Başlangıç: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "════════════════════════════════════════" | tee -a "$LOG_FILE"
echo ""                                         | tee -a "$LOG_FILE"

if claude --print "$PROMPT" 2>&1 | tee -a "$LOG_FILE"; then
    echo ""                                     | tee -a "$LOG_FILE"
    echo "✅ SAĞ PANE TAMAMLANDI"               | tee -a "$LOG_FILE"
else
    EXIT_CODE=$?
    echo ""                                     | tee -a "$LOG_FILE"
    echo "❌ SAĞ PANE HATA (exit: $EXIT_CODE)"  | tee -a "$LOG_FILE"
fi

echo "Bitiş: $(date '+%Y-%m-%d %H:%M:%S')"     | tee -a "$LOG_FILE"
touch "$DONE_FILE"

echo ""
echo "Çıkmak için ENTER'a basın..."
read -r
WRAPPER_EOF

chmod +x "$LEFT_SCRIPT" "$RIGHT_SCRIPT"

# Done marker dosyaları
DONE_LEFT=$(mktemp /tmp/ai-done-left.XXXXXX)
DONE_RIGHT=$(mktemp /tmp/ai-done-right.XXXXXX)
rm -f "$DONE_LEFT" "$DONE_RIGHT"

# ---- tmux session oluştur ----
# Sol pane (ilk pane)
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

# Status bar'da bilgi göster
tmux set-option -t "$SESSION_NAME" status on
tmux set-option -t "$SESSION_NAME" status-style "bg=colour235,fg=colour136"
tmux set-option -t "$SESSION_NAME" status-left "#[fg=colour46,bold] 🚀 AI Pipeline "
tmux set-option -t "$SESSION_NAME" status-right "#[fg=colour166] %H:%M | #[fg=colour136]CTRL+B ← → pane geçiş "
tmux set-option -t "$SESSION_NAME" pane-border-style "fg=colour240"
tmux set-option -t "$SESSION_NAME" pane-active-border-style "fg=colour46"

# Sol pane'de prompt1 çalıştır
tmux send-keys -t "$SESSION_NAME" "bash '$LEFT_SCRIPT' '$PROMPT1' '$LOG_LEFT' '$DONE_LEFT'" C-m

# Sağ pane oluştur (vertical split)
tmux split-window -h -t "$SESSION_NAME"

# Sağ pane'de prompt2 çalıştır
tmux send-keys -t "$SESSION_NAME" "bash '$RIGHT_SCRIPT' '$PROMPT2' '$LOG_RIGHT' '$DONE_RIGHT'" C-m

# Sol pane'e odaklan
tmux select-pane -t "$SESSION_NAME":0.0

echo -e "${GREEN}✅ tmux session başlatıldı: ${SESSION_NAME}${NC}"
echo ""
echo -e "Bağlanmak için:"
echo -e "  ${CYAN}tmux attach -t $SESSION_NAME${NC}"
echo ""
echo -e "Session'dan ayrılmak:"
echo -e "  ${CYAN}CTRL+B sonra d${NC} (arka planda devam eder)"
echo ""
echo -e "Pane'ler arası geçiş:"
echo -e "  ${CYAN}CTRL+B sonra ← veya →${NC}"
echo ""
echo -e "Log dosyalarını takip etmek:"
echo -e "  ${CYAN}tail -f $LOG_LEFT${NC}"
echo -e "  ${CYAN}tail -f $LOG_RIGHT${NC}"
echo ""

# ---- Otomatik session'a bağlan ----
tmux attach -t "$SESSION_NAME"

# ---- Session'dan çıkıldıktan sonra temizlik ----
# (kullanıcı CTRL+B d ile ayrılırsa buraya düşer)
echo ""
echo -e "${CYAN}Session arka planda çalışmaya devam ediyor.${NC}"
echo -e "Tekrar bağlanmak: ${CYAN}tmux attach -t $SESSION_NAME${NC}"
echo -e "Durdurmak:        ${CYAN}tmux kill-session -t $SESSION_NAME${NC}"

# Temp dosyaları temizle (session kapandığında)
trap "rm -f '$LEFT_SCRIPT' '$RIGHT_SCRIPT' '$DONE_LEFT' '$DONE_RIGHT' 2>/dev/null" EXIT
