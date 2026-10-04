# Responsabili del trattamento e terze parti

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

Chi riceve dati personali degli utenti, in che ruolo, dove, con quale garanzia per il trasferimento e a che punto è
l'accordo. Le schede dei trattamenti sono in `registro-trattamenti.md`.

Ruoli:

- **responsabile (art. 28)**: tratta i dati per conto del titolare e secondo le sue istruzioni; serve un accordo
  scritto (DPA), spesso già incluso nei termini del fornitore e da accettare;
- **titolare autonomo**: decide da sé finalità e mezzi del proprio trattamento (per esempio il social con cui si
  entra); non serve un DPA, ma va citato nell'informativa;
- **contitolare (art. 26)**: decide insieme al titolare; serve un accordo sulle rispettive responsabilità. Oggi nessun
  caso accertato.

Trasferimenti: il server è nel Regno Unito, coperto dalla decisione di adeguatezza dell'UE (rinnovata nel 2025;
**`TODO_OPERATORE: verificare la scadenza in vigore`**). Gli Stati Uniti sono coperti dall'EU-US Data Privacy
Framework solo per le società certificate (verificare su https://www.dataprivacyframework.gov/), altrimenti servono le
clausole contrattuali tipo (SCC).

**Stato dei DPA: nessuno risulta firmato o verificato al 2026-10-03.** Ogni riga riporta «da firmare / da verificare»
finché l'operatore non indica data e versione dell'accordo accettato.

## Fornitori che ricevono dati degli utenti

| Servizio | Ruolo | Dati trattati | Paese | Garanzia per il trasferimento | DPA del fornitore | Stato del DPA |
|---|---|---|---|---|---|---|
| Hosting del server (Londra). Fornitore secondo la memoria tecnica dell'operatore: Hivelocity. **`TODO_OPERATORE: confermare il fornitore e la sede legale`** | Responsabile | Tutto il database e i log, a livello di infrastruttura | Regno Unito (data center); sede del fornitore da verificare | Adeguatezza UK. Se la società madre è negli USA e può accedere ai server: DPF o SCC | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Fornitori LLM attivi in console (vedi tabella sotto) | Responsabile | Quesiti, interviste, chat, memorie, persone della lettura con nomi in pseudonimo, testi da vettorizzare | Per fornitore | Per fornitore | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Google Analytics 4 (Google Ireland Ltd.) | Responsabile | Identificativo del client (`_ga`), pagine, eventi, dispositivo, posizione approssimativa | Irlanda, USA | DPF (Google LLC) e SCC nei termini Google | Google Ads Data Processing Terms: https://business.safety.google/adsprocessorterms/ | **`TODO_OPERATORE: da verificare l'accettazione nella console GA4 (Impostazioni account → Trattamento dati)`** |
| Google AdSense (Google Ireland Ltd.), solo se la pubblicità è accesa | Titolare autonomo | Cookie e identificativi pubblicitari, dati del dispositivo e della pagina | Irlanda, USA | DPF e SCC nei termini Google | Google Ads Controller-Controller Data Protection Terms: https://business.safety.google/adscontrollerterms/ | **`TODO_OPERATORE: da verificare l'accettazione nell'account AdSense`** |
| Stripe (Stripe Payments Europe Ltd.; Stripe, Inc.) — Fase 2 in corso | Responsabile per l'elaborazione dei pagamenti; titolare autonomo per antifrode e obblighi di legge (come dichiara Stripe stessa) | Email, importo, prodotto, dati di pagamento (la carta resta presso Stripe), paese | Irlanda, USA | DPF e SCC | https://stripe.com/legal/dpa | **`TODO_OPERATORE: da verificare (si accetta con i termini del servizio)`** |
| Tipografia e corriere dei mazzi fisici | **`TODO_OPERATORE: responsabile o titolare autonomo`** | Nome, indirizzo, telefono, contenuto dell'ordine | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Commercialista | **`TODO_OPERATORE: responsabile o titolare autonomo`** | Dati contabili dei clienti | Italia (presumibile) | — | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |

### Fornitori LLM

Il catalogo della console (`backend/tarot_core/llm/catalogo_fornitori.py`) propone questi fornitori; contano solo
quelli **attivi** con compiti che toccano dati degli utenti (intervista, validazione, interpretazione, sintesi,
giudizio, memoria, embedding, chat). **`TODO_OPERATORE: segnare quali sono attivi e su quali compiti`**.

| Fornitore (dal catalogo) | Paese della sede | Garanzia | DPA | Attivo? | Stato del DPA |
|---|---|---|---|---|---|
| NVIDIA (`integrate.api.nvidia.com`) — predefinito secondo la memoria dell'operatore | USA | DPF se certificata, altrimenti SCC | **`TODO_OPERATORE`**; verificare anche se i prompt dell'API di prova sono usati per addestramento | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| OpenAI (`api.openai.com`) | USA (con entità in Irlanda per l'UE) | DPF e/o SCC | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Anthropic (`api.anthropic.com`) | USA | DPF e/o SCC | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Nebius Token Factory | Paesi Bassi (sede); data center da verificare | Nessuna se nell'UE | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| DeepSeek | Cina — nessuna adeguatezza | SCC più valutazione del trasferimento; **sconsigliato per dati degli utenti** (`dpia.md`, R2) | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Moonshot (Kimi) | Cina — nessuna adeguatezza | Come sopra; sconsigliato per dati degli utenti | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Alibaba Cloud DashScope (endpoint internazionale) | Singapore (endpoint); società cinese — nessuna adeguatezza | Come sopra; sconsigliato per dati degli utenti | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Z.ai (GLM) | **`TODO_OPERATORE: sede`** (Cina o Singapore) | Come sopra; sconsigliato per dati degli utenti | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da firmare / da verificare`** |
| Server locali (LM Studio, vLLM, llama.cpp) | Dove gira la macchina | Nessun terzo se la macchina è dell'operatore | — | **`TODO_OPERATORE`** | — |

## Titolari autonomi per l'accesso con un social

Il sito riceve dati dal provider (non li invia); il provider è titolare del proprio trattamento. Keycloak è
self-hosted.

| Servizio | Dati che il sito riceve | Paese | Garanzia | Nota |
|---|---|---|---|---|
| Google (accesso con Google) | Identificativo, nome, email, foto, lingua; se concessi data di nascita e genere | Irlanda, USA | DPF | — |
| Apple (accesso con Apple) | Identificativo, nome, email (anche in inoltro privato) | Irlanda, USA | DPF | Revoca del token alla cancellazione dell'account: Fase 6. |
| Meta (accesso con Facebook) | Identificativo, nome, email, foto; se concessi data di nascita, genere, città | Irlanda, USA | DPF | Il consulente valuti se, per il login lato server tramite Keycloak, possa configurarsi una contitolarità (giurisprudenza Fashion ID, riferita però ai plug-in nella pagina, che qui non ci sono). |
| GitHub (Microsoft) | Identificativo, nome, email, foto, città | USA | DPF | — |
| Microsoft (accesso con Microsoft) | Identificativo, nome, email | Irlanda, USA | DPF | — |
| LinkedIn (LinkedIn Ireland) | Identificativo, nome, email, foto, lingua | Irlanda, USA | DPF | — |

Stato: verificare nella console di ciascun provider che l'app sia intestata al titolare e che l'informativa del sito
sia indicata dove richiesto. **`TODO_OPERATORE: da verificare`**.

## Servizi futuri

| Servizio | Ruolo | Dati | Paese | Garanzia | DPA | Stato |
|---|---|---|---|---|---|---|
| Firebase Cloud Messaging (Google) — Fase 5 | Responsabile | Token del dispositivo, contenuto della notifica | USA | DPF e SCC | Firebase Data Processing and Security Terms: https://firebase.google.com/terms/data-processing-terms | **`TODO_OPERATORE: da firmare / da verificare prima della Fase 5`** |
| Apple Push Notification service (tramite FCM) — Fase 5 | **`TODO_OPERATORE`** | Token del dispositivo, contenuto della notifica | USA | DPF | **`TODO_OPERATORE`** | **`TODO_OPERATORE: da verificare`** |
| Web Push (servizi push dei browser: Google, Mozilla, Apple, Microsoft) — Fase 5 | Da valutare col consulente | Sottoscrizione cifrata, contenuto cifrato end-to-end (VAPID) | Vari | — | — | **`TODO_OPERATORE`** |
| Google Play e App Store (acquisti nelle app) | Titolari autonomi (vendono loro all'utente) | Ricevuta d'acquisto, identificativo della transazione | Irlanda, USA | DPF | — | **`TODO_OPERATORE: da verificare con l'uscita delle app`** |
| Fornitore di newsletter via email | Responsabile | Email, lingua, iscrizione | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | **`TODO_OPERATORE`** | Non esiste ancora |

## Servizi senza dati degli utenti, o self-hosted

| Servizio | Perché non è un responsabile (o non riceve dati) |
|---|---|
| Keycloak | Self-hosted nel cluster. |
| Posta in uscita Stalwart (mail.tadamoo.com) | Self-hosted sullo stesso server: messaggi di servizio di Keycloak e rapporti agli amministratori. |
| NAS TerraMaster (backup) | Dell'operatore, in Italia. **`TODO_OPERATORE: verificare che non siano attivi servizi cloud TerraMaster (sincronizzazione, accesso remoto) che porterebbero i backup a terzi; se il collegamento passa da Tailscale, citarlo (instrada il traffico cifrato senza vederne il contenuto)`**. |
| DB-IP City Lite | File locale nell'immagine dell'API: nessuna chiamata, l'IP non esce. |
| Google Colab | Riceve solo aggregati con soglia di 5 persone per cella (dati anonimi). Da tenere così. |
| Google Search Console, IndexNow, WebSub | Dati del sito, non degli utenti. |
| LitMedia | Immagini del blog da descrizioni editoriali: nessun dato utente. |
| Reddit | Pubblicazione degli articoli: nessun dato utente. |
| Codemagic | Build delle app: nessun dato utente. |
| Let's Encrypt | Certificati: nessun dato utente. |

## Checklist

- [ ] Confermare il fornitore dell'hosting, la sua sede e il DPA; verificare chi può accedere fisicamente e
      remotamente ai server.
- [ ] Elencare i fornitori LLM attivi e i compiti; per ciascuno: DPA accettato (data, versione), divieto di
      addestramento sui dati, durata di conservazione dei prompt, sede del trattamento, sub-responsabili.
- [ ] Togliere dai compiti con dati degli utenti i fornitori in paesi senza adeguatezza, o documentare SCC e
      valutazione del trasferimento.
- [ ] Verificare la certificazione DPF di ogni società statunitense su dataprivacyframework.gov e annotare la data
      della verifica.
- [ ] GA4: accettare i termini di trattamento dati nella console; annotare la conservazione impostata.
- [ ] AdSense: accettare i termini controller-controller prima di accendere la pubblicità; valutare l'obbligo di una
      CMP certificata IAB TCF.
- [ ] Stripe: conservare copia del DPA in vigore al momento dell'attivazione.
- [ ] Definire ruolo e accordo con tipografia, corriere e commercialista.
- [ ] Prima della Fase 5: termini Firebase e Apple, e aggiornare registro e DPIA.
- [ ] Riportare nell'informativa pubblica l'elenco delle categorie di destinatari e i paesi di trasferimento.
- [ ] Tenere copia (PDF o link con data) di ogni DPA accettato in una cartella dell'operatore:
      **`TODO_OPERATORE: dove`**.
