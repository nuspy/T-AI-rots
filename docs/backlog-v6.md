# Backlog v6 — richieste rimandate

Funzionalità richieste dall'utente ma esplicitamente rimandate a un rilascio futuro (v6), non ancora
iniziate. Registrate qui perché non vadano perse tra una sessione e l'altra.

---

## 1. Richiamo "leggi le tue carte" in home — da verificare/rafforzare

L'utente segnala: manca sulla home page il richiamo a "leggi le tue carte" — una delle funzioni
distintive del sito. **Nota di verifica**: un banner per questa funzione esiste già nel codice
(`frontend/app/componenti/banner-interpreta.tsx`, collegato a `/interpreta`, la funzione "Interpreta
i miei tarocchi" della Fase C di v5) ed è presente in `app/page.tsx`; confermato anche in produzione
(`https://tarots.chat/` contiene il link `/interpreta` dopo il deploy v5). Non è quindi assente dal
codice — ma l'utente lo percepisce come mancante, il che suggerisce che vada reso più visibile/
prominente, oppure che si riferisca a qualcos'altro con lo stesso nome informale. Da chiarire con
l'utente prima di intervenire: cosa esattamente manca (posizione, visibilità, testo, un concetto
diverso da "Interpreta i miei tarocchi").
