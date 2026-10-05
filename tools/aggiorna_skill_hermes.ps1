# Le skill di TAROTS per Hermes sono COPIE (decisione dell'operatore, 5/10: Hermes non deve poter cambiare gli originali
# del repository). Questo script:
#  1. toglie i collegamenti in E:\Projects\T-AI-rots\.agents\skills e mette al loro posto copie;
#  2. aggiorna le copie in %LOCALAPPDATA%\hermes\skills alla versione attuale del repository.
# Si rilancia a mano ogni volta che si vuole portare in Hermes una versione nuova delle skill.
$ErrorActionPreference = 'Stop'
$repo = 'E:\Projects\T-AI-rots\skills'
$fonti = @{
  'tarots-blog-publisher' = "$repo\tarots-blog-publisher"
  'tarots-blog-images'    = "$repo\tarots-blog-images"
  'browser-image-gen'     = "$repo\browser-image-gen"
  'crea-mazzo-tarocchi'   = "$repo\crea-mazzo-tarocchi"
}
$escludi = '__pycache__', 'tests', 'sessione_litmedia.json', 'url_immagini_scaricate.json', 'verifica_screenshot.png', '.gitignore'

function Copia($da, $a) {
  # /MIR: la copia diventa uguale alla fonte (file tolti nella fonte spariscono anche dalla copia), tranne gli esclusi,
  # che restano come sono (per esempio la sessione LitMedia del browser di Hermes).
  robocopy $da $a /MIR /XD $escludi /XF $escludi /NFL /NDL /NJH /NJS /NP | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy $da -> $a fallito ($LASTEXITCODE)" }
}

# 1. Cartella di progetto: via i collegamenti, dentro le copie.
$progetto = 'E:\Projects\T-AI-rots\.agents\skills'
foreach ($voce in Get-ChildItem $progetto) {
  if ($voce.LinkType) {
    $bersaglio = [string]$voce.Target
    [System.IO.Directory]::Delete($voce.FullName, $false)   # solo il collegamento, non la cartella a cui puntava
    Copia $bersaglio $voce.FullName
    "progetto: $($voce.Name) ora è una copia di $bersaglio"
  } elseif ($fonti.ContainsKey($voce.Name)) {
    Copia $fonti[$voce.Name] $voce.FullName
    "progetto: $($voce.Name) aggiornata"
  }
}

# 2. Copie di Hermes.
$hermes = "$env:LOCALAPPDATA\hermes\skills"
foreach ($s in $fonti.Keys) {
  Copia $fonti[$s] (Join-Path $hermes $s)
  "hermes: $s aggiornata"
}
Get-ChildItem $progetto, (Join-Path $hermes 'tarots-*') -ErrorAction SilentlyContinue |
  Select-Object FullName, LinkType | Format-Table -AutoSize | Out-String -Width 200
