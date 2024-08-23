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
set iskeyword=a-z,A-Z,-,*,_,!,@
syntax keyword torthTodos TODO NOTE

" Language keywords
syntax keyword torthKeywords BREAK CONTINUE DO DONE ELIF ELSE END ENDIF IF INCLUDE WHILE

syntax keyword torthFunctionDefs CLASS CONST END ENDCLASS ENUM FUNCTION IN METHOD PEEK RETURN TAKE

" Comments
syntax region torthCommentLine start="//" end="$"   contains=torthTodos

" String literals
syntax match torthString /".*"/hs=s+1,he=e-1 contains=torthEscapes

" Character literals
syntax match torthCharacter /'\\[nr\"']\|'.'/hs=s+1,he=e-1 contains=torthEscapes

" Escape literals \n, \r, ....
syntax match torthEscapes display contained /\\[nr\"']/

" Number literals
syntax region torthNumber start=/\s\d/  skip=/\d/ end=/\s/
syntax keyword torthNull  NULL

" Type names the compiler recognizes
syntax keyword torthTypeNames any bool char fn none int ptr str

" Set highlights
highlight default link torthTodos Todo
highlight default link torthKeywords Keyword
highlight default link torthFunctionDefs Macro
highlight default link torthCommentLine Comment
highlight default link torthString String
highlight default link torthCharacter Character
highlight default link torthNull Number
highlight default link torthNumber Number
highlight default link torthTypeNames Type
highlight default link torthEscapes SpecialChar

let b:current_syntax = "torth"
