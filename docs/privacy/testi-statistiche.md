# Testi per statistiche e spunti del blog (pipeline futura)

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v1.
**Non è consulenza legale: da far rivedere a un consulente privacy.**

**Stato al 2026-10-03: esiste solo il consenso `testi_statistiche`. Nessuna estrazione, nessun dataset, nessun
codice della pipeline.** Questo documento fissa le regole che la pipeline dovrà rispettare quando verrà scritta;
prima del rilascio va aggiornata la DPIA (`dpia.md`, rischio R13) e questo documento passa alla revisione v2.

## Lo scopo

Capire, in forma anonima e aggregata, di cosa chiedono le persone (temi, tipi di quesito, frequenze per lingua e
periodo) per:

- statistiche interne sul servizio;
- idee per gli articoli del blog («molte persone in questo periodo chiedono di cambi di lavoro»).

Non è uno scopo: profilare la singola persona, pubblicare storie, addestrare modelli, vendere o cedere i dati.

## 1. Consenso

- Base giuridica: art. 6.1.a, consenso `testi_statistiche`, separato da tutti gli altri e spento per impostazione
  predefinita.
- **Il consenso si legge al momento dell'estrazione**, non al momento in cui il testo è stato scritto: entrano solo i
  testi di chi ha il consenso `accettato` in quel momento.
- **Revoca**: da quel momento la persona è esclusa da tutte le estrazioni successive. I derivati già calcolati non
  contengono nulla che la riguardi in modo riconoscibile (sono aggregati con soglia, punto 3) e non si ricalcolano.
- Letture anonime: escluse, finché il visitatore non ha un consenso registrato sul suo identificativo anonimo.
  **`TODO_OPERATORE: decidere se escluderle sempre (proposta: sì, è più semplice e più prudente)`**.
- Il consenso vale per i testi scritti **dopo** la data del consenso? **`TODO_OPERATORE: col consulente (proposta: sì,
  solo testi successivi al consenso, perché i precedenti sono stati scritti senza saperlo)`**.

## 2. Quali testi

Entrano: quesito, risposte dell'intervista, messaggi della persona nella chat.

Non entrano mai:

- i testi generati dal modello (responsi, interpretazioni): non dicono nulla di nuovo sulle persone;
- le memorie (sono già una sintesi sulla persona);
- **i testi di una lettura o chat in cui è scattato il segnale di crisi** (frasi su autolesionismo);
- **i testi che toccano temi dell'art. 9**: salute (fisica e mentale, gravidanza, dipendenze), vita sessuale e
  orientamento, identità di genere, origine etnica, convinzioni religiose o politiche, appartenenza sindacale, dati
  genetici o biometrici, procedimenti penali. Il controllo si fa **prima** di ogni altro passaggio, con un filtro
  deterministico (elenchi di parole nelle lingue del sito) più un classificatore; nel dubbio il testo si scarta;
- i testi delle persone che hanno la casella «trans» o memorie sulla salute, anche se hanno dato il consenso
  `dati_particolari`: quel consenso non vale per questo scopo;
- i testi di account con età confermata sotto i 18 anni o con data di nascita che indica meno di 18 anni.

La regola è volutamente larga: perdere qualche tema è un costo piccolo, pubblicare un dato sensibile no.

## 3. Anonimizzazione e aggregazione

Ordine dei passaggi, tutti sul server:

1. **Selezione** dei testi ammessi (punti 1 e 2).
2. **Pulizia deterministica** sul server, prima di qualunque modello:
   - nomi di persona: quelli noti alla lettura con il meccanismo dei pseudonimi (`tarot/pseudonimi.py`), poi
     rimossi del tutto (non basta «Persona_1»: nel dataset non serve nemmeno il segnaposto);
   - email, numeri di telefono, indirizzi web, numeri lunghi (documenti, conti, targhe), date precise, età precise,
     indirizzi e luoghi più piccoli di un paese (città, quartieri, nomi di aziende e scuole) sostituiti da etichette
     generiche (`[luogo]`, `[data]`);
   - un riconoscitore di entità con nome (NER) per i nomi che il sistema non conosce già.
3. **Estrazione dei temi** con il modello: riceve solo testi già puliti, senza alcun identificativo, mescolati e in
   lotti; restituisce **etichette** (tema, sottotema, tono, tipo di quesito), non riassunti.
4. **Aggregazione**: si conta per tema, lingua, mese ed eventualmente paese. **Soglia k≥5**: un tema, una frequenza o
   un incrocio si mostra solo se viene da almeno 5 persone diverse; sotto la soglia si accorpa in «altro» o si
   tace. Le persone si contano sul server con l'identificativo interno, che **non entra nel dataset derivato**.
5. **Scarto** dei testi intermedi puliti alla fine dell'esecuzione.

Il dataset derivato contiene solo: tema, sottotema, lingua, mese, paese (se k≥5 anche per paese), conteggio. Nessun
identificativo, nessun testo, nessun legame con letture o account.

## 4. Uso nel blog

- **Mai citazioni letterali**, nemmeno brevi, nemmeno anonime.
- **Mai parafrasi riconoscibili**: niente storie singole raccontate «come se»; niente dettagli che una persona
  potrebbe riconoscere come suoi (combinazioni insolite di circostanze, tempi, luoghi).
- Il blog parla solo di **tendenze**: «molte domande in questo mese riguardano…», con numeri arrotondati.
- Chi scrive l'articolo (persona o agente con chiave REST) vede solo il dataset derivato, mai i testi.
- Nei temi di un articolo non si usano mai categorie dell'art. 9, anche se il conteggio lo permetterebbe (non
  dovrebbero comunque esserci, per il punto 2).

## 5. Dove gira

- Tutto sul server del servizio (Regno Unito), come un Job di Kubernetes a richiesta o pianificato.
- Il modello linguistico riceve solo testi già anonimizzati (punto 3.2) e solo da fornitori con DPA verificato e
  senza addestramento sui dati; mai fornitori in paesi senza adeguatezza (`responsabili.md`).
- Nessuna esportazione dei testi verso strumenti esterni (Colab compreso): fuori dal server esce solo il dataset
  derivato con soglia.

## 6. Conservazione

| Cosa | Quanto |
|---|---|
| Testi originali | Restano dove sono (letture, chat), con le loro regole (`conservazione.md`). La pipeline non ne fa copie durature. |
| Testi intermedi puliti e risposte del modello | Solo durante l'esecuzione; cancellati alla fine. |
| Dataset derivato (temi aggregati con k≥5) | Dati anonimi: **`TODO_OPERATORE: durata (proposta: 25 mesi, come il dettaglio delle statistiche)`**. |
| Registro delle esecuzioni | Data, numero di testi ammessi e scartati per motivo, versione delle regole: in `audit_log`, senza testi. |

## 7. Controlli prima del rilascio

- [ ] Test automatici: un testo senza consenso, con consenso revocato, con segnale di crisi, con temi art. 9, di un
      minore non entra; un tema con 4 persone non compare; il dataset non contiene identificativi né testo.
- [ ] Prova su un campione: una persona legge 50 testi puliti e verifica che nessuno resti riconoscibile.
- [ ] Informativa aggiornata con lo scopo, il funzionamento e la revoca.
- [ ] DPIA aggiornata (R13) e parere del consulente.
- [ ] Interruttore generale in console, spento per impostazione predefinita.

## Cosa NON è ancora implementato

Tutto tranne il consenso: selezione, filtri sui temi art. 9 e sulla crisi, pulizia, estrazione con il modello,
aggregazione con soglia, dataset derivato, registro delle esecuzioni, interruttore in console, test.
