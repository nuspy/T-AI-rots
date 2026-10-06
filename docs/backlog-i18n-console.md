# Obiettivo futuro: la console in più lingue

Richiesta dell'operatore, 6/10/2026; **rimandata** («aspettiamolo e mettiamolo tra i target futuri»), in attesa che
la GPU sia libera per tradurre con il modello locale.

- **Registro separato** da quello del sito: dizionari propri in `admin/i18n/<lingua>/`, divisi per area.
- **Lingue nel selettore**: italiano, inglese, ungherese, francese, spagnolo, tedesco. **Tradotte solo it, en, hu**;
  fr, es, de mostrano l'inglese finché non vengono tradotte.
- Lingua predefinita: quella del browser se è una delle sei, altrimenti l'inglese; scelta salvata per amministratore.
- Dimensioni misurate il 6/10: 59 pagine, 138 file, ~21.000 righe, ~3.200 frasi in italiano nel codice.
- Metodo previsto (per spendere poco): estrazione dei testi con uno script sull'AST (testi JSX e attributi
  `placeholder`, `title`, `aria-label`, `label`), sistemazione a mano delle frasi nella logica; traduzione en/hu con
  il modello locale (LM Studio) e un glossario fisso (crediti, letture, stese, nomi delle carte); nomi propri e codici
  invariati; revisione a campione.
- Stima: ~1 giorno infrastruttura e script, 2–3 giorni estrazione, ½ giorno traduzione e revisione.
