# Procedura per le violazioni dei dati personali (art. 33-34 GDPR)

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

Una violazione (data breach) è ogni incidente di sicurezza che porta alla distruzione, perdita, modifica, divulgazione
non autorizzata o accesso non autorizzato a dati personali (art. 4.12). Non serve che ci sia un attacco: un backup
lasciato accessibile, un'email al destinatario sbagliato, una lettura mostrata alla persona sbagliata sono violazioni.

Le tre domande, in ordine: **cosa è successo**, **che rischio c'è per le persone**, **chi va avvisato e entro quando**.

## Contatti

| Ruolo | Chi | Come |
|---|---|---|
| Titolare, decide e notifica | Andrea Taini | **`TODO_OPERATORE: telefono ed email di emergenza`** |
| Consulente privacy | **`TODO_OPERATORE: nome`** | **`TODO_OPERATORE: contatti`** |
| DPO, se nominato | Vedi console → Impostazioni → Dati del titolare | Vedi console → Impostazioni → Dati del titolare |
| Fornitore dell'hosting (supporto) | Vedi console → Impostazioni → Dati del titolare | **`TODO_OPERATORE: contatto del supporto e procedura per gli incidenti`** |
| Fornitori LLM, Stripe, Google | Vedi `responsabili.md` | **`TODO_OPERATORE: indirizzi per segnalare un incidente`** |
| Garante per la protezione dei dati personali | — | Servizio online per la notifica: https://servizi.gpdp.it/databreach/s/ |

I responsabili (art. 28) devono avvisare il titolare **senza ingiustificato ritardo** quando scoprono una violazione
(art. 33.2): verificare che i DPA lo prevedano.

## 1. Rilevazione

Segnali tipici:

- righe inattese in `audit_log` (azioni di amministratore non riconosciute, cancellazioni di massa, cambi di ruolo);
- accessi alla console da reti sconosciute (IP troncati e impronte nel registro);
- errori o picchi nei log dei pod dell'API, di Keycloak, di Nginx Proxy Manager;
- backup che falliscono o file sul NAS che non tornano con l'impronta SHA-256;
- segnalazioni di utenti («vedo la lettura di un altro»), di ricercatori, dei fornitori;
- avvisi del fornitore dell'hosting, di Google, di Stripe, di GitHub (segreti esposti in un repository).

Chi se ne accorge scrive subito la prima riga del registro delle violazioni (sotto), anche se non è ancora sicuro.
**L'orologio delle 72 ore parte da quando il titolare ha una ragionevole certezza** che una violazione è avvenuta.

## 2. Contenimento (subito)

Fermare il danno senza distruggere le prove.

- Credenziali compromesse: cambiare password e chiavi (Secret di Kubernetes, chiavi dei fornitori LLM dalla console,
  segreto client di Keycloak, chiavi Stripe, chiave SFTP del NAS); chiudere le sessioni in Keycloak.
- Account amministratore compromesso: togliere il ruolo `admin`, chiudere le sessioni, controllare il registro.
- Servizio esposto: chiudere l'host su Nginx Proxy Manager o scalare a zero il Deployment
  (`kubectl -n tarots scale deploy/<nome> --replicas=0`).
- Fornitore LLM compromesso: spegnerlo dalla console (`attivo = false`) e assegnare i compiti a un altro.
- Prima di ripristinare o reinstallare: **conservare le prove** (copia dei log dei pod, export di `audit_log`, una
  copia del database com'è, elenco dei file sul NAS).

## 3. Valutazione del rischio

Per ogni violazione annotare:

| Domanda | Note |
|---|---|
| Che tipo di violazione? | Riservatezza (dati visti da chi non doveva), integrità (dati modificati), disponibilità (dati persi o non accessibili). |
| Quali dati? | Le letture, le chat, le memorie e la casella «trans» sono **dati intimi o art. 9**: gravità alta di partenza. Email e nomi: media. Statistiche anonime: bassa. |
| Quante persone, di che paesi? | Contare dal database. Possibili minori? |
| I dati erano protetti? | IP troncati e con impronta (il segreto `TAROT_IP_HASH_SECRET` è fuori dal database); nomi in pseudonimo presso i fornitori LLM; backup **non** cifrati. |
| Le persone sono identificabili? | Il testo libero può identificare anche senza nome. |
| Conseguenze possibili? | Imbarazzo, discriminazione (identità di genere, salute), ricatto, furto d'identità, perdita della propria storia. |
| Il rischio è ancora in corso? | Contenimento riuscito? |

Esito:

- **nessun rischio probabile** per i diritti e le libertà: si registra soltanto (art. 33.5);
- **rischio**: notifica al Garante entro 72 ore;
- **rischio elevato**: notifica al Garante **e** comunicazione agli interessati.

Riferimento utile: le linee guida EDPB 9/2022 sulla notifica delle violazioni, con esempi.

## 4. Notifica al Garante (art. 33)

- Entro **72 ore** da quando il titolare ne è venuto a conoscenza; se oltre, spiegare il ritardo.
- Con il servizio online: https://servizi.gpdp.it/databreach/s/
- Si può notificare **per fasi**: una prima notifica con ciò che si sa, poi le integrazioni.
- Contenuto minimo: natura della violazione, categorie e numero approssimativo di interessati e di registrazioni,
  contatto a cui chiedere informazioni, conseguenze probabili, misure adottate o proposte.
- Se sono coinvolte persone di altri paesi dell'UE, il Garante resta l'autorità capofila se lo stabilimento del
  titolare è in Italia. **`TODO_OPERATORE: confermare lo stabilimento`**.

## 5. Comunicazione agli interessati (art. 34)

Quando il rischio è elevato, senza ingiustificato ritardo, in linguaggio semplice, nella lingua della persona (il
servizio parla molte lingue: usare `users.locale`):

- cosa è successo e quando;
- quali loro dati sono coinvolti;
- cosa può succedere;
- cosa ha fatto il titolare e cosa possono fare loro (cambiare password, attivare la 2FA, fare attenzione a email
  sospette);
- a chi scrivere.

Canale: email dalla posta di servizio (Stalwart) agli indirizzi in `users.email`. Non serve se i dati erano resi
incomprensibili, se le misure successive hanno eliminato il rischio elevato, o se la comunicazione individuale
richiederebbe sforzi sproporzionati (allora un avviso pubblico sul sito).

## 6. Registro delle violazioni (art. 33.5)

Si registra **ogni** violazione, anche quelle non notificate. **`TODO_OPERATORE: dove si tiene il registro (file
riservato dell'operatore, fuori da questo repository se contiene dettagli sulle persone o sulle vulnerabilità)`**.

Modello di riga:

| Campo | Esempio |
|---|---|
| N. | 2026-001 |
| Scoperta il (data e ora) | 2026-11-05 09:40 |
| Avvenuta il (stima) | 2026-11-04 tra le 22:00 e le 23:30 |
| Scoperta da / come | Allarme backup fallito; impronta SHA-256 diversa sul NAS |
| Descrizione | … |
| Tipo | riservatezza / integrità / disponibilità |
| Dati coinvolti | es. letture (testo libero), email |
| Interessati (numero, paesi, minori?) | es. circa 120, IT/ES, nessun minore noto |
| Valutazione del rischio | nessuno / rischio / rischio elevato, con motivazione |
| Contenimento | … |
| Notifica al Garante | sì/no; data e ora; numero di protocollo; motivazione se no |
| Comunicazione agli interessati | sì/no; data; canale; motivazione se no |
| Misure per evitare che si ripeta | … |
| Chiusa il | … |

## 7. Fonti tecniche utili

| Fonte | Cosa dice | Dove |
|---|---|---|
| `audit_log` | Chi ha fatto cosa, su quale oggetto, prima e dopo, rete troncata e impronta dell'IP, identificativo di correlazione | Database, tabella `audit_log` (append-only) |
| Log dei pod k3s | Richieste all'API (con IP interi), errori, Keycloak, CronJob | `kubectl -n tarots logs <pod>`; **i log ruotano**: copiarli subito |
| Log di Nginx Proxy Manager | Accessi HTTP a tutti gli host | Pod NPM; **`TODO_OPERATORE: percorso e rotazione`** |
| Eventi di Keycloak | Accessi, errori di login, cambi di credenziali | Console di amministrazione di Keycloak. **`TODO_OPERATORE: verificare che il salvataggio degli eventi sia attivo e per quanto`** |
| Registro dei backup | Esecuzioni, dimensione, impronta SHA-256, copie ruotate | Console «Backup», tabella `backup_esecuzioni` |
| Backup sul NAS | Lo stato del database nelle notti precedenti, per capire cosa è cambiato e per ripristinare | NAS TerraMaster, cartella scelta in console |
| Statistiche interne | Picchi anomali di visite o eventi | Console «Analytics» |
| Registro dei consensi | Cambi di massa sospetti | `consensi_storico` |
| Tracce OpenTelemetry | Percorso delle richieste, se il collettore è attivo | **`TODO_OPERATORE: collettore OTLP attivo sì/no`** |

## 8. Dopo

- Analisi delle cause e misure correttive annotate nel registro.
- Se la violazione tocca un responsabile, verificare che abbia rispettato il DPA.
- Rivedere la DPIA (`dpia.md`) se la violazione rivela un rischio non considerato.
- **`TODO_OPERATORE: provare questa procedura una volta l'anno (esercitazione con un caso finto) e annotare la data`**.
