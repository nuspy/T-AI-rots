# Obiettivo futuro: segnali di pericolo nei quesiti e nelle risposte

Richiesta dell'operatore, 6/10/2026. **Non è in sviluppo**: è un obiettivo da pianificare dopo la v9.5 (che rende
leggibili in console, con motivo e registro, i contenuti di ogni utente: `api/routers/admin_contenuti_utente.py`).

## Cosa si vuole
- Riconoscere nei quesiti, nelle risposte dell'intervista, nella chat e nei testi del diario le **tracce di
  comportamenti pericolosi**: rischio di suicidio o autolesionismo, violenza verso altri, atti criminali, terrorismo.
- **Avvisare l'amministratore** nei modi che l'operatore definirà (console, posta, notifica), con il collegamento alla
  scheda dell'utente (che si apre comunque solo con un motivo, e resta nel registro).
- **Aiutare la persona dal sito e dall'app**, solo con suggerimenti adatti al tipo di problema e al paese, per esempio
  «se ti senti solo, nella tua zona è attivo questo servizio: chiama…» (i servizi e i numeri vanno raccolti e
  verificati paese per paese; il paese viene dalla posizione già nota o dalla lingua).
- **Atti criminali e terrorismo**: nessun suggerimento all'utente; avviso all'amministratore e, secondo quanto
  stabilirà l'operatore con il consulente legale, segnalazione alle forze dell'ordine.

## Da decidere prima di costruirlo
- Come si riconosce: un classificatore (modello LLM o modello dedicato) sui testi nuovi, con categorie e livelli di
  gravità; il guardrail esistente sul responso (`Reading.guard_outcome`) controlla l'uscita del modello, non l'utente.
- Soglie, falsi positivi e revisione umana: nessuna azione verso terzi senza che un amministratore abbia letto.
- Base giuridica e trasparenza: informativa, DPIA (nuovo rischio: trattamento di dati particolari per finalità di
  sicurezza), registro dei trattamenti; con il consulente, anche il percorso verso le forze dell'ordine.
- Costi: un controllo per ogni testo dell'utente (scegliere un modello economico o locale).
- Minori: tutela rafforzata quando l'età dichiarata è bassa.
