# Valutazione del legittimo interesse — statistiche di utilizzo collegate all'account

Titolare: Andrea Taini (TAROTS chat, https://tarots.chat). Data: 2026-10-03. Revisione: v2.
**Non è consulenza legale: da far rivedere a un consulente privacy.**
Base giuridica valutata: art. 6(1)(f) GDPR. Scheda T12 di `registro-trattamenti.md`.

## Trattamento

Le visite degli utenti **registrati e autenticati** (pagine viste, tempo attivo, provenienza della
visita — canale, referrer, parametri UTM —, dispositivo e browser in categorie, paese e città stimati
dall'IP) sono collegate all'identificativo interno dell'account, insieme agli eventi di business
(iscrizione, letture, acquisti). Dati raccolti con la libreria `lanterna`, conservati nel database
del servizio (server nel Regno Unito), mai ceduti a terzi.

Fuori da questa valutazione, perché anonimi: le visite di chi non ha fatto l'accesso (impronta
giornaliera con sale distrutto dopo 48 ore, nessun cookie, nessun dato salvato nel browser, IP mai
conservato). Il livello «esteso» (identificativo casuale del browser) si basa sul **consenso
`statistiche`** del banner, non sul legittimo interesse; Google Analytics 4 sul consenso separato
`google_analytics`. Fino alla v1 entrambi dipendevano dall'unico consenso «cookie», ora dismesso: la migrazione
della Fase 1 GDPR ha convertito ogni scelta «cookie» nella stessa scelta su `statistiche` e su `google_analytics`
(decisione dell'operatore).

## 1. Finalità (test dello scopo)

- Capire da quali canali e campagne arrivano gli iscritti e i clienti, per decidere dove investire.
- Capire quali passaggi della lettura e dell'acquisto fanno abbandonare, per migliorarli.
- Misurare la fidelizzazione (ritorni, giorni attivi) e il valore dei clienti nel tempo.

Interessi legittimi, concreti e attuali di un servizio a pagamento che deve sostenersi.

## 2. Necessità

- Senza il collegamento all'account non si può collegare una campagna a un acquisto successivo né
  misurare le coorti: i conteggi anonimi da soli non bastano.
- Minimizzazione: nessun IP, nessun user agent completo, nessuna query string (può contenere il testo
  della domanda), nessuna email nelle tabelle delle statistiche; dispositivo e browser solo in
  categorie; città stimata e dichiarata come imprecisa.
- Le analisi automatiche (anche con modelli linguistici) e le esportazioni verso strumenti esterni
  (Google Colab) ricevono solo **aggregati** con soglia minima di 5 persone per cella.

## 3. Bilanciamento

- Aspettative ragionevoli: un utente registrato di un servizio online si aspetta che il gestore sappia
  come usa il servizio stesso; non c'è profilazione pubblicitaria né cessione a terzi.
- Natura dei dati: le letture dei tarocchi possono toccare temi personali, ma **il contenuto delle
  letture non entra nelle statistiche** (solo il fatto che una lettura è iniziata/finita, il tipo di
  stesa, la lingua).
- Categorie particolari: **le statistiche non ne trattano, ma il servizio sì.** Letture e chat possono
  contenere dati dell'art. 9 nei testi liberi (salute, vita sessuale, orientamento, identità di genere), e il
  profilo ha la casella «persona trans». Nelle statistiche:
  - il contenuto di letture e chat non entra mai (vedi sopra): nessun quesito, nessuna risposta, nessun
    messaggio, nessuna query string;
  - la casella «trans» è esclusa da ogni analisi; nel servizio vale solo con il consenso `dati_particolari`
    (art. 9.2.a), e la revoca la spegne;
  - il segnale di crisi (frasi su autolesionismo) è contato **senza utente**: un evento `lettura_crisi` e una riga
    `reading.crisis` nel registro, senza legame con l'account, quindi non collegabile alla persona nemmeno in
    questo trattamento.

  I dati art. 9 del servizio sono valutati nella DPIA (`dpia.md`), non qui.
- Garanzie: opposizione in un clic dal profilo (le visite smettono di essere collegate e il legame con
  quelle passate viene cancellato, art. 21), informativa nella pagina Privacy, conservazione 25 mesi
  del dettaglio (poi solo totali giornalieri anonimi), accesso alla console riservato agli
  amministratori.

## Esito

Il trattamento è ammissibile sulla base del legittimo interesse, con le garanzie indicate. Da
rivalutare se cambiano le finalità (per esempio pubblicità mirata, che richiederebbe il consenso) o se
i dati venissero condivisi con terzi.
