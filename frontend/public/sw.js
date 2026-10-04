/* Il service worker di TAROTS chat (v9, Fase 5): solo le notifiche Web Push.
 *
 * Fa due cose e basta: mostra la notifica che arriva (`push`) e, al tocco, apre la pagina giusta e dice al server che
 * è stata aperta (`notificationclick`). Nessuna cache, nessun `fetch`: il sito non funziona offline e non deve
 * sembrare che lo faccia; una versione vecchia delle pagine servita da qui sarebbe solo un guaio.
 *
 * Il messaggio arriva cifrato per questo browser (RFC 8291) e il browser lo decifra prima di passarlo qui:
 * `{titolo, corpo, link, immagine, tag, invio, firma, api, azioni}`. `firma` (HMAC del server) serve a segnare
 * l'apertura senza bisogno dell'accesso. */

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(self.clients.claim());
});

self.addEventListener("push", (evento) => {
  let dati = {};
  try {
    dati = evento.data ? evento.data.json() : {};
  } catch {
    dati = { corpo: evento.data ? evento.data.text() : "" };
  }
  const titolo = dati.titolo || "TAROTS chat";
  const azioni = Array.isArray(dati.azioni) ? dati.azioni.slice(0, 2) : [];
  const opzioni = {
    body: dati.corpo || "",
    icon: "/icon.png",
    badge: "/icon.png",
    tag: dati.tag || undefined,
    // Una notifica nuova dello stesso tipo sostituisce la vecchia senza suonare di nuovo.
    renotify: false,
    data: {
      link: typeof dati.link === "string" && dati.link.startsWith("/") ? dati.link : "/",
      invio: dati.invio || null,
      firma: dati.firma || null,
      api: dati.api || null,
      azioni: Object.fromEntries(azioni.map((a) => [a.azione, a.link])),
    },
    actions: azioni.map((a) => ({ action: a.azione, title: a.titolo })),
  };
  if (dati.immagine) opzioni.image = dati.immagine;
  evento.waitUntil(self.registration.showNotification(titolo, opzioni));
});

self.addEventListener("notificationclick", (evento) => {
  const dati = evento.notification.data || {};
  evento.notification.close();

  // «Niente più promozioni»: il link firmato apre la pagina di conferma del server.
  const esterno = evento.action && dati.azioni ? dati.azioni[evento.action] : null;
  const destinazione = esterno || new URL(dati.link || "/", self.location.origin).href;

  const apertura = dati.invio && dati.firma && dati.api
    ? fetch(`${dati.api}/notifiche/aperta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invio: dati.invio, firma: dati.firma }),
      keepalive: true,
    }).catch(() => undefined)
    : Promise.resolve();

  const finestra = self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((aperte) => {
    if (!esterno) {
      // Una scheda del sito già aperta: la si porta davanti e la si manda alla pagina.
      for (const c of aperte) {
        if (new URL(c.url).origin === self.location.origin && "focus" in c) {
          return c.focus().then((f) => (f && "navigate" in f ? f.navigate(destinazione) : undefined));
        }
      }
    }
    return self.clients.openWindow(destinazione);
  });

  evento.waitUntil(Promise.all([apertura, finestra]));
});
