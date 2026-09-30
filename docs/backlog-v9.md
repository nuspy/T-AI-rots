# Backlog v9

Annotato il 2026-10-01, durante la v8.5. Nessun lavoro ancora: la v9 viene dopo il rilascio della v8.5.

## 1. App Android e iOS

- Da valutare: un guscio nativo sopra la v2 (Capacitor o simile, stesso codice del sito) oppure un'app
  nativa. La v2 è già mobile-first, quindi il guscio è la strada più corta.
- Login Keycloak con PKCE e deep link di ritorno (`tarots://…` o universal/app link sul dominio).
- Notifiche push: il lettore che riapre la conversazione, la carta del giorno.
- Safe area, gesto «indietro», tastiera e font di sistema come nelle regole UI di sempre.

## 2. Pagamenti in-app accanto a Stripe

- Google Play Billing e Apple In-App Purchase per crediti e abbonamenti, con **verifica delle ricevute
  sul server** (mai fidarsi del client) e notifiche server-to-server delle due piattaforme (rinnovi,
  rimborsi, revoche).
- Un solo saldo di crediti e un solo abbonamento per utente, qualunque sia il canale d'acquisto: il
  registro dei movimenti (`credit_entries`) resta l'unica fonte, il canale è un attributo del movimento.
- Stripe sul sito resta com'era deciso (coupon interno, importo già scontato, webhook firmato, chiavi
  nel Secret); oggi non esiste ancora codice Stripe, solo `mock` e `disattivato`.
- Prodotti fisici (scatola del mazzo) fuori dagli acquisti in-app: le regole degli store lo permettono
  solo con pagamenti esterni.

## 3. Voce (rimandata dalla v8.5, F7)

Decisione del 2026-10-01: rimandata. Il piano della v8.5 resta valido:
- Ibrida: Web Speech API dove c'è (Chrome, Edge, Safari anche iOS: nessun download, ma l'audio va al
  fornitore del browser); altrimenti modelli nel browser (Firefox): Silero VAD per la fine della frase,
  Whisper/Moonshine con transformers.js per l'ascolto, Piper (vits-web) per la voce.
- Mezzo duplex: microfono spento mentre il lettore parla, tocco per interromperlo, «modalità
  conversazione» che riapre l'ascolto a fine risposta, testo riconosciuto modificabile nella chat, niente
  invio doppio mentre il lettore scrive.
- Peso dei modelli locali (stime, da misurare): VAD ~2 MB, runtime ONNX 10–25 MB, Whisper base/Moonshine
  base 60–80 MB, voce Piper «medium» ~60 MB → ~150–170 MB una tantum. Con Whisper tiny e voci «x_low»
  ~70 MB. Proposta: modelli piccoli, scaricati solo su richiesta con la dimensione mostrata prima e il
  consenso. Niente di tutto questo entra nel caricamento della pagina (import dinamico).
- Librerie provate il 2026-10-01 (poi tolte): `@huggingface/transformers@4.3`, `@ricky0123/vad-web@0.0.31`,
  `@diffusionstudio/vits-web@1.0.3` (ha voci per en, it, hu, ru, uk, es; l'italiano solo `riccardo-x_low`).
- Nell'app nativa (punto 1) l'ascolto e la voce del sistema operativo evitano i modelli nel browser.
