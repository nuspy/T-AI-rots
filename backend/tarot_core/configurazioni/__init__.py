"""Le configurazioni che si impostano dalla console invece che dal server (v9, Fase 2c).

Richiesta dell'operatore del 3/10: «Tutte le configurazioni devono essere lì». Sul server restano solo tre segreti:
la password del database, la chiave master di cifratura (`TAROT_LLM_PROVIDER_KEY`) e il segreto del client
`tarot-api` di Keycloak. Tutto il resto vive nel database, cifrato con la chiave master dove è un segreto.

- `correnti`: i valori in uso nel processo (database → ambiente), letti senza `await` da chi li usa;
- `segreti`: i segreti interni generati al primo avvio (impronta degli IP, sale delle condivisioni);
- `importa`: la copia una tantum dall'ambiente al database, al primo avvio;
- `avvio`: ciò che l'API fa partendo, e il rinfresco periodico dei valori;
- `stripe_console`, `smtp`, `dns`, `titolare`: le prove e le letture delle pagine della console.
"""
