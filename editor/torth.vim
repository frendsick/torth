" Vim syntax file
" Language: Torth

" === VIM ===
" Put this file in ~/.vim/syntax/torth.vim
" and add in your ~/.vimrc file the next line:
" autocmd BufRead,BufNewFile *.torth set filetype=torth

" === NEOVIM ===
" Put this file in $VIMRUNTIME/syntax/torth.vim (default: /usr/share/nvim/runtime/syntax/torth.vim)
" and add in your ~/.config/nvim/init.lua file the following lines:
"
" vim.filetype.add {
"     extension = {
"         torth = "torth",
"     },
" }

if exists("b:current_syntax")
  finish
endif

syntax case ignore
set iskeyword=a-z,A-Z,+,-,*,/,=,>,<,!,:

" Keyword tokens
syntax keyword torthBinding CONST ENUM IN PEEK TAKE
syntax keyword torthConditional IF ELIF ELSE ENDIF DO
syntax keyword torthFunction CLASS END ENDCLASS FUNCTION METHOD RETURN
syntax keyword torthInclude INCLUDE
syntax keyword torthOperators + - * / = > < == != >= <= -> >> <<
syntax keyword torthRepeat BREAK CONTINUE DONE WHILE
syntax keyword torthTodos TODO NOTE

" Comments
syntax region torthCommentLine start="\v(^|\s)//" end="$"   contains=torthTodos

" String literals
syntax region torthString start=/\v(^|\s)@<="/hs=s+1 end=/"/he=e-1 contains=torthEscapes

" Character literals
syntax match torthCharacter /'\\[nr\"']\|'.'/hs=s+1,he=e-1 contains=torthEscapes

" Escape literals \n, \r, ....
syntax match torthEscapes display contained /\\[nr\"']/

" Number literals
syntax match torthNumber /\v(^|\s)@<=\d+(\s|$)@=/ " Token with just numbers
syntax keyword torthNull  NULL
syntax keyword torthBoolean TRUE FALSE

" Type names the compiler recognizes
syntax keyword torthTypeNames any bool char fn none int ptr str List Array LinkedList

" Delimiters
syntax match torthDelimiter /[:.]/

" Set highlights
highlight default link torthTodos Todo
highlight default link torthBinding Statement
highlight default link torthConditional Conditional
highlight default link torthInclude Include
highlight default link torthRepeat Repeat
highlight default link torthFunction Function
highlight default link torthCommentLine Comment
highlight default link torthString String
highlight default link torthCharacter Character
highlight default link torthNull Number
highlight default link torthNumber Number
highlight default link torthBoolean Number
highlight default link torthTypeNames Type
highlight default link torthEscapes SpecialChar
highlight default link torthOperators Operator
highlight default link torthDelimiter Delimiter

let b:current_syntax = "torth"
