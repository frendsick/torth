" Vim syntax file
" Language: Torth

" Usage Instructions
" Put this file in .vim/syntax/torth.vim
" and add in your .vimrc file the next line:
" autocmd BufRead,BufNewFile *.torth set filetype=torth

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
syntax region torthString start=/\v"/ skip=/\v\\./ end=/\v"/ contains=torthEscapes

" Escape literals \n, \r, ....
syntax match torthEscapes display contained "\\[nr\"']"

" Number literals
syntax region torthNumber start=/\s\d/  skip=/\d/ end=/\s/
syntax region torthUint   start=/\su\d/ skip=/\d/ end=/\s/
syntax keyword torthNull  NULL

" Type names the compiler recognizes
syntax keyword torthTypeNames any bool char int ptr str

" Set highlights
highlight default link torthTodos Todo
highlight default link torthKeywords Keyword
highlight default link torthFunctionDefs Macro
highlight default link torthCommentLine Comment
highlight default link torthString String
highlight default link torthNull Number
highlight default link torthNumber Number
highlight default link torthUint Number
highlight default link torthTypeNames Type
highlight default link torthChar Character
highlight default link torthEscapes SpecialChar

let b:current_syntax = "torth"
