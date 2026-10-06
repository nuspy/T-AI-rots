/* Texts that only the apps (Android, iPhone, iPad) use: where the site speaks of cookies and the browser, the app
 * speaks of data on the device. The site never reads this section; `scripts/genera-arb.mjs` turns it into the app's
 * `app_*` keys, like every other section. */

export const app = {
  /* the consent sheet at first launch (the site's cookie banner) */
  consensi_titolo: "Privacy and your data",
  consensi_testo: "Technical data on this device keeps the app working and needs no consent. Everything else stays off until you turn it on: accept all, reject all, or choose one by one. You can change your mind at any time in your profile.",
  consenso_statistiche: "App statistics",
  consenso_statistiche_testo: "A random identifier recognises this device when you come back. It stays with us, never with third parties.",
  consenso_google: "Google Analytics",
  consenso_google_testo: "Google Analytics for Firebase (Google Ireland) measures how the app is used, with an identifier stored on the device; data may go to the United States.",
  consenso_tecnici: "Technical data on the device (signing in, the free reading, these choices) is always kept: without it the app does not work.",
  /* «Privacy and consent» in the profile */
  cons_statistiche_testo: "A random identifier recognises this device when you come back. Turning it off makes our servers forget it.",
  cons_google_testo: "Google Analytics for Firebase measures how the app is used. Turning it off stops it at once.",
  /* the privacy page */
  scelte_titolo: "Your choices on this device",
  scelte_testo: "Everything below is off until you turn it on, and you can change it here at any time. Technical data on the device (signing in, the anonymous free reading, remembering these choices) needs no consent: without it the app does not work.",
  /* the free reading */
  gia_usata: "You have already used your free reading on this device. Create a free account to continue: it adds free readings to your story.",
  /* payments open on the web until in-app purchases arrive */
  pagamento_browser: "The payment page opens in your browser. When you have finished, you come back here.",
  pagamento_attesa: "Checking your payment…",
  pagamento_non_concluso: "The payment has not been completed. Nothing has been charged.",
  /* a video in an article opens outside the app */
  video_apri: "Watch the video on {fonte}",
  /* saving a file (your data, a PDF) */
  file_pronto: "Your file is ready: choose where to save or send it.",
  /* «Already have an account on the website?» (Fase 6): the code that moves this sign-in to the account on the site */
  codice_titolo: "Already have an account on the website?",
  codice_testo: "If you already used TAROTS chat on the website with a different sign-in, the app may have created a new account. Create a code here and enter it in your profile on the website («Do you have a code from the app?») within 10 minutes: this sign-in moves to your account there, together with what you did in the app.",
  codice_crea: "Create the code",
  codice_valido: "Valid until {ora}. On the website: Profile → Sign-in methods → «Do you have a code from the app?».",
  codice_nuovo: "Create a new code",
  codice_relay: "You signed in with Apple and hid your email, so this is a new account. If you already have one on the website, move this sign-in there now.",
  sessione_spostata_titolo: "Sign in again",
  sessione_spostata: "Your session in the app has ended. If you entered the app's code on the website, your sign-in now leads to your account there: sign in again and you will find your story.",
  sessione_entra: "Sign in again",
  /* Fase 9: the purchases in the stores (Google Play, App Store) on the pricing page */
  store_nota: "You pay with {store}. Subscriptions renew on their own until you cancel them in {store}.",
  store_non_disponibile: "Purchases with {store} aren't available on this device right now. Check that you're signed in to {store} and try again.",
  store_ripristina: "Restore purchases",
  store_ripristinati: "Purchases restored.",
  store_niente_da_ripristinare: "There was nothing to restore.",
  store_in_corso: "Checking your purchase…",
  store_in_attesa: "Your payment is pending: the credits arrive as soon as {store} confirms it. You can close the app in the meantime.",
  store_annullato: "Purchase cancelled: nothing was charged.",
  store_err_account: "This purchase was made with another TAROTS chat account: sign in with the account you bought it with.",
  store_err_registrazione: "We couldn't register this purchase yet. It's kept safe and we'll try again: if it doesn't show up within a day, write to us.",
  store_err_rete: "We can't reach our server to confirm the purchase. It's kept safe: we'll try again as soon as you're back online.",
  store_err_non_valido: "{store} didn't confirm this purchase. Nothing was added to your account.",
  store_err_posseduto: "You already own this. Tap «Restore purchases».",
  store_err_generico: "The purchase didn't go through. Please try again.",
  store_carta: "Pay by card",
  store_carta_testo: "Card payments go through Stripe on our website, and you come back here when you're done.",
  store_metodo: "How to pay",
  store_codici: "Discount codes only apply to card payments; gift codes always work.",
  store_abbonamento_web: "Your current subscription wasn't bought with {store}. To switch to {store}, turn off its automatic renewal in your profile: you can subscribe here when it ends.",
  store_altro_store: "Your subscription is managed by {store}: change or cancel it there.",
  /* Fase 9: the notifications on this device (profile → Notifications) and the Android channels */
  push_stato_attive: "Notifications are on on this device.",
  push_stato_spente: "Notifications are off on this device.",
  push_attiva: "Turn on notifications here",
  push_disattiva: "Turn off on this device",
  push_negato: "Notifications for TAROTS chat are turned off in your phone's settings. Turn them on there, then come back.",
  push_impostazioni: "Open settings",
  push_non_disponibile: "Notifications aren't available in this version of the app yet.",
  canale_servizio: "Card of the day and reminders",
  canale_servizio_testo: "Your card of the day, your streak, the end of a trial, a payment to fix.",
  canale_promozioni: "Offers and news",
  canale_promozioni_testo: "Only if you turned on promotions in your privacy choices.",
  /* Fase 9: deleting the account with a subscription bought in a store */
  elimina_store: "A subscription bought with {store} doesn't stop on its own: cancel it in {store} so it isn't renewed.",
  /* v9.5: the reading language of the contents (ML Kit, on the device) */
  lingua_titolo: "Reading language",
  lingua_testo: "Articles, cards and spreads are written in English. Choose the language you want to read them in: your phone translates them by itself, without sending them anywhere. Every language except English needs a download of about 30 MB, only once.",
  lingua_cerca: "Search for a language",
  lingua_continua: "Continue",
  lingua_scarico: "Downloading {lingua}… it can take a minute.",
  lingua_errore: "The download didn't work (are you online?). The contents stay in English for now: we'll try again when you open them.",
  lingua_voce: "Reading language: {lingua}",
  lingua_cambia: "Change",
};
