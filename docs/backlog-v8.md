# Backlog v8 — Analytics e statistiche

Registrato verbatim dalle istruzioni dell'operatore (2026-09-29), dettate durante l'implementazione
di v7. **In coda dopo v7**: non ancora pianificato in fasi, non ancora esplorato nel codice.

## 1. Statistiche di ingresso (traffico)

Provenienza del traffico, utenti già registrati vs nuovi, utenti che ritornano sulla pagina, tempi
medi fra le visite, luogo di connessione (geolocalizzazione), tempo di permanenza sul sito, pagine
visitate per utente, pagine più visitate in totale nel tempo (assoluto, ultima settimana, ultimo
mese, ultimi X mesi, dinamica di visita alle pagine nel tempo), funzioni più utilizzate, utenti che
entrano e poi si registrano (dopo quante visite, in percentuale). Altre informazioni tipiche di
questo tipo di analisi (da determinare in fase di progettazione).

## 2. Statistiche utenti

Fasce di età, sesso, cosa comprano, provenienza (se disponibile, da IP o altro), incroci fra età /
sesso / provenienza / campagna (referral o ID campagna) e media per campagna. Funzioni più usate,
pagine più visitate. Altri dati tipici di questo genere di statistiche.

## 3. Grafici interattivi e incrocio dinamico dei dati

Statistiche di entrate e utenti con grafici adeguati e interattivi; possibilità di incrociare i dati
dinamicamente per studi ad hoc (non solo viste precostituite).

## 4. Export ed invio automatico

- Export dei dati visualizzati (qualunque vista/grafico corrente).
- Export di collezioni di dati standard — da determinare quali sono utili esportare
  automaticamente in fase di progettazione.
- Cron job che invia questi dati a una lista di email in automatico ogni domenica notte.

## 5. Ricerca di mercato

Ricerca online su quali funzioni e quale raccolta dati offrono i pacchetti commerciali per analisi
degli ingressi (web analytics) e analisi clienti (CRM/customer analytics) — da fare come parte della
progettazione, prima di scegliere cosa costruire.

## 6. Google Colab per BI e interpretazione automatica

Idea dell'operatore (2026-09-29): esportare dati verso Google Colab (https://colab.research.google.com)
e predisporre notebook/algoritmi di analisi per business intelligence e interpretazione automatica.
Due modalità coesistenti: apertura diretta del link Colab, e importazione dei risultati delle analisi
fra le statistiche della GUI admin.

Obiettivi indicati per i notebook: ottimizzare le campagne, rafforzare le aree del sito di maggiore
interesse per il pubblico, analizzare gli utenti (inclusi quelli che si iscrivono e quelli già
iscritti), ottimizzare la conversione da uso gratuito ad acquisto di pacchetti/abbonamenti,
individuare mercati in crescita/dominanti — in generale, tutto ciò che è utile per la crescita.

**Valutazione (2026-09-29, non dall'operatore)**: Colab è adatto all'analisi esplorativa ad-hoc
(coorti, funnel di conversione, segmentazione, trend), ma richiede l'apertura manuale di un umano —
non copre da solo il cron job automatico del punto 4 (invio email ogni domenica notte), che resta
un'automazione separata nella propria infrastruttura. L'importazione dei risultati in GUI admin è il
pezzo più delicato: serve un endpoint admin che accetti un export (con autenticazione/firma) dal
notebook, non solo l'apertura del link. Da trattare come un canale complementare all'automazione del
punto 4, non un sostituto.

## Nota

Non ancora esplorato nel codice: da verificare se esiste già una qualche raccolta dati (log
richieste, tabella `audit_log`, ecc.) riusabile come base, o se va costruita da zero una pipeline di
tracciamento eventi. Data la portata (paragonabile a v6/v7), andrà pianificato a fasi separatamente,
con probabile bisogno di decisioni preliminari dell'operatore su: quali dati si è disposti a
raccogliere (privacy/GDPR, vedi v7 punto 5), se usare uno strumento esistente (self-hosted tipo
Plausible/Umami/PostHog) invece di costruire tracciamento e dashboard da zero, e il formato/mittente
delle email automatiche del punto 4.
