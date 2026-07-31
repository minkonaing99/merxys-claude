#!/usr/bin/env bash
# Claude Code status line script
# Shows: folder | git branch | model | ctx % | 5h % | cost

input=$(cat)

# --- Persist metrics for external readers (e.g. NoctAgent) ---
printf '%s' "$input" > "$HOME/.claude/statusline-metrics.json.tmp" 2>/dev/null \
  && mv -f "$HOME/.claude/statusline-metrics.json.tmp" "$HOME/.claude/statusline-metrics.json" 2>/dev/null

# --- Extract fields ---
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
model=$(echo "$input" | jq -r '.model.display_name // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
used_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(echo "$input" | jq -r '
  .rate_limits.five_hour.resets_at //
  .rate_limits.five_hour.reset_at //
  .rate_limits.five_hour.resets //
  empty')
weekly_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
extra_pct=$(echo "$input" | jq -r '
  .rate_limits.extra.used_percentage //
  .rate_limits.extra_usage.used_percentage //
  .rate_limits.overage.used_percentage //
  .usage.extra.used_percentage //
  empty')
session_cost=$(echo "$input" | jq -r '.session_cost // empty')

# --- Folder (last 2 path segments) ---
parent=$(basename "$(dirname "$cwd")")
base=$(basename "$cwd")
if [ -n "$parent" ] && [ "$parent" != "." ] && [ "$parent" != "/" ]; then
  folder="${parent}/${base}"
else
  folder="$base"
fi

# --- Git branch (skip lock, silent) ---
branch=""
if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
fi

# --- Progress bar (10 chars wide) ---
build_bar() {
  local pct="$1"
  local width=10
  local filled=0
  if [ -n "$pct" ]; then
    filled=$(printf '%.0f' "$(echo "$pct * $width / 100" | bc -l 2>/dev/null || echo 0)")
  fi
  [ "$filled" -gt "$width" ] && filled=$width
  local empty=$(( width - filled ))
  local bar=""
  local i
  for (( i=0; i<filled; i++ )); do bar="${bar}█"; done
  for (( i=0; i<empty;  i++ )); do bar="${bar}░"; done
  echo "$bar"
}

# --- Color a percentage value by threshold ---
# < 61%  → no color (plain)
# 61–85% → yellow
# >= 86% → red
color_pct() {
  local pct="$1"
  local label="$2"
  local YELLOW=$'\e[33m'
  local RED=$'\e[31m'
  local RESET=$'\e[0m'
  local int_pct
  int_pct=$(printf '%.0f' "$pct")
  if [ "$int_pct" -ge 86 ]; then
    printf "%s%s%s" "${RED}" "${label}" "${RESET}"
  elif [ "$int_pct" -ge 61 ]; then
    printf "%s%s%s" "${YELLOW}" "${label}" "${RESET}"
  else
    printf "%s" "${label}"
  fi
}

# --- Color a percentage: 60-80% yellow, >80% red, else plain ---
color_over80() {
  local pct="$1"
  local label="$2"
  local YELLOW=$'\e[33m'
  local RED=$'\e[31m'
  local RESET=$'\e[0m'
  local int_pct
  int_pct=$(printf '%.0f' "$pct")
  if [ "$int_pct" -gt 80 ]; then
    printf "%s%s%s" "${RED}" "${label}" "${RESET}"
  elif [ "$int_pct" -ge 60 ]; then
    printf "%s%s%s" "${YELLOW}" "${label}" "${RESET}"
  else
    printf "%s" "${label}"
  fi
}

# --- Format token count: >=1000 → k, >=1000000 → m ---
format_tokens() {
  local n="$1"
  awk -v n="$n" '
    function fmt(v, u) { s = sprintf("%.1f", v); sub(/\.0$/, "", s); return s u }
    BEGIN {
      if (n >= 1000000) {
        v = n / 1000000
        if (sprintf("%.1f", v) == "1000.0") { printf "%s", fmt(n/1000000000, "b"); exit }
        printf "%s", fmt(v, "m")
      } else if (n >= 1000) {
        v = n / 1000
        if (sprintf("%.1f", v) == "1000.0") { printf "%s", fmt(n/1000000, "m"); exit }
        printf "%s", fmt(v, "k")
      } else {
        printf "%d", n
      }
    }'
}

# --- Assemble line ---
# Segment separator
SEP=" | "

line=""

# Folder
line=" ${folder}"

# Git branch
if [ -n "$branch" ]; then
  line="${line}${SEP}${branch}"
fi

# Model
if [ -n "$model" ]; then
  line="${line}${SEP}${model}"
fi

# Context: percentage(token count)
if [ -n "$used_pct" ]; then
  ctx_label=$(printf '%.0f' "$used_pct")
  ctx_str=$(color_pct "$used_pct" "${ctx_label}%")
  if [ -n "$used_tokens" ]; then
    ctx_str="${ctx_str}($(format_tokens "$used_tokens"))"
  fi
  line="${line}${SEP}${ctx_str}"
fi

# 5-hour percent : weekly percent (5-hour reset time) — red only if >80%
if [ -n "$five_pct" ]; then
  five_label=$(printf '%.0f' "$five_pct")
  reset_str=""
  if [ -n "$five_reset" ]; then
    if [[ "$five_reset" =~ ^[0-9]+$ ]]; then
      reset_str=$(date -r "$five_reset" "+%-I:%M%p" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    else
      clean="${five_reset%%.*}"
      clean="${clean%Z}"
      clean="${clean%+*}"
      reset_str=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$clean" "+%s" 2>/dev/null \
                  | xargs -I{} date -r {} "+%-I:%M%p" 2>/dev/null | tr '[:upper:]' '[:lower:]')
      [ -z "$reset_str" ] && reset_str=$(date -d "$five_reset" "+%-I:%M%p" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    fi
  fi
  combined=$(color_over80 "$five_pct" "${five_label}%")
  if [ -n "$weekly_pct" ]; then
    weekly_label=$(printf '%.0f' "$weekly_pct")
    combined="${combined} : $(color_over80 "$weekly_pct" "${weekly_label}%")"
  fi
  if [ -n "$reset_str" ]; then
    combined="${combined} (${reset_str})"
  fi
  line="${line}${SEP}${combined}"
fi

# Extra usage: only when present and non-zero
if [ -n "$extra_pct" ]; then
  extra_int=$(printf '%.0f' "$extra_pct")
  if [ "$extra_int" -gt 0 ]; then
    line="${line}${SEP}extra:$(color_pct "$extra_pct" "${extra_int}%")"
  fi
fi

# Session cost (only when present and non-zero)
if [ -n "$session_cost" ] && [ "$session_cost" != "0" ] && [ "$session_cost" != "0.0" ]; then
  cost_label=$(printf '$%.2f' "$session_cost")
  line="${line}${SEP}${cost_label}"
fi

printf "%s" "$line"
