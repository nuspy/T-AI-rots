# Rifà le copertine delle BOZZE del blog con Hermes: un articolo per volta, ognuno in una sessione nuova di Hermes
# (contesto pulito), con il ciclo deterministico skills\tarots-blog-images\scripts\redo_covers_loop.py.
# Con -SenzaCopertina prende anche gli articoli che una copertina non ce l'hanno proprio, in qualunque stato (anche
# pubblicati, come «Wheel of Fortune»), oltre alle bozze. Con -Sezioni fa le immagini delle sezioni del Journal che
# non ne hanno una (circa 25), con -Stese le illustrazioni delle stese (19): 10 crediti a immagine, 20 contati per
# ciascuna nel budget (immagine + un solo nuovo tentativo). Le sezioni e le stese si lanciano solo col via
# dell'operatore: in tutto circa 440 crediti.
# Si lancia a mano. Valori predefiniti del ciclo: 10 elementi per giro, 15 minuti al massimo per ciascuno, stop dopo
# 2 fallimenti di fila.
# Il ciclo scrive una riga per elemento in %USERPROFILE%\.tarots-blog\loop-covers-log.jsonl (esito, motivo, durata,
# crediti prima e dopo) e l'output di Hermes in %USERPROFILE%\.tarots-blog\loop-covers\; questo script salva lì anche
# tutto quello che compare a video (giro-<data>.txt).
# Rilanciato, riparte da dove si era fermato. Prima la prova, che non lancia Hermes:
#   .\tools\rifai_copertine_bozze.ps1 -Prova
#   .\tools\rifai_copertine_bozze.ps1 -SenzaCopertina -Prova
#   .\tools\rifai_copertine_bozze.ps1 -Sezioni -Articoli 25 -Budget 500 -Prova
#   .\tools\rifai_copertine_bozze.ps1 -Stese -Articoli 19 -Budget 380 -Prova
# Prima del primo giro: tools\aggiorna_skill_hermes.ps1, perché Hermes legga la versione attuale della skill.
param(
  [int]$Articoli = 10,      # elementi (articoli, sezioni o stese) in questo giro
  [int]$Budget = 0,         # crediti LitMedia al massimo per questo giro (0 = nessun tetto oltre al saldo)
  [int]$Riserva = 0,        # crediti che devono restare sul conto
  [switch]$SenzaCopertina,  # anche gli articoli senza copertina, in qualunque stato (oltre alle bozze da rifare)
  [switch]$Sezioni,         # le immagini delle sezioni del Journal che non ne hanno una, invece degli articoli
  [switch]$Stese,           # le illustrazioni delle stese che non ne hanno una, invece degli articoli
  [switch]$Prova            # solo l'elenco e il prompt del primo elemento: niente Hermes, niente crediti
)
if ($Sezioni -and $Stese) { throw "Una cosa per giro: -Sezioni oppure -Stese, non tutte e due." }
if ($SenzaCopertina -and ($Sezioni -or $Stese)) { throw "-SenzaCopertina vale per gli articoli, non con -Sezioni o -Stese." }
$repo = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repo 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = (Get-Command python -ErrorAction Stop).Source }
# La copia di Hermes (aggiornata a mano con tools\aggiorna_skill_hermes.ps1), non l'originale del repository: così anche
# i comandi che il ciclo scrive nel prompt di Hermes puntano alle sue copie (decisione dell'operatore, 5/10).
$ciclo = Join-Path $env:LOCALAPPDATA 'hermes\skills\tarots-blog-images\scripts\redo_covers_loop.py'
if (-not (Test-Path $ciclo)) { throw "Manca la copia di Hermes della skill: lancia prima tools\aggiorna_skill_hermes.ps1" }
$cartella = Join-Path $env:USERPROFILE '.tarots-blog\loop-covers'
New-Item -ItemType Directory -Force $cartella | Out-Null
$uscita = Join-Path $cartella ('giro-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt')

$argomenti = @($ciclo, '--limit', $Articoli, '--reserve', $Riserva)
if ($Budget -gt 0) { $argomenti += @('--budget', $Budget) }
if ($SenzaCopertina) { $argomenti += '--missing' }
if ($Sezioni) { $argomenti += '--sections' }
if ($Stese) { $argomenti += '--spreads' }
if ($Prova) { $argomenti += '--dry-run' }

$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
# 'Continue': le righe del ciclo su stderr (error: ...) si mostrano e si salvano, non fermano lo script.
$ErrorActionPreference = 'Continue'
& $python @argomenti 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $uscita
$codice = $LASTEXITCODE
"output salvato in $uscita (codice di uscita ${codice}: 0 finito, 2 opzioni sbagliate, 3 fermo per fallimenti, 4 lettura blog/saldo, 5 Hermes non trovato)"
exit $codice
