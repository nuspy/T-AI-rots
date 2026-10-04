"""Gli acquisti nelle app (v9, Fase 4): Google Play e App Store, verificati presso lo store e accreditati qui.

- `comune.py`: ciò che vale per entrambi — dal prodotto comprato al piano (`prodotti_store`), dall'acquisto
  all'account (il token dell'account per gli store), l'accredito e l'abbonamento passando da
  `GestorePagamenti.applica` con id evento `gp:<ordine>` / `as:<transazione>`, gli storni, lo stato locale che segue
  quello dello store.
- `google_play.py`: la Play Developer API (acquisti, abbonamenti, conferma, rimborsi) e le notifiche RTDN di
  Pub/Sub con il loro token OIDC.
- `app_store.py`: le transazioni firmate di StoreKit 2 (JWS verificati fino ad Apple Root CA G3 con la libreria
  ufficiale `app-store-server-library`), le Server Notifications V2 e la App Store Server API.

Il denaro lo incassa lo store; qui arriva solo la prova firmata che l'ha incassato.
"""
