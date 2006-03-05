

" Vertical blocks using mouse
noremap <M-LeftMouse> <LeftMouse><Esc><C-V>
noremap <M-LeftDrag> <LeftDrag>

set gcr=a:blinkon0" never blink the cursor

let g:uname = system("uname")
if v:shell_error
    let g:uname = 'unknown system'
else
    if g:uname =~ "SunOS"
        echo g:uname
    else
"        echo "Other: " . g:uname
    endif
endif

set laststatus=2

" Windows
"colorscheme desert
"colorscheme inkpot
"colorscheme MidNight2
"colorscheme BlueGreen
"colorscheme Dusk
"colorscheme OceanDeep
colorscheme Camo

" Unix
"colorscheme desert
"colorscheme edo_sea
"colorscheme blackdust
"colorscheme neon
 
map <C-F10> :source ~/.gvimrc<CR>

if has("gui_gtk2")
    set guifont=MiscFixed\ 10
else
    set guifont=Lucida_Console:h10:cRUSSIAN
"    set guifont=-misc-fixed-medium-r-normal--10-120-75-75-c-60-iso8859-1
endif

if has('gui_running')
    if g:uname =~ "SunOS"
        set lines=55
        set columns=95
    else
        if g:uname =~ "CYGWIN_NT-5.2"
            set lines=65
            set columns=81
        else
            set lines=90
            set columns=160
        endif
    endif
else
    set lines=25
    set columns=80
endif


"flag problematic whitespace (trailing and spaces before tabs)
"Note you get the same by doing let c_space_errors=1 but
"this rule really applys to everything.
highlight RedundantSpaces term=standout ctermbg=red guibg=red
match RedundantSpaces /\s\+$\| \+\ze\t/

" EOF

