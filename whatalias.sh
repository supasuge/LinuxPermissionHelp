#!/usr/bin/env bash
#
# whatalias — scan common shell config locations for alias definitions
# Supports common Bash/Zsh alias syntax across user and system config files.
#

set -euo pipefail
IFS=$'\n\t'

# ---------- Colors ----------
ESC=$'\e['
RESET="${ESC}0m"
BOLD="${ESC}1m"
HDR="${ESC}38;5;82m"
NAME="${ESC}38;5;39m"
CMD="${ESC}38;5;220m"
SRC="${ESC}38;5;141m"
WARN="${ESC}38;5;203m"

# ---------- Storage ----------
declare -A ALIASES
declare -A SOURCES

# ---------- Common alias definition paths ----------
# Order matters: later files override earlier ones.
CONFIG_FILES=(
  # System-wide bash/zsh files
  "/etc/profile"
  "/etc/bash.bashrc"   # Debian/Ubuntu
  "/etc/bashrc"        # RHEL/Fedora/Arch/openSUSE common
  "/etc/zsh/zshenv"
  "/etc/zsh/zprofile"
  "/etc/zsh/zshrc"
  "/etc/zsh/zlogin"
  "/etc/zshrc"

  # User shell files
  "$HOME/.profile"
  "$HOME/.bash_profile"
  "$HOME/.bash_login"
  "$HOME/.bashrc"
  "$HOME/.bash_aliases"
  "$HOME/.zshenv"
  "$HOME/.zprofile"
  "$HOME/.zshrc"
  "$HOME/.zlogin"

  # XDG-ish / custom common locations
  "$HOME/.config/bash/aliases"
  "$HOME/.config/bashrc"
  "$HOME/.config/zsh/.zshrc"
  "$HOME/.config/zsh/aliases"
  "$HOME/.aliases"
  "$HOME/.shell_aliases"
)

# ---------- Helpers ----------
trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

strip_inline_comment() {
  # Remove comments only when # appears outside single/double quotes.
  local input="$1"
  local out=""
  local i ch
  local in_squote=0
  local in_dquote=0
  local prev=''

  for (( i=0; i<${#input}; i++ )); do
    ch="${input:i:1}"

    if [[ "$ch" == "'" && $in_dquote -eq 0 ]]; then
      if [[ "$prev" != '\' ]]; then
        (( in_squote = 1 - in_squote ))
      fi
      out+="$ch"
      prev="$ch"
      continue
    fi

    if [[ "$ch" == '"' && $in_squote -eq 0 ]]; then
      if [[ "$prev" != '\' ]]; then
        (( in_dquote = 1 - in_dquote ))
      fi
      out+="$ch"
      prev="$ch"
      continue
    fi

    if [[ "$ch" == "#" && $in_squote -eq 0 && $in_dquote -eq 0 ]]; then
      break
    fi

    out+="$ch"
    prev="$ch"
  done

  printf '%s' "$out"
}

unquote_outer() {
  local s
  s="$(trim "$1")"

  if [[ "$s" =~ ^\"(.*)\"$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
  elif [[ "$s" =~ ^\'(.*)\'$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
  else
    printf '%s' "$s"
  fi
}

parse_alias_line() {
  local line="$1"
  local src_file="$2"
  local rest name cmd

  line="$(strip_inline_comment "$line")"
  line="$(trim "$line")"
  [[ -n "$line" ]] || return 0
  [[ "$line" == alias* ]] || return 0

  # Remove leading "alias"
  rest="${line#alias}"
  rest="$(trim "$rest")"

  # Only handle one alias definition per line:
  # alias ll='ls -alF'
  # alias grep='grep --color=auto'
  #
  # Does not attempt to evaluate shell logic or sourced files.
  if [[ "$rest" =~ ^([a-zA-Z0-9_.:+@/%-]+)=(.*)$ ]]; then
    name="${BASH_REMATCH[1]}"
    cmd="${BASH_REMATCH[2]}"
    cmd="$(unquote_outer "$cmd")"

    ALIASES["$name"]="$cmd"
    SOURCES["$name"]="$src_file"
  fi
}

parse_file() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  [[ -r "$file" ]] || return 0

  while IFS= read -r line || [[ -n "$line" ]]; do
    parse_alias_line "$line" "$file"
  done < "$file"
}

# ---------- Main ----------
found_files=0
for file in "${CONFIG_FILES[@]}"; do
  if [[ -f "$file" && -r "$file" ]]; then
    ((found_files += 1))
    parse_file "$file"
  fi
done

if (( found_files == 0 )); then
  echo -e "${WARN}No readable common shell config files were found.${RESET}"
  exit 1
fi

if (( ${#ALIASES[@]} == 0 )); then
  echo -e "${WARN}No aliases found in scanned config files.${RESET}"
  exit 0
fi

# Compute column widths
max_name=5   # "Alias"
max_cmd=7    # "Command"

for name in "${!ALIASES[@]}"; do
  (( ${#name} > max_name )) && max_name=${#name}
  (( ${#ALIASES[$name]} > max_cmd )) && max_cmd=${#ALIASES[$name]}
done

# Header
echo -e "${BOLD}${HDR}Aliases found across common shell config paths (${#ALIASES[@]})${RESET}"
echo
printf "%-${max_name}s  %-${max_cmd}s  %s\n" "Alias" "Command" "Source"
printf "%-${max_name}s  %-${max_cmd}s  %s\n" \
  "$(printf '%*s' "$max_name" '' | tr ' ' '-')" \
  "$(printf '%*s' "$max_cmd" '' | tr ' ' '-')" \
  "------"

# Rows
while IFS= read -r name; do
  printf "%b%-${max_name}s%b  %b%-${max_cmd}s%b  %b%s%b\n" \
    "$NAME" "$name" "$RESET" \
    "$CMD" "${ALIASES[$name]}" "$RESET" \
    "$SRC" "${SOURCES[$name]}" "$RESET"
done < <(printf '%s\n' "${!ALIASES[@]}" | sort)
