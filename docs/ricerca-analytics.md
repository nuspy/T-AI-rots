# Analytics: cosa offrono i prodotti commerciali e cosa abbiamo (backlog v8, punto 8)

Data: 2026-09-30. Fonte: conoscenza delle funzioni pubbliche dei prodotti (documentazione e pagine
prodotto note), **non** una ricerca web aggiornata di oggi: prezzi e dettagli vanno riverificati prima
di citarli. Serve a una cosa sola: capire se a `lanterna` manca qualcosa che conti per le decisioni.

Prodotti considerati: **GA4** (Google Analytics 4), **Matomo**, **Plausible / Umami / Fathom** (analytics
leggeri senza cookie), **PostHog**, **Mixpanel / Amplitude** (product analytics), e per l'analisi
clienti **HubSpot / Customer.io** (CRM e automazione).

## Funzioni e copertura

| Funzione | Chi la offre | Noi |
|---|---|---|
| Pagine viste, sessioni, visitatori, tempo, rimbalzo | tutti | ✓ (visitatori = univoci giornalieri, senza cookie) |
| Canali, referrer, UTM, raggruppamento predefinito | GA4, Matomo, Plausible, PostHog | ✓ (con «assistenti AI» come canale a sé) |
| Paese, regione, città | tutti | ✓ (DB-IP locale, città indicativa) |
| Dispositivo, browser, sistema | tutti | ✓ (in categorie) |
| Nuovi / di ritorno, frequenza | GA4, Matomo, Mixpanel | ✓ solo per chi ha accesso o cookie accettati (dichiarato) |
| Eventi personalizzati e proprietà | tutti | ✓ (`data-an`, `traccia()`, eventi di server) |
| Eventi di business dal server (acquisti veri) | GA4 (Measurement Protocol), Mixpanel, PostHog | ✓ nella stessa transazione del fatto |
| Imbuti | GA4, Matomo (premium), PostHog, Mixpanel | ✓ predefiniti (lettura, iscrizione, acquisto, negozio), segmentabili |
| Coorti e ritenzione | GA4, PostHog, Mixpanel, Amplitude | ✓ (letture, ritorni, spesa per mese d'iscrizione) |
| Valore del cliente (LTV) | GA4, Mixpanel, CRM | ✓ come coorte di spesa |
| Attribuzione primo contatto | tutti | ✓ |
| Attribuzione ultimo contatto / modelli multi-touch | GA4, Matomo (premium) | parziale: l'acquisto eredita la sessione che lo porta; nessun modello multi-touch |
| Esploratore libero, incroci, drill-down | GA4 (Esplorazioni), Mixpanel, PostHog | ✓ (catalogo dichiarato, fino a 3 dimensioni) |
| Export CSV/Excel, rapporti email programmati | GA4 (Looker Studio), Matomo | ✓ (vista, collezioni, email del lunedì) |
| Accesso ai dati per notebook / data warehouse | GA4 (BigQuery), PostHog, Mixpanel | ✓ Colab con token e reimport firmato |
| Interpretazione automatica («insights») | GA4 (Analytics Intelligence), Amplitude, Mixpanel (Spark) | ✓ con fatti numerati e verifica dei numeri, su richiesta |
| Segmenti salvati | GA4, Matomo, Mixpanel | parziale: la vista dell'Esploratore sta nell'indirizzo (si salva come link) |
| **Annotazioni sui grafici** (campagne, rilasci) | GA4, Matomo, Plausible, PostHog | ✗ |
| **Avvisi automatici** su anomalie o soglie | GA4 (avvisi personalizzati), Matomo, Amplitude | ✗ (le anomalie si vedono solo chiedendo l'analisi AI) |
| **Obiettivi / conversioni configurabili** dalla console | GA4, Matomo, Plausible | ✗ (eventi e imbuti sono definiti nel codice) |
| **Tempo reale** (chi c'è adesso) | GA4, Matomo, Plausible, PostHog | ✗ |
| Parole chiave di ricerca | via Search Console (GA4, Matomo, Plausible) | ✗ (servirebbe il service account Search Console) |
| Web vitals / prestazioni | Plausible, PostHog, GA4 (limitato) | ✗ |
| Registrazione delle sessioni, heatmap | Matomo (premium), PostHog, Hotjar | ✗ — scelta: invasivo, e le letture sono dati intimi |
| Esperimenti A/B, feature flag | PostHog, Amplitude, GA4 (con altri strumenti) | ✗ |
| CRM: schede cliente, segmenti per campagne email | HubSpot, Customer.io | ✗ fuori dall'ambito (analytics aggregati, non profilazione) |

## Cosa ne segue

Il nucleo che serve alle decisioni di un servizio piccolo è coperto. Le lacune che varrebbe la pena
colmare, in ordine di utilità stimata:

1. **Annotazioni**: segnare sul calendario campagne, rilasci, articoli, cambi di prezzo; comparirebbero
   sui grafici e nei fatti dati all'AI («la crescita inizia il giorno della campagna X»). Poco lavoro,
   molto valore interpretativo.
2. **Avvisi**: il giro notturno controlla poche metriche (visite, iscrizioni, acquisti, letture
   completate, errori del modello) e manda un'email quando escono dal normale (stessa statistica
   robusta già usata per le anomalie).
3. **Parole chiave dalla Search Console**: stesso service account già previsto per le sitemap.
4. **Obiettivi configurabili** dalla console (un evento o una pagina = una conversione), senza toccare
   il codice.
5. **Tempo reale** minimo: sessioni degli ultimi 5 minuti e pagine aperte.

Da non fare, per scelta: registrazione delle sessioni e heatmap (invasive, e il contenuto delle letture
è intimo), profilazione di tipo CRM (fuori dalla base giuridica documentata in
`docs/privacy/lia-analytics.md`).
