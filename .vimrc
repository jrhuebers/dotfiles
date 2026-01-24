
filetype plugin indent on
syntax on

set number

set listchars=space:·,trail:·

set expandtab       " use spaces instead of actual tab characters
set tabstop=8       " a tab looks like 8 spaces
set shiftwidth=4    " indentation uses 4 spaces
set softtabstop=4   " pressing Tab inserts 4 spaces
autocmd FileType make setlocal noexpandtab " Makefiles require real tabs for recipes.

" Search settings
set hlsearch
set incsearch
nnoremap <Esc> :nohl<CR>

set mouse=a

" Screen-line movement when wrapped
" j/k move by display lines when no count is given; with counts they behave normally.
nnoremap <expr> k (v:count == 0 ? 'gk' : 'k')
nnoremap <expr> j (v:count == 0 ? 'gj' : 'j')

" Y becomes y$ (yank to end of line), consistent with D and C.
nnoremap Y y$

" :Indent sets folding based on indent.
command Indent set foldmethod=indent

nnoremap <C-j> o<Esc>k
nnoremap <C-k> O<Esc>j

" statusline
set laststatus=2 " gives a proper status line
set statusline=%f\ %h%w%m%r\ \ \ Buffer\ %n%=%(%l,%c%V\ %=\ %P%)

