
" Just a note - C-W-f - open file under cursor in new window
" and gf - open in current window

set backupdir=~/tmp

" S-INS
map <S-Insert> <MiddleMouse>
map! <S-Insert> <MiddleMouse>

" Beginning of file - end of file
map <C-PageUp> gg
map <C-PageDown> G

imap <C-PageUp> <esc>gg<ins>
imap <C-PageDown> <esc>G<ins>
  
" window resizing
map <C-kplus> :res +1<CR>
imap <C-kplus> <esc>:res +1<CR><ins>
map <C-kminus> :res -1<CR>
imap <C-kminus> <esc>:res -1<CR><ins>
 
set viminfo='20,f1,\"1000,%,n~/.viminfo

"set statusline=%<%f%=\ [%1*%M%*%n%R%H]\ \ %-25(%3l,%c%03V\ \ %P\ (%L)%)%12o'%03b'
set statusline=%=%f\ \"%F\"\ %m%R\ [%4l(%3p%%):%3c-(0x%2B),%Y]


autocmd BufRead *.C silent! %s/^M$//
autocmd BufRead *.H silent! %s/^M$//
 
"set statusline=%<%f%h%m%r%=%{&ff}\ %l,%c%V\ %P

" expand tab
set et

" 4
set softtabstop=4
set shiftwidth=4
set tabstop=4

set virtualedit=all

" Solaris had a problems with it
set wildchar=<Tab>

" switch off error bells
set noeb
set vb

" fix solaris fucking backspace
set backspace=indent,eol,start

" switch between windows
imap <C-Tab> <ESC><C-w><C-w><INS>
map <C-Tab> <C-w><C-w>

" save on f2
imap <F2> <ESC>:w<CR><INS><RIGHT>
map <F2> :w<CR>

" turn off bells and whistles
set guioptions=-M
set guioptions=-R
set guioptions=-L
set guioptions=-t

" syntex
syntax on

" no wrap
set nowrap

