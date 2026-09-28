# Backlog v6 — richieste rimandate

Funzionalità richieste dall'utente ma esplicitamente rimandate a un rilascio futuro (v6), non ancora
iniziate. Registrate qui perché non vadano perse tra una sessione e l'altra.

---

## 1. Richiamo "leggi le tue carte" in home — da verificare/rafforzare

L'utente segnala: manca sulla home page il richiamo a "leggi le tue carte" — una delle funzioni
distintive del sito. **Nota di verifica**: un banner per questa funzione esiste già nel codice
(`frontend/app/componenti/banner-interpreta.tsx`, collegato a `/interpreta`, la funzione "Interpreta
i miei tarocchi" della Fase C di v5) ed è presente in `app/page.tsx`; confermato anche in produzione
(`https://tarots.chat/` contiene il link `/interpreta` dopo il deploy v5). Non è quindi assente dal
codice — ma l'utente lo percepisce come mancante, il che suggerisce che vada reso più visibile/
prominente, oppure che si riferisca a qualcos'altro con lo stesso nome informale. Da chiarire con
l'utente prima di intervenire: cosa esattamente manca (posizione, visibilità, testo, un concetto
diverso da "Interpreta i miei tarocchi").

**Risolto in sessione** (non è più un item di backlog, lasciato qui come cronologia): il banner
c'era ma dopo troppo scroll (in fondo a tutta la sezione `Soglia` — hero, carta del giorno, come
funziona, stese, mazzi, rigore — prima di arrivare a `BannerInterpreta` in `page.tsx`). Spostato
dentro `Soglia`, subito dopo la sezione "carta del giorno" (`frontend/app/soglia.tsx`).

## 2. Memoria RAG per utente + chat proattiva con proposta di lettura

Sistema di memoria persistente per utente, usata sia nelle letture sia in una nuova chat proattiva.

### Memoria RAG
- Memorizza le domande dell'utente e le risposte/letture, per **riusarle** invece di riformularle
  sempre uguali, o per chiedere esplicitamente se ci sono **evoluzioni** rispetto alla volta
  precedente sullo stesso tema.
- Distingue **condizioni variabili** da condizioni **stabili**: esempio dato dall'utente — se
  all'utente manca una gamba, il sistema se ne ricorda e non richiede più in futuro se ha handicap
  fisici, né se "gli è ricresciuta la gamba" (non richiede conferma su fatti stabili già noti).
- Un **campo di attinenza** per ogni memoria, usato per estrarre dal contesto passato solo ciò che è
  pertinente al tema corrente (dove si hanno già informazioni, o si vogliono aggiornamenti).
- La **formulazione della risposta finale** tiene conto delle memorie: fa comparazioni esplicite con
  letture precedenti sullo stesso tema (cambiamenti, evoluzioni, peggioramenti), mostrando che il
  sistema "conosce" l'utente nel tempo.

### Chat proattiva (solo utenti loggati)
- Uno spazio chat fisso nella parte inferiore della pagina, visibile solo a chi ha fatto login.
- L'AI **inizia da sola** la conversazione:
  - dopo X minuti di inattività senza risposta dell'utente (X **configurabile da GUI admin**);
  - oppure alla fine di una conversazione precedente, con un'altra domanda/proposta per creare
    interazione, basandosi sulle memorie dell'utente.
- Un **suono delicato ("chime")** viene emesso a ogni inizio di comunicazione automatica dell'AI,
  per attirare l'attenzione dell'utente. Deve essere **disattivabile** con un'icona switch/
  altoparlante visualizzata nella chat.
- Durante la conversazione, l'AI può proporre una lettura sul tema in corso, mostrando un **bottone
  in chat**: "Leggi le carte per: $argomento di cui si sta parlando".
  - Il bottone apre la sezione di selezione dello schema di lettura, **filtrata per pertinenza**
    (es. tema amoroso → schemi relativi + compatibilità).
  - L'AI **precompila la domanda** della lettura in base al discorso appena fatto, ma **senza
    inviarla**: resta modificabile dall'utente prima di procedere. Da lì in poi il flusso è quello
    di una lettura normale.

### Gestione memoria in scheda utente (profilo)
Nuova sezione/tab "Memoria" nel profilo utente:
- Elenco delle memorie precedenti, leggibili.
- Ogni memoria ha, in piccole icone in alto a destra (con tooltip i18n):
  - una **checkbox** di selezione (per cancellazione multipla),
  - un'icona **cestino** per cancellare quella singola memoria,
  - un'icona **penna** per modificarla.
- In fondo al tab, un bottone fisso: **"Cancella memorie selezionate"** (se ce ne sono di
  selezionate) altrimenti **"Cancella tutte le memorie"** — con un **dialog di doppia conferma**,
  tutto i18n.

**Nota di scope**: richiesta grande e articolata (RAG, chat proattiva, pianificazione automatica
lato admin, UI di gestione memoria) — non ancora iniziata, da pianificare come più fasi quando si
arriva a v6.
