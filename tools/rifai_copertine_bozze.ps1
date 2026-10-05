# Rifà le copertine delle BOZZE del blog con Hermes: un articolo per volta, ognuno in una sessione nuova di Hermes
# (contesto pulito), con il ciclo deterministico skills\tarots-blog-images\scripts\redo_covers_loop.py.
# Si lancia a mano. Valori predefiniti del ciclo: 10 articoli per giro, 15 minuti al massimo per articolo, stop dopo
# 2 fallimenti di fila, 20 crediti contati per articolo (copertina + un solo nuovo tentativo).
# Il ciclo scrive una riga per articolo in %USERPROFILE%\.tarots-blog\loop-covers-log.jsonl (esito, motivo, durata,
# crediti prima e dopo) e l'output di Hermes in %USERPROFILE%\.tarots-blog\loop-covers\; questo script salva lì anche
# tutto quello che compare a video (giro-<data>.txt).
# Rilanciato, riparte da dove si era fermato. Prima la prova, che non lancia Hermes:
#   .\tools\rifai_copertine_bozze.ps1 -Prova
# Prima del primo giro: tools\aggiorna_skill_hermes.ps1, perché Hermes legga la versione attuale della skill.
param(
  [int]$Articoli = 10,   # articoli in questo giro
  [int]$Budget = 0,      # crediti LitMedia al massimo per questo giro (0 = nessun tetto oltre al saldo)
  [int]$Riserva = 0,     # crediti che devono restare sul conto
  [switch]$Prova         # solo l'elenco e il prompt del primo articolo: niente Hermes, niente crediti
)
$repo = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repo 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = (Get-Command python -ErrorAction Stop).Source }
$ciclo = Join-Path $repo 'skills\tarots-blog-images\scripts\redo_covers_loop.py'
$cartella = Join-Path $env:USERPROFILE '.tarots-blog\loop-covers'
New-Item -ItemType Directory -Force $cartella | Out-Null
$uscita = Join-Path $cartella ('giro-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt')

$argomenti = @($ciclo, '--limit', $Articoli, '--reserve', $Riserva)
if ($Budget -gt 0) { $argomenti += @('--budget', $Budget) }
if ($Prova) { $argomenti += '--dry-run' }

$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
# 'Continue': le righe del ciclo su stderr (error: ...) si mostrano e si salvano, non fermano lo script.
$ErrorActionPreference = 'Continue'
& $python @argomenti 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $uscita
$codice = $LASTEXITCODE
"output salvato in $uscita (codice di uscita ${codice}: 0 finito, 3 fermo per fallimenti, 4 lettura blog/saldo, 5 Hermes non trovato)"
exit $codice
