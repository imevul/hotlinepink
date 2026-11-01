# Hotline Pink for Powerlevel10k: a small lean prompt.
# Use it as ~/.p10k.zsh, or copy the colour block into your own config.

'builtin' 'local' '-a' 'p10k_config_opts'
[[ ! -o 'aliases'         ]] || p10k_config_opts+=('aliases')
[[ ! -o 'sh_glob'         ]] || p10k_config_opts+=('sh_glob')
[[ ! -o 'no_brace_expand' ]] || p10k_config_opts+=('no_brace_expand')
'builtin' 'setopt' 'no_aliases' 'no_sh_glob' 'brace_expand'

() {
  emulate -L zsh -o extended_glob
  unset -m '(POWERLEVEL9K_*|DEFAULT_USER)~POWERLEVEL9K_GITSTATUS_DIR'

  typeset -g POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true
  typeset -g POWERLEVEL9K_MODE=nerdfont-complete
  typeset -g POWERLEVEL9K_ICON_PADDING=none
  typeset -g POWERLEVEL9K_INSTANT_PROMPT=quiet
  typeset -g POWERLEVEL9K_TRANSIENT_PROMPT=off

  typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(dir vcs newline prompt_char)
  typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status command_execution_time background_jobs context virtualenv node_version time)

  typeset -g POWERLEVEL9K_BACKGROUND=
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_{LEFT,RIGHT}_WHITESPACE=
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_SUBSEGMENT_SEPARATOR=' '
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_SEGMENT_SEPARATOR=
  typeset -g POWERLEVEL9K_VISUAL_IDENTIFIER_EXPANSION=
  typeset -g POWERLEVEL9K_PROMPT_ADD_NEWLINE=true
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_PREFIX=
  typeset -g POWERLEVEL9K_MULTILINE_NEWLINE_PROMPT_PREFIX=
  typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_PREFIX=

  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VIINS_CONTENT_EXPANSION='>'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VICMD_CONTENT_EXPANSION='<'
  typeset -g POWERLEVEL9K_DIR_MAX_LENGTH=80
  typeset -g POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_unique
  typeset -g POWERLEVEL9K_STATUS_OK=false
  typeset -g POWERLEVEL9K_STATUS_ERROR=true
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_THRESHOLD=3
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_PRECISION=0
  typeset -g POWERLEVEL9K_TIME_FORMAT='%D{%H:%M}'
  typeset -g POWERLEVEL9K_CONTEXT_{DEFAULT,SUDO}_{CONTENT,VISUAL_IDENTIFIER}_EXPANSION=

  # >>> hotline pink colours
  typeset -g POWERLEVEL9K_DIR_FOREGROUND='#FF5CB8'
  typeset -g POWERLEVEL9K_DIR_SHORTENED_FOREGROUND='#B8AAB2'
  typeset -g POWERLEVEL9K_DIR_ANCHOR_FOREGROUND='#FF1493'
  typeset -g POWERLEVEL9K_DIR_ANCHOR_BOLD=true
  typeset -g POWERLEVEL9K_VCS_CLEAN_FOREGROUND='#22C55E'
  typeset -g POWERLEVEL9K_VCS_UNTRACKED_FOREGROUND='#2DE2E6'
  typeset -g POWERLEVEL9K_VCS_MODIFIED_FOREGROUND='#F59E0B'
  typeset -g POWERLEVEL9K_VCS_CONFLICTED_FOREGROUND='#EF4444'
  typeset -g POWERLEVEL9K_VCS_LOADING_FOREGROUND='#B8AAB2'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND='#FF1493'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND='#EF4444'
  typeset -g POWERLEVEL9K_STATUS_ERROR_FOREGROUND='#EF4444'
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND='#F59E0B'
  typeset -g POWERLEVEL9K_BACKGROUND_JOBS_FOREGROUND='#2DE2E6'
  typeset -g POWERLEVEL9K_CONTEXT_FOREGROUND='#B8AAB2'
  typeset -g POWERLEVEL9K_CONTEXT_ROOT_FOREGROUND='#EF4444'
  typeset -g POWERLEVEL9K_VIRTUALENV_FOREGROUND='#B8AAB2'
  typeset -g POWERLEVEL9K_NODE_VERSION_FOREGROUND='#B8AAB2'
  typeset -g POWERLEVEL9K_TIME_FOREGROUND='#8E7985'
  # <<< hotline pink colours

  (( ! $+functions[p10k] )) || p10k reload
}

typeset -g POWERLEVEL9K_CONFIG_FILE=${${(%):-%x}:a}

(( ${#p10k_config_opts} )) && setopt ${p10k_config_opts[@]}
'builtin' 'unset' 'p10k_config_opts'
