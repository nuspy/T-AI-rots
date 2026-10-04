"""Le notifiche push dell'app e del sito (v9, Fase 5). Da non confondere con `tarot/notifiche_motori.py`, che
avvisa i motori di ricerca degli articoli nuovi.

- `config`: la configurazione della console (service account di Firebase cifrato, chiavi VAPID generate da sole e
  salvate cifrate, predefiniti), la firma HMAC dei link (apertura, disiscrizione), i testi predefiniti;
- `fcm`: Firebase Cloud Messaging HTTP v1 (Android, e iOS attraverso la chiave APNs caricata in Firebase);
- `webpush`: il Web Push dei browser (RFC 8030/8291/8292), con `pywebpush` per la cifratura e la firma VAPID;
- `segmenti`: i filtri della console → SQL. Le promozioni solo a chi ha il consenso `marketing`; mai dati dell'art. 9,
  e il genere non è un filtro;
- `invio`: il postino — lotti, limite di velocità, ore di silenzio, tetti, dispositivi da disattivare (404/410);
- `automatiche`: carta del giorno, serie in pericolo, crediti in scadenza, benvenuto, rinnovo non riuscito, prova
  che finisce; `campagne`: i messaggi della console; `traduzione`: i testi tradotti con l'LLM.

Il giro lo fa il CronJob `tarots-notifiche` ogni 15 minuti (`tools/notifiche.py`).
"""
