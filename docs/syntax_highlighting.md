# Syntax highlighting

Instructions how to add syntax highlighting for the different supported editors.

## VIM

1. Create directory for custom VIM syntaxes `mkdir -p ~/.vim/syntax/`
2. Move VIM syntax file [torth.vim](../editor/torth.vim) to the VIM syntax folder `cp torth.vim ~/.vim/syntax/`
3. Add row `syntax on` to `~/.vimrc` if it is not already there to enable syntax highlighting

## Visual Studio Code

1. Copy the whole [VSCode syntax folder](../editor/vscode/) (including the torth folder) to VSCode's `extensions` folder
   - Windows default: `C:\Users\{Username}\AppData\Local\Programs\Microsoft VS Code\resources\app\extensions`
