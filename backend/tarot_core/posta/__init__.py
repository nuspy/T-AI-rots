"""Le email agli utenti (v9, Fase 2b): rinnovo automatico, prova, pagamenti falliti, rinnovi, sospensioni.

Prima di questo modulo all'utente non partiva nessuna email: solo il rapporto settimanale agli amministratori
(`analytics/rapporto.py`). Si usa lo stesso SMTP (`TAROT_SMTP_*`) con `lanterna.posta`; i testi stanno in
`modelli.py`, l'invio e il registro anti-doppioni in `invio.py`.
"""
from .invio import data_in, importo_in, lingua_di, manda

__all__ = ["data_in", "importo_in", "lingua_di", "manda"]
