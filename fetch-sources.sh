#!/bin/sh
# The fonts terminal.py merges into Pinboard Typewriter NF CN, at pinned
# versions, checked against their SHA-256 before use.
set -eu
cd "$(dirname "$0")"
mkdir -p sources/wenkai sources/nerd

fetch() {   # url file sha256
  [ -f "$2" ] || curl -fsSL -o "$2" "$1"
  echo "$3  $2" | shasum -a 256 -c -
}

WK=https://github.com/lxgw/LxgwWenkaiTC/releases/download/v1.530
fetch $WK/LXGWWenKaiMonoTC-Regular.ttf sources/wenkai/LXGWWenKaiMonoTC-Regular.ttf \
  784e26e968fe777fb8f93b2de66ae55a5e1c5405ac31f6144692709c7a6e4517
fetch $WK/LXGWWenKaiMonoTC-Medium.ttf sources/wenkai/LXGWWenKaiMonoTC-Medium.ttf \
  173c18310ec5da94aa649f7e696fe3905f0b04fa6629504e29dcce067e7e54d3
curl -fsSL -o sources/wenkai/OFL.txt https://raw.githubusercontent.com/lxgw/LxgwWenkaiTC/v1.530/OFL.txt

fetch https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/NerdFontsSymbolsOnly.zip \
  sources/nerd/NerdFontsSymbolsOnly.zip fdca3682534f6f65e1ccb2345b0362ccf67d9b8eca7c8025330946e93e2473bc
unzip -oq sources/nerd/NerdFontsSymbolsOnly.zip -d sources/nerd/unpacked
