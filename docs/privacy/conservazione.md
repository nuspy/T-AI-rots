# Tempi di conservazione e cancellazione

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

Quanto si tiene ogni dato, come si cancella, cosa resta dopo la cancellazione dell'account. Il codice che applica
queste regole: `tarot/cancellazione.py`, `tools/cancellazioni.py` (CronJob `tarots-cancellazioni`),
`api/routers/admin_conservazione.py` (console «Conservazione dati»), `tarot/backup.py`, libreria `lanterna`.

## La decisione su letture e chat

L'operatore ha deciso: letture (anche anonime) e chat con l'oracolo si conservano **senza scadenza automatica**,
«fino a cancellazione dell'interessato o dell'amministratore». Nessuna pulizia notturna: la console mostra quante righe
ci sono per fascia d'età (meno di 30 giorni, fino a 6 mesi, fino a 1 anno, fino a 2 anni, oltre) e l'amministratore
cancella a mano.

Motivo dichiarato: le letture sono la storia personale della persona, che ci torna sopra e su cui si basano memoria e
letture successive.

**Nota per il consulente.** L'art. 5.1.e chiede che i dati si conservino «per un arco di tempo non superiore al
conseguimento delle finalità» e l'art. 13.2.a chiede di indicare il periodo o i criteri per determinarlo. «Fino a
cancellazione» è un criterio, ma regge per gli account attivi più che per:

- gli account **inattivi da anni**;
- le **letture anonime**, che il visitatore non può cancellare da sé e che restano legate a un cookie di un anno.

Proposte da valutare: cancellare (o avvisare e poi cancellare) gli account inattivi da N anni; cancellare le letture
anonime dopo N mesi. **`TODO_OPERATORE: confermare la decisione «senza scadenza» o fissare N, con motivazione scritta`**.

## Tabella

| Dato | Dove | Conservazione | Come si cancella | Dopo la cancellazione dell'account |
|---|---|---|---|---|
| Scheda dell'account (email, nomi, nascita, genere, lingua, preferenze, posizione attuale) | `users`, Keycloak | Fino alla cancellazione dell'account | Campi dal profilo; account dal profilo | Riga pseudonimizzata (campi vuoti, identificativo Keycloak che non corrisponde a nessuno); utente Keycloak cancellato |
| Dati importati dai social e loro provenienza | `users.dati_social` | Come la scheda | Dal profilo, anche tutti in un colpo | Cancellati |
| Casella «trans» (persona e partner ricordato) | `users`, `readings.persone` | Fino alla revoca di `dati_particolari` o alla cancellazione | Revoca del consenso: nella scheda e nel partner ricordato si spegne subito; nelle istantanee delle letture già fatte resta (racconto di allora) ma non arriva più al modello, e si cancella con la lettura | Cancellata con la scheda e le letture |
| Partner ricordato | `users.partner_ricordato` | Fino a cancellazione | Dal profilo | Cancellato |
| Letture registrate (quesito, intervista, carte, responso, diario, feedback) | `readings`, `interview_turns`, `drawn_cards` | **Senza scadenza** | Singola lettura dalla storia (cancellazione vera, in cascata); amministratore dal database | Cancellate |
| Immagine e dati di condivisione di una lettura (impronte di clic e visite) | `share_*` | Come la lettura | Con la lettura | Cancellati |
| Letture anonime | `readings` con `anon_id` | **Senza scadenza** | Console, voce `letture_anonime`. Il visitatore non ha un pulsante: **`TODO_OPERATORE: aggiungerlo o indicare nell'informativa la richiesta via email`** | — |
| Cookie `tarots_anon` | Browser | Un anno | Dal browser | — |
| Memorie del lettore | `user_memories` | Fino a cancellazione | Da «La mia storia»; quelle sulla salute alla revoca di `dati_particolari` | Cancellate |
| Chat con l'oracolo | `chat_proattiva_turni` | **Senza scadenza** | Console, voce `chat_proattiva`; con l'account | Cancellata |
| Carte del giorno | `daily_cards` | Fino a cancellazione | Con l'account | Cancellate |
| Avatar e nome pubblico | `media_images`, `users` | Fino a modifica | Dal profilo | Cancellati |
| Indirizzi di spedizione salvati | `indirizzi_spedizione` | Fino a cancellazione | Dal profilo | Cancellati |
| Temi suggeriti per i mazzi | `deck_suggestions` | Fino a cancellazione | Con l'account | Cancellati |
| Voti sui mazzi | `deck_votes` | Fino a cancellazione | — | Restano, legati allo pseudonimo |
| Contabilità: registro dei crediti, abbonamenti, pagamenti, ordini, coupon usati, mazzi sbloccati, premi da inviti | `credit_ledger`, `subscriptions`, `payment_*`, `ordini`, `coupon_redemptions`, `deck_unlocks`, `share_signups` | **10 anni** (art. 2220 c.c.). **`TODO_OPERATORE: confermare col commercialista termini e decorrenza`** | Non dall'utente: obbligo di legge | Restano, **pseudonimizzati**. Degli ordini resta il paese di spedizione (IVA), non l'indirizzo |
| Consensi correnti | `user_consents` | Finché valgono | Cambiando la scelta | Cancellati |
| Storico dei consensi e conferma dell'età | `consensi_storico` | Prova del consenso. **`TODO_OPERATORE: fissare N anni (proposta: 5 dopo la fine del rapporto)`** | Console, voce `consensi_storici` (oltre N anni; mai l'ultima scelta per persona e tipo) | Restano, legati allo pseudonimo |
| Registro (`audit_log`) | `audit_log` | **Senza scadenza**; IP già troncati con impronta | Console, voce `ip_audit`: toglie IP e impronte, le righe restano | Restano, legate allo pseudonimo |
| Log dei pod e del proxy (IP interi) | k3s, Nginx Proxy Manager | **`TODO_OPERATORE: verificare la rotazione (proposta: 30 giorni)`** | Rotazione | — |
| Statistiche interne (visite ed eventi) | Tabelle `lanterna` | Dettaglio **25 mesi**, poi solo totali giornalieri anonimi | Opposizione dal profilo: il legame con l'account si toglie | Il legame con l'account si toglie |
| Sale dell'impronta giornaliera | Tabelle `lanterna` | 48 ore | Automatico | — |
| Identificativo del browser (statistiche estese) | Browser e tabelle `lanterna` | Fino alla revoca | Revoca del consenso `statistiche` | — |
| Google Analytics 4 | Google | **`TODO_OPERATORE: 2 o 14 mesi, come impostato in GA4`** | Revoca: script fermo e cookie cancellati | — |
| Richiesta di cancellazione | `users.cancellazione_richiesta_il` | 30 giorni di ripensamento, poi esecuzione | Annullabile rientrando | Resta la data di esecuzione |
| Archivio di esportazione | Nessuno: generato al volo e consegnato | Non si conserva | — | — |
| Backup del database | NAS dell'operatore, Italia | Le **7** copie notturne più recenti (modificabile in console) e **3** copie di sicurezza pre-ripristino | Rotazione automatica dopo un caricamento verificato | Vedi sotto |

## Come si cancella

**La persona**, dal profilo:

- corregge o cancella i campi della scheda, i dati arrivati dai social, il partner ricordato, gli indirizzi, l'avatar;
- cancella una singola lettura o una memoria;
- revoca i consensi (la revoca di `dati_particolari` spegne «trans» e cancella le memorie sulla salute);
- si oppone alle statistiche collegate all'account;
- scarica i suoi dati (`GET /me/esportazione`, ZIP di JSON, una volta al giorno);
- chiede la cancellazione dell'account (`POST /me/cancellazione`): l'account si chiude subito, per 30 giorni si può
  annullare rientrando, poi il CronJob notturno cancella l'utente in Keycloak e i dati personali.

**L'amministratore**, dalla console «Conservazione dati»: letture anonime, chat, IP del registro, account in
cancellazione (anche prima dei 30 giorni), scelte storiche dei consensi oltre N anni. Ogni cancellazione passa da
un'anteprima (quante righe, la più vecchia e la più recente) e da una conferma che ripete il numero; se i dati sono
cambiati nel frattempo si ferma. Ogni esecuzione resta nel registro.

**Richieste via email** (visitatori anonimi, persone senza accesso all'account): **`TODO_OPERATORE: procedura,
verifica dell'identità, risposta entro un mese`**.

## Cosa resta dopo la cancellazione dell'account, e perché

| Cosa resta | Perché | Base |
|---|---|---|
| Contabilità pseudonimizzata (crediti, abbonamenti, pagamenti, ordini, coupon, mazzi sbloccati, premi da inviti) | Obbligo di conservare le scritture contabili | Art. 6.1.c; art. 2220 c.c. (10 anni); norme IVA. **`TODO_OPERATORE: conferma del commercialista`** |
| Paese di spedizione degli ordini | IVA sulle vendite a distanza | Art. 6.1.c |
| Registro (`audit_log`) e storico dei consensi, legati allo pseudonimo | Prova di ciò che è stato fatto (consensi, cancellazione) | Art. 5.2, art. 7.1 |
| Voti sui mazzi, legati allo pseudonimo | Totali dei turni di voto | Art. 6.1.f. **`TODO_OPERATORE: valutare se cancellarli`** |
| Statistiche senza legame con l'account | Dati non più riferibili alla persona | — |

## Backup

I dati cancellati restano nelle copie di backup già fatte **fino alla loro rotazione**: con 7 copie notturne, al più
circa una settimana dopo la cancellazione; le 3 copie di sicurezza pre-ripristino possono essere più vecchie, perché
ruotano solo a ogni nuovo ripristino.

**`TODO_OPERATORE`**:

- confermare il numero di copie impostato in console;
- dire se il NAS ha altre copie (snapshot, dischi esterni, cloud) e con quale rotazione;
- decidere una durata massima per le copie di sicurezza pre-ripristino;
- procedura dopo un ripristino: rieseguire le cancellazioni avvenute dopo la data della copia (le richieste in
  `audit_log` e le cancellazioni della console), così che un ripristino non faccia «risorgere» dati cancellati.
