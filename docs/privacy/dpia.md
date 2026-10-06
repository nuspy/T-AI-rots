# Valutazione d'impatto sulla protezione dei dati (art. 35 GDPR)

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

Oggetto: il servizio TAROTS chat nel suo insieme (letture dei tarocchi con modelli linguistici, memoria, chat,
account, pagamenti, statistiche). Le schede dei singoli trattamenti sono in `registro-trattamenti.md`; i fornitori in
`responsabili.md`; i tempi in `conservazione.md`.

## 1. Perché serve

La DPIA è obbligatoria quando un trattamento può presentare un rischio elevato (art. 35.1). Le linee guida WP248
indicano che due criteri bastano di norma a richiederla; qui ne ricorrono almeno quattro, e l'elenco del Garante
(provv. n. 467 dell'11 ottobre 2018) include sia i trattamenti con tecnologie innovative sia quelli su dati di soggetti
vulnerabili.

| Criterio | Perché ricorre |
|---|---|
| Dati sensibili o di natura molto personale | Nei testi liberi (quesito, intervista, chat) le persone scrivono di salute, vita sessuale, orientamento, identità di genere, lutti, crisi. La casella «persona trans» è un dato art. 9 esplicito. Le letture stesse sono dati intimi. |
| Soggetti vulnerabili | Possibili minori (età minima auto-dichiarata) e persone in difficoltà emotiva che cercano risposte nelle carte. |
| Uso innovativo di tecnologie | Modelli linguistici (LLM) di terzi che leggono i testi, estraggono memorie e conducono la conversazione. |
| Trasferimenti e terzi | I testi vanno a fornitori LLM spesso fuori dall'UE; server nel Regno Unito. |
| Profilazione leggera | La memoria del lettore costruisce nel tempo un quadro della persona per personalizzare le letture. |

## 2. Descrizione sistematica

### 2.1 Il flusso

1. Il browser (o l'app) parla con `tarots.chat`: Nginx Proxy Manager con HTTPS, poi il sito Next.js e l'API FastAPI
   su un cluster k3s a nodo singolo, a Londra.
2. L'identità è in Keycloak self-hosted (password, 2FA facoltativa, accesso con Google, Apple, Facebook, GitHub,
   Microsoft, LinkedIn).
3. La persona scrive il quesito; l'oracolo fa da 2 a 6 domande di contesto; le carte si estraggono con un impegno
   crittografico; il modello interpreta e scrive il responso; un secondo modello (giudice) lo controlla.
4. Ogni chiamata al modello passa da un involucro che sostituisce i nomi noti con «Persona_N»; il cognome del partner
   non entra mai nel prompt; la casella «trans» entra solo con il consenso `dati_particolari`.
5. Dopo la lettura un modello estrae le memorie; la ricerca usa vettori numerici calcolati da un modello di embedding.
6. Tutto si salva in PostgreSQL nel cluster; ogni notte una copia va sul NAS dell'operatore in Italia.
7. Le statistiche interne (`lanterna`) contano visite ed eventi senza IP; GA4 e AdSense si caricano solo con i loro
   consensi.

### 2.2 Compiti affidati ai modelli

Intervista, validazione delle domande, interpretazione, sintesi, giudizio del responso, estrazione delle memorie,
embedding, chat con l'oracolo, analisi dei dati (solo aggregati); più compiti senza dati degli utenti (traduzione degli
articoli e della base di conoscenza, creazione dei mazzi). Ogni compito si assegna dalla console a un fornitore della
tabella `llm_providers`.

Elenco dei fornitori attivi e paesi: vedi console → Impostazioni → Dati del titolare (letto dai fornitori attivi in «Modelli», dove sono anche i compiti
assegnati a ciascuno; il predefinito, secondo la memoria dell'operatore, è NVIDIA).

### 2.3 Volumi

**`TODO_OPERATORE: utenti registrati, letture al mese, paesi principali`**. Servono a valutare la «larga scala»
(art. 35.3.b e art. 37.1.c).

### 2.4 Conservazione

Decisione dell'operatore: letture (anche anonime) e chat **senza scadenza automatica**, fino a cancellazione
dell'interessato o dell'amministratore. Dettagli in `conservazione.md`.

## 3. Necessità e proporzionalità

| Principio | Come è rispettato | Cosa resta aperto |
|---|---|---|
| Finalità determinate | Ogni trattamento ha una finalità scritta nel registro. | — |
| Base giuridica | Contratto per il servizio; consensi separati per statistiche estese, GA4, pubblicità, testi, dati art. 9, marketing; legittimo interesse per le statistiche collegate all'account (`lia-analytics.md`). | Base art. 9 per i dati sensibili scritti nel testo libero (rischio R3); dato art. 9 del partner (R4). |
| Minimizzazione | Pseudonimi verso i modelli; niente cognome del partner; IP troncati con impronta; statistiche senza contenuti, senza IP, con soglia k≥5 negli aggregati; nessun dato di carta sul server. | Il testo libero può contenere nomi che il sistema non conosce: partono come sono. |
| Esattezza | La persona corregge la scheda, le memorie, i dati importati dai social. | — |
| Limitazione della conservazione | Cancellazione manuale con anteprima e registro; statistiche 25 mesi; backup a rotazione. | Letture e chat senza scadenza (R9). |
| Integrità e riservatezza | Misure M1–M8 del registro. | Backup non cifrati (R8); log con IP interi (R11); server condiviso (R7). |
| Trasparenza | Pagina «Metodo e privacy», banner con consensi granulari, versione dell'informativa salvata con ogni scelta. | **`TODO_OPERATORE: allineare l'informativa pubblica a questi documenti`**: il 2026-10-03 i testi della pagina Privacy v2 contengono ancora la voce «Condivisione dati con i partner» e parlano di consenso ai «cookie» invece dei consensi granulari. |
| Diritti | Esportazione ZIP e cancellazione dal profilo; opposizione alle statistiche in un clic; revoca di ogni consenso. | Visitatori anonimi senza pulsante per cancellare la propria lettura; revoca del token Apple (Fase 6); procedura per le richieste via email. |
| Responsabili e trasferimenti | Elenco in `responsabili.md`. | Nessun DPA risulta firmato o verificato (R1, R2). |

## 4. Rischi e misure

Scala: probabilità e gravità **bassa / media / alta**. «Residuo» è il livello dopo le misure già in opera.

| # | Rischio per le persone | Prob. | Grav. | Misure in opera | Residuo |
|---|---|---|---|---|---|
| R1 | Il fornitore LLM legge, conserva o usa per addestramento testi intimi (anche art. 9). | Media | Alta | Pseudonimi dei nomi noti; cognome mai; «trans» solo con consenso; memorie sulla salute solo con consenso; nessun dato anagrafico oltre il necessario. | **Media** finché i termini dei fornitori (niente addestramento, conservazione breve) non sono verificati e firmati. |
| R2 | Trasferimento verso paesi senza adeguatezza. Il catalogo della console propone anche fornitori con sede in Cina o con endpoint a Singapore (DeepSeek, Moonshot, Alibaba DashScope, Z.ai). | Media | Alta | Nessuna tecnica: dipende da quali fornitori l'operatore accende. | **Alta** se uno di questi riceve testi degli utenti; **bassa** se sono usati solo per compiti senza dati utente. Azione A2. |
| R3 | Dati art. 9 scritti spontaneamente nel testo libero trattati senza una base art. 9 dichiarata. | Alta | Media | Il contenuto non entra nelle statistiche; il segnale di crisi si conta senza utente; cancellazione della lettura vera. | **Media**: questione di base giuridica, da decidere col consulente (azione A3). |
| R4 | La casella «trans» del partner e i suoi dati (nome, genere, nascita) sono dati di un terzo che non ha scelto; «trans» è un dato art. 9 che il consenso di chi consulta non copre. | Media | Media | Al modello: niente cognome, nome pseudonimizzato, «trans» solo col consenso di chi consulta; nella condivisione il nome diventa «qualcuno di speciale». | **Media**. Azione A4. |
| R5 | Minori che usano il servizio, comprano o confidano temi intimi. | Media | Alta | Età minima per paese (IT/ES 14, FR 15, altri 16) confermata al primo accesso e prima della lettura anonima, con prova nello storico; data di nascita più forte della casella. | **Media**: l'auto-dichiarazione si aggira. Il consulente valuti se alzare la soglia a 18 anni per acquisti e contenuti intimi (si cambia in `tarot/eta_minima.py`). |
| R6 | Persona in crisi (autolesionismo) che riceve una risposta inadatta, o il cui stato viene registrato. | Bassa | Alta | Filtro deterministico prima delle carte e sull'uscita: la lettura si ferma, si danno contatti d'aiuto, il credito si restituisce; giudice sul responso; registrazione solo come conteggio senza utente; nel registro dei crediti il rimborso dice solo «lettura sospesa». | **Bassa–media**: un filtro a parole non coglie tutto; il testo scritto resta nella lettura annullata, nella storia della persona (cancellabile da lei). |
| R7 | Accesso non autorizzato al database (attacco, errore di configurazione, altro servizio compromesso sullo stesso server). | Media | Alta | Database non esposto; HTTPS; segreti nei Secret; chiavi LLM cifrate; registro append-only; 2FA disponibile. | **Media**: server a nodo singolo condiviso con altri servizi e PostgreSQL condiviso. Azione A7. |
| R8 | Furto o accesso al NAS con i backup in chiaro. | Bassa | Alta | NAS dell'operatore, SFTP con chiave dell'host verificata, rotazione a 7 copie. | **Media**. Azione A8 (cifratura dei dump). |
| R9 | Accumulo di letture e chat senza scadenza: più dati esposti in caso di violazione; possibile contrasto con l'art. 5.1.e. | Alta | Media | Cancellazione da parte della persona (lettura singola o account) e dell'amministratore dalla console. | **Media**. Azione A9. |
| R10 | Re-identificazione dalle statistiche o dalle analisi automatiche. | Bassa | Media | Nessun IP, categorie larghe, soglia k≥5 negli aggregati, 25 mesi di dettaglio, opposizione. | **Bassa**. |
| R11 | IP interi nei log dei pod (uvicorn) e di Nginx Proxy Manager, senza durata documentata. | Alta | Bassa | Nessuna specifica. | **Media**. Azione A11. |
| R12 | Presa di un account altrui tramite un social con la stessa email. | Bassa | Alta | Unione da confermare: Keycloak toglie i vecchi accessi di un account mai verificato e chiede alla persona; separazione dei dati se l'account non era suo. | **Bassa**. |
| R13 | Uso futuro dei testi per il blog con frasi riconoscibili. | Media | Alta | Consenso separato `testi_statistiche`; regole in `testi-statistiche.md` (anonimizzazione, k≥5, mai citazioni, esclusione dei testi sensibili). Oggi nessuna estrazione. | **Bassa** se le regole si applicano; da rivalutare prima del rilascio. |
| R14 | Accesso degli amministratori alle letture oltre il necessario. Dalla v9.5 (decisione dell'operatore del 6/10/2026) la console può mostrare, per ragioni di sicurezza, letture, intervista, chat, memorie e dati di profilazione di un utente. | Media | Alta | Console riservata al ruolo `admin`; i contenuti si aprono solo scrivendo un motivo (accesso di 30 minuti, per quell'utente e quell'amministratore); ogni accesso e ogni scheda letta restano nel registro append-only (`admin.contenuti.accesso` / `admin.contenuti.lettura`), visibile nella scheda dell'utente; non escono stato del mazzo, vettori delle memorie, token dei dispositivi; l'informativa lo dichiara (sezione «Letture»). | **Media**: dipende dalla disciplina degli amministratori e dalla revisione del registro. Azioni A14 e A15. **`TODO_OPERATORE: il consulente confermi la base giuridica (art. 6.1.f e, per i dati art. 9, la deroga applicabile) e se serve aggiornare la versione dell'informativa (oggi «v1») per chiedere di nuovo il consenso.`** |
| R15 | Effetti sulle decisioni personali (la persona prende per vera una «previsione»). | Media | Media | Il servizio dichiara che l'AI non conosce il futuro e che nessuna lettura è una previsione; guardrail sul responso. | **Bassa–media**. |

## 5. Azioni aperte

| # | Azione | Chi | Stato |
|---|---|---|---|
| A1 | Verificare e firmare (o accettare) i DPA di tutti i responsabili; per i fornitori LLM verificare per iscritto: niente addestramento sui dati, durata di conservazione dei prompt, sede del trattamento. | Operatore | **`TODO_OPERATORE`** |
| A2 | Non assegnare compiti con dati degli utenti a fornitori in paesi senza adeguatezza; se necessario, clausole tipo più valutazione del trasferimento (TIA). | Operatore + consulente | **`TODO_OPERATORE`** |
| A3 | Decidere la base art. 9 per i dati sensibili nel testo libero (per esempio: consenso esplicito prima della prima lettura, con avviso chiaro che il testo va a un modello di terzi; oppure altra soluzione indicata dal consulente). | Consulente | **`TODO_OPERATORE`** |
| A4 | Decidere sulla casella «trans» del partner: toglierla, oppure tenerla con una base giuridica che il consulente ritenga valida. | Operatore + consulente | **`TODO_OPERATORE`** |
| A5 | Confermare le soglie d'età (o alzarle a 18 per acquisti e contenuti intimi). | Consulente | **`TODO_OPERATORE`** |
| A6 | Revoca del token «Accedi con Apple» alla cancellazione dell'account. | Sviluppo | Rimandata alla Fase 6 |
| A7 | Separare il database del servizio dagli altri servizi del server (utente e database dedicati, permessi minimi); 2FA obbligatoria per gli amministratori; aggiornamenti di sicurezza documentati. | Operatore | **`TODO_OPERATORE`** |
| A8 | Cifrare i dump prima dell'invio al NAS (chiave fuori dal NAS e fuori dal database). | Sviluppo | **`TODO_OPERATORE`** |
| A9 | Motivare la conservazione «senza scadenza» di letture e chat, o fissare una durata (per esempio cancellazione dopo N anni di inattività dell'account e N mesi per le letture anonime). | Operatore + consulente | **`TODO_OPERATORE`** |
| A10 | Allineare l'informativa pubblica (consensi granulari, niente «partner», fornitori LLM e paesi, durata di conservazione, età minima, contatto privacy). | Operatore | **`TODO_OPERATORE`** |
| A11 | Fissare rotazione e durata dei log di k3s e di Nginx Proxy Manager (proposta: 30 giorni). | Operatore | **`TODO_OPERATORE`** |
| A12 | Pulsante di cancellazione per la lettura anonima (oggi solo via email e console). | Sviluppo | **`TODO_OPERATORE`** |
| A13 | Procedura e registro per le richieste degli interessati che arrivano via email. | Operatore | **`TODO_OPERATORE`** |
| A14 | Istruzioni scritte agli amministratori (art. 29) e accesso al database solo per manutenzione. | Operatore | **`TODO_OPERATORE`** |
| A15 | Contenuti degli utenti in console (v9.5): casi in cui è lecito aprirli (segnalazioni, abusi, richieste di supporto), revisione periodica del registro degli accessi, 2FA obbligatoria per gli amministratori. | Operatore | **`TODO_OPERATORE`** |
| A15 | Rivedere questa DPIA prima della Fase 5 (notifiche e marketing) e prima di attivare la pipeline dei testi. | Operatore | Pianificata |

## 6. Consultazione preventiva (art. 36)

La consultazione del Garante è obbligatoria solo se, **dopo le misure**, il rischio residuo resta elevato.

Valutazione tecnica di questo documento:

- con le azioni A1–A4 chiuse (DPA verificati, nessun fornitore senza adeguatezza sui dati degli utenti, base art. 9
  decisa, casella del partner risolta), il rischio residuo complessivo appare **medio** e la consultazione non
  sembrerebbe necessaria;
- se invece si mantengono fornitori LLM in paesi senza adeguatezza sui testi degli utenti, o se la base art. 9 resta
  scoperta, il rischio residuo resta **elevato** e la consultazione andrebbe considerata.

**La decisione spetta all'operatore, sentito il consulente.**

| | |
|---|---|
| Decisione sulla consultazione preventiva | **`TODO_OPERATORE: sì / no, con motivazione`** |
| Data e firma del titolare | **`TODO_OPERATORE`** |
| Parere del DPO, se nominato (art. 35.2) | **`TODO_OPERATORE`** |
| Opinione degli interessati (art. 35.9) | **`TODO_OPERATORE: raccolta o motivo per non raccoglierla`** |

## 7. Riesame

Da rivedere a ogni cambio rilevante (nuovo fornitore LLM, Fase 5, pipeline dei testi, app mobili, apertura dei
commenti del blog, cambio di hosting) e comunque una volta l'anno. Prossimo riesame: **`TODO_OPERATORE: data`**.
