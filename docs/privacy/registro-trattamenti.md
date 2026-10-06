# Registro delle attività di trattamento (art. 30 GDPR)

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

Documenti collegati: `dpia.md` (valutazione d'impatto), `responsabili.md` (fornitori e terze parti),
`conservazione.md` (tempi e cancellazione), `data-breach.md` (violazioni), `lia-analytics.md` (legittimo interesse
sulle statistiche), `testi-statistiche.md` (pipeline futura dei testi).

## Il titolare

| | |
|---|---|
| Titolare | Andrea Taini, gestore di TAROTS chat |
| Forma | Nome o ragione sociale e partita IVA/codice fiscale: vedi console → Impostazioni → Dati del titolare |
| Indirizzo postale | Vedi console → Impostazioni → Dati del titolare |
| Contatto privacy | Vedi console → Impostazioni → Dati del titolare (predefinito privacy@tarots.chat; la posta in arrivo a @tarots.chat la inoltra Namecheap) |
| DPO | Nominato sì/no e contatto: vedi console → Impostazioni → Dati del titolare. Da valutare col consulente: l'art. 37.1.c lo richiede se l'attività principale comporta un trattamento «su larga scala» di categorie particolari; oggi i dati art. 9 sono possibili ma non sono lo scopo del servizio, e i volumi sono piccoli. |
| Rappresentante UE (art. 27) | Non serve se il titolare è stabilito in Italia. **`TODO_OPERATORE: confermare lo stabilimento`** |
| Persone autorizzate (art. 29) | Gli amministratori della console (ruolo `admin` in Keycloak). **`TODO_OPERATORE: elenco nominativo e lettera di autorizzazione/istruzioni per ciascuno`** |

## Misure di sicurezza comuni

Valgono per tutti i trattamenti; le schede citano solo le misure in più.

- **M1 — Infrastruttura.** Un server dedicato a Londra (Regno Unito) con cluster k3s a nodo singolo; database
  PostgreSQL nel cluster, non esposto in rete; ingresso solo da Nginx Proxy Manager con HTTPS (Let's Encrypt).
  Fornitore del server e luogo: vedi console → Impostazioni → Dati del titolare (predefinito: Hivelocity, data center di Londra). Il server ospita anche altri servizi dell'operatore (namespace diversi, stesso
  PostgreSQL condiviso).
- **M2 — Accessi.** Identità e accessi in Keycloak self-hosted; verifica in due passaggi (app di autenticazione)
  proposta a ogni accesso; la console di amministrazione richiede il ruolo `admin`. **`TODO_OPERATORE: rendere
  obbligatoria la 2FA per gli amministratori, se non lo è già`**.
- **M3 — Segreti.** Chiavi e password nei Secret di Kubernetes, mai nel codice; le chiavi dei fornitori LLM nel
  database cifrate (Fernet). Il segreto per le impronte degli IP (`TAROT_IP_HASH_SECRET`) sta solo nel Secret, non
  nel database (che finisce nei backup).
- **M4 — IP protetti.** Nel registro (`audit_log`) e nei consensi (`user_consents`, `consensi_storico`) l'IP non è mai
  intero: rete troncata (IPv4 /24, IPv6 /48) più impronta HMAC-SHA256 (`tarot/ip_protetto.py`). Le statistiche
  interne non salvano IP. La posizione si stima con il database DB-IP locale: l'IP non esce dal server.
- **M5 — Pseudonimi verso i modelli linguistici.** I nomi di persona noti alla lettura arrivano al fornitore LLM
  come «Persona_N» e tornano veri solo sul server (`tarot/pseudonimi.py`), anche in chat e nelle memorie. Il cognome
  del partner non entra mai nei prompt (`tarot/persone.py`).
- **M6 — Registro append-only.** Ogni azione rilevante (consensi, cancellazioni, azioni degli amministratori) lascia
  una riga in `audit_log`, che l'applicazione non modifica né cancella.
- **M6b — Contenuti degli utenti in console (v9.5).** Per ragioni di sicurezza gli amministratori possono leggere, nella
  scheda di un utente, letture, intervista, chat, memorie e dati di profilazione, solo dopo aver scritto un motivo
  (accesso di 30 minuti); ogni accesso e ogni scheda letta finiscono in `audit_log` e si rivedono nella scheda stessa
  (`api/routers/admin_contenuti_utente.py`). L'informativa lo dichiara. **`TODO_OPERATORE: base giuridica e deroga
  art. 9 da confermare col consulente (vedi DPIA, R14 e A15)`**.
- **M7 — Backup.** Copia notturna del database sul NAS dell'operatore in Italia via SFTP con chiave dell'host
  verificata e impronta SHA-256 di ogni file; rotazione automatica (`tarot/backup.py`). I file del dump non sono
  cifrati a riposo. **`TODO_OPERATORE: valutare la cifratura dei dump sul NAS e documentare chi accede al NAS`**.
- **M8 — Diritti in autonomia.** Esportazione dei dati e cancellazione dell'account dal profilo, senza passare
  dall'operatore (`docs/privacy/conservazione.md`).

## Schede dei trattamenti

### T01 — Account e profilo

| | |
|---|---|
| Finalità | Creare e gestire l'account; personalizzare le letture (carta dell'anima e dell'anno dalla data di nascita, pronomi e concordanze dal genere, lingua, registro linguistico, mazzo preferito); posta di servizio (verifica dell'email, recupero della password). |
| Base giuridica | Art. 6.1.b (servizio richiesto). Posizione attuale stimata all'accesso: art. 6.1.f, con interruttore nel profilo (`rileva_posizione`). |
| Interessati | Utenti registrati. |
| Dati | Email, nome visualizzato, nome e cognome, lingua, data di nascita (facoltativa), genere (facoltativo), paese e città attuali stimati, codice di invito e chi ha invitato, preferenze, conferma dell'età minima, stato della cancellazione. La casella «persona trans» è nella scheda T17. |
| Destinatari | Keycloak (self-hosted); posta in uscita Stalwart (self-hosted, mail.tadamoo.com). Nessun terzo. |
| Trasferimenti extra-UE | Regno Unito (server), con decisione di adeguatezza. |
| Conservazione | Fino alla cancellazione dell'account (30 giorni di ripensamento, poi esecuzione notturna). Vedi `conservazione.md`. |
| Misure | Comuni. Campi correggibili e cancellabili dal profilo. |

### T02 — Accesso con un social e dati importati

| | |
|---|---|
| Finalità | Entrare con Google, Apple, Facebook, GitHub, Microsoft o LinkedIn; compilare i soli campi vuoti della scheda con i dati del social (`tarot/profilo_social.py`); proteggere l'account quando un social si collega a un account esistente con email mai verificata (`tarot/unione_account.py`). |
| Base giuridica | Art. 6.1.b (accesso richiesto); importazione dei campi: art. 6.1.b con interruttore nel profilo (`importa_social`) e la scelta fatta nella schermata del provider. |
| Interessati | Utenti che usano un social. |
| Dati | Identificativo presso il provider, nome, cognome, email, foto, lingua; se il provider li concede: data di nascita, genere, città. Token del provider custoditi da Keycloak. Provenienza di ogni campo (`users.dati_social`). |
| Destinatari | I provider sono titolari autonomi del proprio trattamento (vedi `responsabili.md`). Keycloak self-hosted. |
| Trasferimenti extra-UE | USA (Google, Apple, Meta, GitHub/Microsoft, LinkedIn): il dato nasce presso di loro; il sito riceve, non invia. Garanzie dei provider: EU-US Data Privacy Framework e/o clausole tipo. |
| Conservazione | Come T01. La persona può cancellare in un colpo tutto ciò che è arrivato dai social. |
| Misure | Comuni. Mai sopra un valore scritto dalla persona. |

### T03 — Letture e intervista (utenti registrati)

| | |
|---|---|
| Finalità | Fornire la lettura: quesito, intervista di contesto, estrazione delle carte con impegno crittografico, interpretazioni, responso, diario e valutazione della persona; controllo del responso (guardrail) e risposta d'aiuto se compaiono frasi su autolesionismo. |
| Base giuridica | Art. 6.1.b. Per i dati art. 9 che la persona scrive di sua iniziativa nel testo libero vedi T17: **la base art. 9 è un punto aperto** (`dpia.md`). |
| Interessati | Utenti registrati; **terzi nominati** nel quesito o nelle letture di coppia e compatibilità (il partner: nome, cognome, genere, data di nascita). |
| Dati | Quesito e risposte dell'intervista (testo libero), carte, testi generati, memorie richiamate, istantanea delle persone, feedback, stato della condivisione. |
| Destinatari | Fornitori LLM attivi in console (responsabili art. 28), con i nomi sostituiti da pseudonimi e senza il cognome del partner. Elenco reale e paesi: vedi console → Impostazioni → Dati del titolare (si legge dai fornitori attivi in «Modelli», dove sono anche i compiti assegnati), vedi anche `responsabili.md`. |
| Trasferimenti extra-UE | Dipende dai fornitori attivi: USA (per esempio NVIDIA, OpenAI, Anthropic) con DPF e/o clausole tipo. Fornitori con sede in paesi senza adeguatezza (Cina, Singapore) richiedono clausole tipo e valutazione del trasferimento: vedi `dpia.md`. |
| Conservazione | **Senza scadenza automatica**, fino a cancellazione dell'interessato (singola lettura o account) o dell'amministratore. Nota art. 5.1.e in `conservazione.md`. |
| Misure | Comuni, in particolare M5. Cancellazione vera della lettura (cascata su intervista, carte, immagine di condivisione). Segnale di crisi registrato solo come conteggio senza utente. |

### T04 — Letture anonime

| | |
|---|---|
| Finalità | Una lettura gratuita di prova senza account. |
| Base giuridica | Art. 6.1.b (servizio richiesto). |
| Interessati | Visitatori senza account. |
| Dati | Identificativo casuale in un cookie tecnico `tarots_anon` (HttpOnly, un anno), quesito e intervista, carte, testi generati, conferma dell'età minima con prova nello storico dei consensi. |
| Destinatari | Fornitori LLM come in T03. |
| Trasferimenti extra-UE | Come T03. |
| Conservazione | **Senza scadenza automatica**; cancellazione manuale dalla console «Conservazione dati» (voce `letture_anonime`). |
| Misure | Comuni. Sono **pseudonime, non anonime**: il testo libero può identificare la persona. |

### T05 — Memoria del lettore

| | |
|---|---|
| Finalità | Ricordare fatti utili alle letture successive (`tarot/memoria.py`): estratti da un modello dopo la lettura o dalla chat, richiamati per similarità (vettori numerici). |
| Base giuridica | Art. 6.1.b (personalizzazione del servizio). Memorie sulla salute: art. 9.2.a, solo con il consenso `dati_particolari` (T17). **`TODO_OPERATORE: col consulente, decidere se la memoria debba diventare facoltativa (interruttore) e quindi basata sul consenso`**. |
| Interessati | Utenti registrati; terzi citati nelle memorie (con pseudonimi verso il modello). |
| Dati | Testo della memoria, tipo, campo di attinenza, versioni sostituite, vettore numerico. |
| Destinatari | Fornitori LLM attivi per i compiti `memoria_estrazione` ed `embedding`. |
| Trasferimenti extra-UE | Come T03. |
| Conservazione | Fino a cancellazione da «La mia storia» o dell'account. Le memorie sulla salute si cancellano alla revoca di `dati_particolari`. |
| Misure | Comuni. La persona vede, modifica e cancella ogni memoria. |

### T06 — Chat con l'oracolo

| | |
|---|---|
| Finalità | Conversazione aperta dall'oracolo a partire dalle memorie, con proposta di una lettura sul tema (`tarot/chat_proattiva.py`). |
| Base giuridica | Art. 6.1.b. Dati art. 9 nel testo libero: come T03. |
| Interessati | Utenti registrati; terzi citati. |
| Dati | Messaggi della persona e dell'oracolo. |
| Destinatari | Fornitori LLM attivi per il compito `chat_proattiva`, con pseudonimi. |
| Trasferimenti extra-UE | Come T03. |
| Conservazione | **Senza scadenza automatica**; cancellazione con l'account o dalla console (voce `chat_proattiva`). |
| Misure | Comuni. |

### T07 — Carta del giorno

| | |
|---|---|
| Finalità | Mostrare la carta del giorno della persona. |
| Base giuridica | Art. 6.1.b. |
| Interessati | Utenti registrati. |
| Dati | Utente, giorno, carta. |
| Destinatari | Nessuno. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Fino alla cancellazione dell'account. |
| Misure | Comuni. |

### T08 — Condivisione delle letture e inviti

| | |
|---|---|
| Finalità | Pubblicare il link di una lettura scelta dalla persona; accertare che il link sia stato aperto da un visitatore vero per il premio «5 condivisioni = 1 lettura» (`tarot/condivisione.py`); premiare gli inviti con il codice personale. |
| Base giuridica | Art. 6.1.b (funzione scelta dalla persona e regolamento del premio). |
| Interessati | Utenti che condividono; visitatori del link; persone invitate che si iscrivono. |
| Dati | Token pubblico e testo della lettura condivisa, immagine di anteprima; impronte con sale del browser e della rete di chi clicca e di chi visita (mai l'IP in chiaro); legame invitante–invitato e crediti dati. |
| Destinatari | Chiunque riceva il link (contenuto scelto dalla persona). Nella versione condivisa il nome dell'altra persona diventa «qualcuno di speciale»; cognome e date non escono mai. |
| Trasferimenti extra-UE | Regno Unito (server). Le piattaforme social su cui la persona pubblica il link sono scelta sua. |
| Conservazione | Fino alla cancellazione della lettura o dell'account. |
| Misure | Comuni. |

### T09 — Pagamenti, crediti, abbonamenti, coupon, ordini e spedizioni

| | |
|---|---|
| Finalità | Vendere crediti, abbonamenti e mazzi (digitali, PDF, fisici); applicare offerte e coupon; spedire i mazzi fisici; tenere la contabilità. |
| Base giuridica | Art. 6.1.b (contratto); art. 6.1.c (obblighi fiscali e contabili). |
| Interessati | Clienti. |
| Dati | Registro dei crediti, abbonamenti, sessioni di pagamento ed eventi del fornitore (mai i dati della carta), ordini e righe, indirizzi di spedizione (nome, via, città, CAP, provincia, paese, telefono facoltativo), coupon usati, mazzi sbloccati. |
| Destinatari | Stripe (pagamenti web, Fase 2 in corso); in futuro Google Play e App Store per gli acquisti nelle app. Spedizione dei mazzi fisici: **`TODO_OPERATORE: tipografia/corriere che riceve nome, indirizzo e telefono`**. Commercialista: **`TODO_OPERATORE: nome dello studio, se riceve i dati`**. |
| Trasferimenti extra-UE | USA (Stripe, Inc., per le parti che tratta negli Stati Uniti) con DPF e/o clausole tipo; Regno Unito (server). |
| Conservazione | Dieci anni per la contabilità (art. 2220 c.c., da confermare col commercialista). Alla cancellazione dell'account la contabilità resta **pseudonimizzata**; degli ordini resta il paese (IVA), non l'indirizzo. |
| Misure | Comuni. Nessun dato di carta sul server. |

### T10 — Voto dei mazzi e temi suggeriti

| | |
|---|---|
| Finalità | Far scegliere agli utenti i prossimi mazzi e raccogliere temi proposti. |
| Base giuridica | Art. 6.1.b (partecipazione volontaria a una funzione del servizio). |
| Interessati | Utenti registrati che votano o propongono. |
| Dati | Voto (utente, turno, candidato); testo libero del tema proposto (fino a 1000 caratteri) e il suo stato. |
| Destinatari | Nessuno. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Voti fino alla cancellazione dell'account; i temi suggeriti si cancellano con l'account. **`TODO_OPERATORE: decidere se i voti dei turni chiusi da oltre N mesi vadano ridotti a totali`**. |
| Misure | Comuni. |

### T11 — Statistiche interne di base (anonime)

| | |
|---|---|
| Finalità | Contare visite, pagine, provenienza e dispositivi di chi non ha fatto l'accesso. |
| Base giuridica | Dati anonimi: fuori dal GDPR una volta calcolati. Il breve uso dell'IP per l'impronta e la posizione: art. 6.1.f. **`TODO_OPERATORE: col consulente, verificare che non serva il consenso ai sensi dell'art. 122 Codice privacy (nessun cookie e nessuna scrittura nel browser: dovrebbe essere escluso)`**. |
| Interessati | Visitatori. |
| Dati | Impronta giornaliera `sha256(sale del giorno, sito, IP, user agent)` con sale distrutto dopo 48 ore; pagina, provenienza (canale, referrer, UTM), dispositivo e browser in categorie, paese e città stimati (DB-IP locale). Nessun IP, nessun cookie. |
| Destinatari | Nessuno. Analisi automatiche ed esportazioni (Google Colab) solo su aggregati con soglia di 5 persone per cella. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Dettaglio 25 mesi, poi solo totali giornalieri anonimi. |
| Misure | Comuni. Libreria `lanterna`. |

### T12 — Statistiche collegate all'account

| | |
|---|---|
| Finalità | Capire canali, abbandoni e fidelizzazione degli utenti registrati. |
| Base giuridica | Art. 6.1.f: valutazione in `lia-analytics.md`. Opposizione in un clic dal profilo (art. 21). |
| Interessati | Utenti registrati che hanno fatto l'accesso. |
| Dati | Come T11, collegati all'identificativo interno dell'account, più gli eventi di business (iscrizione, letture iniziate e finite, acquisti). Mai il contenuto delle letture o della chat. |
| Destinatari | Nessuno; aggregati con soglia k≥5 verso analisi automatiche e Colab. |
| Trasferimenti extra-UE | Regno Unito (server). Colab: solo aggregati. |
| Conservazione | Dettaglio 25 mesi, poi totali anonimi. Con l'opposizione o la cancellazione dell'account il legame con l'account si toglie. |
| Misure | Comuni. |

### T13 — Statistiche estese (identificativo del browser)

| | |
|---|---|
| Finalità | Riconoscere lo stesso browser nei giorni successivi per misurare i ritorni. |
| Base giuridica | Art. 6.1.a e art. 122 Codice privacy: consenso `statistiche`. |
| Interessati | Visitatori e utenti che accettano. |
| Dati | Identificativo casuale del browser, più i dati di T11. |
| Destinatari | Nessuno. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Come T11. Alla revoca il sito dimentica l'identificativo (`/e/dimentica`). |
| Misure | Comuni. |

### T14 — Google Analytics 4

| | |
|---|---|
| Finalità | Misurare l'uso del sito con uno strumento standard. |
| Base giuridica | Art. 6.1.a e art. 122 Codice privacy: consenso `google_analytics`. Si carica solo dopo il consenso (Consent Mode), con segnali Google e personalizzazione degli annunci spenti. |
| Interessati | Visitatori e utenti che accettano. |
| Dati | Cookie `_ga`, identificativo del client, pagine, eventi, dispositivo, posizione approssimativa (GA4 non conserva gli IP). |
| Destinatari | Google Ireland Ltd. (responsabile). |
| Trasferimenti extra-UE | USA (Google LLC): DPF e clausole tipo. |
| Conservazione | Quella impostata in GA4. **`TODO_OPERATORE: indicare la conservazione impostata nella proprietà GA4 (2 o 14 mesi)`**. |
| Misure | Revoca: GA si ferma e i cookie si cancellano. |

### T15 — Pubblicità (Google AdSense)

| | |
|---|---|
| Finalità | Mostrare fino a tre spazi pubblicitari segnalati. Spenta per impostazione predefinita: attiva solo se l'operatore la accende in console. |
| Base giuridica | Art. 6.1.a e art. 122 Codice privacy: consenso `pubblicita`. |
| Interessati | Visitatori e utenti che accettano, quando la pubblicità è accesa. |
| Dati | Cookie di Google (`__gads`, `__gpi`), identificativi pubblicitari, dati del dispositivo e della pagina. |
| Destinatari | Google Ireland Ltd., titolare autonomo per la pubblicità. |
| Trasferimenti extra-UE | USA: DPF e clausole tipo. |
| Conservazione | Decisa da Google per i suoi cookie. |
| Misure | Annunci non personalizzati salvo diversa indicazione nell'informativa. **`TODO_OPERATORE: se la pubblicità si accende nello SEE, verificare l'obbligo di una CMP certificata IAB TCF richiesta da Google`**. |

### T16 — Testi per statistiche e spunti del blog (futuro)

| | |
|---|---|
| Finalità | Ricavare temi ricorrenti, anonimi e aggregati, dai testi delle persone, per statistiche interne e idee per il blog. |
| Base giuridica | Art. 6.1.a: consenso `testi_statistiche`. |
| Stato | **Solo il consenso esiste oggi: nessuna estrazione.** Regole della pipeline futura in `testi-statistiche.md`. |
| Interessati | Utenti che accettano. |
| Dati | Quesiti, interviste e chat, anonimizzati prima di ogni uso; nel dataset derivato nessun legame con l'utente. |
| Destinatari | Fornitori LLM attivi, solo con testi già anonimizzati. |
| Trasferimenti extra-UE | Come T03. |
| Conservazione | Derivati aggregati: vedi `testi-statistiche.md`. |
| Misure | Soglia k≥5, mai citazioni, esclusione dei testi sensibili. |

### T17 — Categorie particolari (art. 9)

| | |
|---|---|
| Finalità | Usare nelle letture la casella «persona trans» (della persona o del partner) e ricordare memorie sulla salute. |
| Base giuridica | Art. 9.2.a: consenso esplicito `dati_particolari`. **Punti aperti** (`dpia.md`): (1) la casella «trans» **del partner** è un dato art. 9 di un terzo, che il consenso di chi consulta non copre; (2) i dati art. 9 scritti spontaneamente nel testo libero di letture e chat (salute, vita sessuale, orientamento, identità di genere, convinzioni religiose) arrivano al modello senza una base art. 9 dichiarata. |
| Interessati | Utenti registrati; partner indicati nelle letture di coppia. |
| Dati | Casella «trans» nella scheda e nel partner ricordato; memorie con campo di attinenza «salute». Segnale di crisi: **solo un conteggio senza utente** (evento `reading.crisis` e statistica `lettura_crisi`). |
| Destinatari | Fornitori LLM, solo con il consenso in vigore e con pseudonimi. |
| Trasferimenti extra-UE | Come T03. |
| Conservazione | Fino alla revoca: la revoca spegne «trans» (anche nel partner ricordato) e cancella le memorie sulla salute (`tarot/consensi.py`). Le letture già fatte restano come racconto di allora, cancellabili dalla persona. |
| Misure | Comuni. «Trans» escluso da ogni statistica. |

### T18 — Marketing e notifiche (futuro, Fase 5)

| | |
|---|---|
| Finalità | Inviare promozioni e novità con notifiche push nelle app (FCM, APNs tramite FCM) e Web Push sul sito, filtrate per lingua, paese e attività. |
| Base giuridica | Art. 6.1.a: consenso `marketing` (più il permesso del sistema operativo o del browser). |
| Stato | **Non implementato**: esiste solo il consenso. Oggi le email partono solo verso gli amministratori e per la posta di servizio di Keycloak. |
| Interessati | Utenti che accettano. |
| Dati | Token del dispositivo o sottoscrizione Web Push, lingua, paese, segmenti di attività. |
| Destinatari | Google (Firebase Cloud Messaging), Apple (APNs), servizi push dei browser. |
| Trasferimenti extra-UE | USA: DPF e/o clausole tipo. |
| Conservazione | **`TODO_OPERATORE: da decidere con la Fase 5 (es. token tolti alla revoca e dopo N mesi di inattività)`**. |
| Misure | Da definire con la Fase 5; aggiornare questa scheda e la DPIA prima del rilascio. |

### T19 — Consensi, età minima e loro prova

| | |
|---|---|
| Finalità | Registrare le scelte sui consensi e la conferma dell'età minima, e poterle dimostrare (art. 7.1, art. 8). |
| Base giuridica | Art. 6.1.c (obbligo di dimostrare il consenso) e art. 6.1.f. |
| Interessati | Visitatori e utenti. |
| Dati | Stato corrente (`user_consents`) e storico append-only (`consensi_storico`): tipo, valore, versione dell'informativa, origine (web, android, ios, sistema), IP troncato e impronta HMAC, data; utente o identificativo anonimo. Età: `users.eta_confermata_il`, `eta_confermata_anni`. |
| Destinatari | Nessuno. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Per la durata del rapporto e oltre per la prova; dalla console si possono cancellare le scelte storiche oltre N anni, mai l'ultima per persona e tipo. **`TODO_OPERATORE: fissare N (proposta: 5 anni dopo la fine del rapporto, da validare col consulente)`**. |
| Misure | Comuni (M4, M6). |

### T20 — Registro, sicurezza e log tecnici

| | |
|---|---|
| Finalità | Sicurezza, prevenzione degli abusi, ricostruzione degli incidenti, prova delle operazioni. |
| Base giuridica | Art. 6.1.f e art. 32. |
| Interessati | Utenti, visitatori, amministratori. |
| Dati | `audit_log`: chi, azione, oggetto, stato prima/dopo, IP troncato e impronta, identificativo di correlazione, data. **Log dei pod (uvicorn) e di Nginx Proxy Manager**: contengono l'IP intero e gli indirizzi richiesti. |
| Destinatari | Nessuno. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | `audit_log`: senza scadenza; gli IP si possono togliere dalla console (voce `ip_audit`). Log dei pod e del proxy: **`TODO_OPERATORE: verificare rotazione e durata dei log di k3s e di Nginx Proxy Manager (proposta: massimo 30 giorni)`**. |
| Misure | Comuni. |

### T21 — Backup

| | |
|---|---|
| Finalità | Continuità del servizio e ripristino dopo un guasto o un incidente. |
| Base giuridica | Art. 6.1.f e art. 32.1.c. |
| Interessati | Tutti quelli dei trattamenti precedenti. |
| Dati | Il database intero (`pg_dump`), compresi lo schema Keycloak e le immagini. |
| Destinatari | NAS TerraMaster dell'operatore, in Italia, raggiunto via SFTP. **`TODO_OPERATORE: confermare il percorso di rete (rete privata Tailscale o porta pubblica del NAS)`**. |
| Trasferimenti extra-UE | Il dato torna nell'UE (Italia). |
| Conservazione | Le 7 copie notturne più recenti (valore modificabile dalla console) e le 3 copie di sicurezza fatte prima di un ripristino. I dati cancellati restano nei backup fino alla rotazione. **`TODO_OPERATORE: confermare il numero di copie impostato in console e se esistono altre copie del NAS (snapshot, dischi esterni, cloud)`**. |
| Misure | M7. |

### T22 — Esercizio dei diritti: esportazione e cancellazione

| | |
|---|---|
| Finalità | Rispondere alle richieste di accesso, portabilità e cancellazione (art. 15, 17, 20). |
| Base giuridica | Art. 6.1.c. |
| Interessati | Utenti registrati. |
| Dati | Archivio ZIP di JSON generato al volo (`GET /me/esportazione`, una volta al giorno); richiesta di cancellazione con data, poi esecuzione (`POST /me/cancellazione`, 30 giorni, CronJob `tarots-cancellazioni`). |
| Destinatari | Keycloak (cancellazione dell'utente). |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Della richiesta resta la traccia in `audit_log`, legata allo pseudonimo. |
| Misure | Comuni. Le richieste che non passano dal profilo (visitatori anonimi, rettifiche, opposizioni via email) si gestiscono a mano: **`TODO_OPERATORE: procedura e registro delle richieste ricevute via email, risposta entro un mese (art. 12.3)`**. La revoca del token presso Apple arriva con la Fase 6. |

### T23 — Blog: nome pubblico, avatar, commenti

| | |
|---|---|
| Finalità | Pubblicare articoli; far presentare l'utente con un nome scelto e un'immagine nei commenti. |
| Base giuridica | Art. 6.1.b. |
| Stato | Nome pubblico e avatar si impostano dal profilo; gli articoli hanno il campo `commenti_aperti`, ma nel codice al 2026-10-03 **non esiste una tabella dei commenti**. **`TODO_OPERATORE: confermare che i commenti non sono attivi; quando lo saranno, aggiornare questa scheda (moderazione, conservazione, segnalazioni)`**. |
| Interessati | Utenti registrati; autori degli articoli (amministratori). |
| Dati | Nome pubblico (mai l'email), immagine dell'avatar, autore dell'articolo. |
| Destinatari | Pubblico del sito. Le immagini degli articoli generate con LitMedia e la pubblicazione su Reddit **non** contengono dati degli utenti. |
| Trasferimenti extra-UE | Regno Unito (server). |
| Conservazione | Fino a modifica dal profilo o cancellazione dell'account. |
| Misure | Comuni. |

## Fuori registro (nessun dato personale degli utenti)

Google Search Console e IndexNow/WebSub (dati del sito), LitMedia (immagini del blog da descrizioni senza dati
utente), Reddit (pubblicazione degli articoli), Codemagic (build delle app), DB-IP (file locale, nessuna chiamata),
traduzione degli articoli e della base di conoscenza con i modelli LLM (testi editoriali).
