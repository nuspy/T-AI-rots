"""La commissione di referral: una quota di ogni acquisto futuro di chi è stato invitato, per chi lo ha invitato.

Diversa dal regalo di benvenuto (una tantum all'iscrizione/al riscatto, coperto in `test_flusso.py` e
`test_impostazioni_crediti.py`): qui il codice d'invito è già collegato direttamente (`referred_by` impostato a
mano, come se il riscatto fosse già avvenuto), per isolare la commissione dal resto della matematica dei crediti.
"""
from __future__ import annotations

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.billing.plans import GestoreAbbonamenti
from tarot_core.domain.base import utcnow
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database
from .test_offerte import _paga, _piano

pytestmark = richiede_database


async def _collega_invito(session, principal_invitante, principal_invitato):
    """Come se l'invitato avesse già riscatto il codice: solo `referred_by`, niente crediti di benvenuto (che
    passano dall'HTTP, non da `ensure()`) — così un test sulla commissione non deve tenerne conto."""
    invitante = await UserRepository(session).ensure(principal_invitante)
    invitato = await UserRepository(session).ensure(principal_invitato)
    invitato.referred_by = invitante.id
    await session.commit()
    return invitante, invitato


async def test_un_pacchetto_paga_la_commissione_a_chi_ha_invitato(client, session, catalogo, principal_altro):
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    client.identita.principal = principal_altro

    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    await _paga(client, r.json()["checkout_id"])

    # 15 crediti del pacchetto, 20% predefinito = 3.
    assert await RegistroCrediti(session).saldo(invitante.id) == 3
    assert await RegistroCrediti(session).saldo(invitato.id) == 15


async def test_il_primo_periodo_di_un_abbonamento_paga_la_commissione(
    client, session, catalogo, principal_altro, principal_admin,
):
    """Fase 2b: l'abbonamento non dà crediti, la commissione è il 20% dell'importo pagato, convertito al prezzo per
    credito del pacchetto più economico (seed: 5 crediti a 4,90 €, cioè 0,98 € l'uno)."""
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    client.identita.principal = principal_admin
    piano = await _piano(
        client, slug="abbonamento-prova-commissione", tipo="abbonamento",
        price_monthly=5000, credits_per_period=0, letture_al_giorno=3,
    )
    client.identita.principal = principal_altro

    r = await client.post("/me/checkout", json={"piano": piano["slug"], "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    assert r.json()["importo"] == 4000          # 50 € col 20% del rinnovo automatico
    await _paga(client, r.json()["checkout_id"])

    # 20% di 40 € = 8 €; 8 € / 0,98 € = 8,16 → 8 crediti.
    assert await RegistroCrediti(session).saldo(invitante.id) == 8
    assert await RegistroCrediti(session).saldo(invitato.id) == 0       # l'abbonamento non dà crediti


async def test_ogni_rinnovo_paga_di_nuovo_la_commissione(
    client, session, catalogo, principal_altro, principal_admin,
):
    """Il primo periodo passa dal checkout vero (come l'altro test); solo il rinnovo — un lavoro periodico, non un
    endpoint — si chiama direttamente su `GestoreAbbonamenti`."""
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    client.identita.principal = principal_admin
    piano_json = await _piano(
        client, slug="abbonamento-prova-rinnovo", tipo="abbonamento",
        price_monthly=5000, credits_per_period=0, letture_al_giorno=3,
    )
    client.identita.principal = principal_altro

    r = await client.post("/me/checkout", json={"piano": piano_json["slug"], "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    await _paga(client, r.json()["checkout_id"])
    assert await RegistroCrediti(session).saldo(invitante.id) == 8       # il primo periodo, dal checkout

    gestore = GestoreAbbonamenti(session)
    abbonamento = await gestore.abbonamento_di(invitato.id)
    assert abbonamento is not None
    abbonamento.period_end = utcnow()
    await gestore.rinnova(abbonamento)
    await session.commit()
    assert abbonamento.importo_periodo == 4000
    assert await RegistroCrediti(session).saldo(invitante.id) == 16      # +8 al rinnovo, cumulativo

async def test_se_chi_ha_invitato_ha_cancellato_l_account_l_acquisto_prosegue_senza_conseguenze(
    client, session, catalogo, principal_altro,
):
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    invitante.deleted_at = utcnow()
    await session.commit()
    client.identita.principal = principal_altro

    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    await _paga(client, r.json()["checkout_id"])              # non deve sollevare né rispondere errore

    assert await RegistroCrediti(session).saldo(invitato.id) == 15      # il compratore ha comunque i suoi crediti
    assert await RegistroCrediti(session).saldo(invitante.id) == 0      # nessuna commissione a un account cancellato


async def test_un_pacchetto_azzerato_da_coupon_non_paga_commissione(
    client, session, catalogo, principal_altro, principal_admin,
):
    """Non è un acquisto vero (nessuno paga): niente commissione, come `admin_offerte.py` già dice per la vendita."""
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    client.identita.principal = principal_admin
    r = await client.post("/admin/coupons", json={"code": "GRATIS100COMM", "tipo": "percentuale", "valore": 100})
    assert r.status_code == 201, r.text

    client.identita.principal = principal_altro
    r = await client.post(
        "/me/checkout", json={"piano": "pacchetto-15", "coupon": "gratis100comm", "ritorno": "/piano"},
    )
    assert r.status_code == 201 and r.json()["gratis"] is True, r.text

    assert await RegistroCrediti(session).saldo(invitato.id) == 15
    assert await RegistroCrediti(session).saldo(invitante.id) == 0


async def test_la_percentuale_si_cambia_dalla_console(
    client, session, catalogo, principal_altro, principal_admin,
):
    invitante, invitato = await _collega_invito(session, client.identita.principal, principal_altro)
    client.identita.principal = principal_admin
    r = await client.put("/admin/impostazioni-crediti", json={"commissione_referral_percentuale": 50})
    assert r.status_code == 200 and r.json()["commissione_referral_percentuale"] == 50

    client.identita.principal = principal_altro
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    await _paga(client, r.json()["checkout_id"])

    assert await RegistroCrediti(session).saldo(invitante.id) == 8       # round(15 * 0.5) = 8 (arrotondamento bancario a parte)
