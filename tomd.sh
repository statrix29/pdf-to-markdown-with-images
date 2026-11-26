# Source in zsh to make tomd, tomd-fast, and tomd-pack available.
typeset -g TOMD_SCRIPT_DIR="${${(%):-%x}:A:h}"

_tomd_convert() {
  local input="$1" work="$2" stem="${1:t:r}" ext="${${1:e}:l}"

  case "$ext" in
    pdf|pptx|ppt|png|jpg|jpeg|tif|tiff|bmp|webp)
      ( cd "$work" && docling convert "$input" --to md \
          --image-export-mode referenced --heading-hierarchy \
          --ocr-engine ocrmac --abort-on-error )
      ;;
    docx|odt|rtf|html|htm|tex|latex|rst|org|ipynb|md|markdown)
      ( cd "$work" && pandoc --sandbox "$input" -t gfm --wrap=none \
          --extract-media="./${stem}_media" -o "./$stem.md" )
      ;;
    *)
      markitdown "$input" -o "$work/$stem.md"
      ;;
  esac
}

_tomd_run() (
  emulate -L zsh
  local mode="$1" input="$2" outdir="$3"
  if [[ -z "$input" || ! -f "$input" ]]; then
    print -u2 "Usage: $mode <file> [output-dir]"
    return 1
  fi

  input="${input:A}"
  outdir="${outdir:-${input:h}}"
  mkdir -p -- "$outdir" || return 1
  outdir="${outdir:A}"
  local stem="${input:t:r}" md="$outdir/${input:t:r}.md" work
  if [[ -e "$md" || -L "$md" ]]; then
    print -u2 "Output already exists: $md. Choose a new output directory."
    return 1
  fi

  work=$(mktemp -d "$outdir/.tomd.XXXXXXXX") || return 1
  trap 'rm -rf -- "$work"' EXIT
  if [[ "$mode" == tomd-fast ]]; then
    markitdown "$input" -o "$work/$stem.md" || return 1
  else
    _tomd_convert "$input" "$work" || return 1
  fi
  if [[ ! -f "$work/$stem.md" ]]; then
    print -u2 "$mode: no Markdown output produced for $input"
    return 1
  fi

  local -a outputs
  local item
  if [[ "$mode" == tomd-pack ]]; then
    python3 -I "$TOMD_SCRIPT_DIR/mdpack.py" "$work/$stem.md" --bundle || return 1
    [[ -d "$work/${stem}_figs" ]] && outputs+=("${stem}_figs")
    outputs+=("${stem}_for_ai.zip")
  else
    for item in "${stem}_artifacts" "${stem}_media"; do
      [[ -d "$work/$item" ]] && outputs+=("$item")
    done
  fi
  outputs+=("$stem.md")

  for item in "${outputs[@]}"; do
    if [[ -e "$outdir/$item" || -L "$outdir/$item" ]]; then
      print -u2 "Output already exists: $outdir/$item. Choose a new output directory."
      return 1
    fi
  done
  for item in "${outputs[@]}"; do
    mv -n -- "$work/$item" "$outdir/$item" || return 1
    if [[ -e "$work/$item" ]]; then
      print -u2 "Output appeared during conversion: $outdir/$item"
      return 1
    fi
  done

  print "Saved:  $md"
  if [[ "$mode" == tomd-pack ]]; then
    print "Bundle: $outdir/${stem}_for_ai.zip"
  fi
)

tomd() { _tomd_run tomd "$@"; }
tomd-fast() { _tomd_run tomd-fast "$@"; }
tomd-pack() { _tomd_run tomd-pack "$@"; }
