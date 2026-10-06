"""I contenuti di un utente in console (v9.5): letture, chat, memorie e profilazione, solo con un motivo, e ogni
accesso nel registro."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.domain.base import utcnow
from tarot_core.domain.chat_models import ChatProattivaTurno
from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.models import AuditLog, DrawnCard, InterviewTurn, Reading, User

from .conftest import richiede_database

pytestmark = [richiede_database, pytest.mark.asyncio]

MOTIVO = "Segnalazione di abuso n. 12"


async def _dati(session, utente) -> Reading:
    adesso = utcnow()
    lettura = Reading(owner_id=utente.id, spread_id="tre-carte", question="Tornerà da me?", status="completata",
                      lang="it", consumo="credito", synthesis="Il responso finale.", context_summary="Il quadro.")
    session.add(lettura)
    await session.flush()
    session.add_all([
        InterviewTurn(reading_id=lettura.id, ordine=1, ruolo="oracolo", testo="Da quanto vi siete lasciati?",
                      created_at=adesso),
        InterviewTurn(reading_id=lettura.id, ordine=2, ruolo="utente", testo="Da tre mesi.", created_at=adesso),
        DrawnCard(reading_id=lettura.id, posizione=1, slot=4, card_id="maj-06", rovescio=False,
                  interpretazione="Gli Amanti: una scelta.", created_at=adesso),
        ChatProattivaTurno(owner_id=utente.id, ordine=1, ruolo="utente", testo="Ciao, ho paura."),
        ChatProattivaTurno(owner_id=utente.id, ordine=2, ruolo="ai", testo="Raccontami.",
                           proposta={"argomento": "paura", "categoria": "spirito"}),
        UserMemory(owner_id=utente.id, contenuto="Si è separata da tre mesi.", tipo="variabile",
                   campo_attinenza="amore", embedding=[0.0] * 8, reading_id=lettura.id, fonte="lettura"),
    ])
    await session.commit()
    return lettura


async def _accesso(client, user_id: int, motivo: str = MOTIVO):
    return await client.post(f"/admin/users/{user_id}/contenuti/accesso", json={"motivo": motivo})


async def test_senza_motivo_i_contenuti_restano_chiusi(client, utente, principal_admin, session):
    await _dati(session, utente)
    client.identita.principal = principal_admin
    for scheda in ("letture", "chat", "memorie", "profilo"):
        r = await client.get(f"/admin/users/{utente.id}/contenuti/{scheda}")
        assert r.status_code == 403, (scheda, r.text)
    r = await client.get(f"/admin/users/{utente.id}/contenuti/letture", params={"accesso": "inventato"})
    assert r.status_code == 403
    assert (await _accesso(client, utente.id, "boh")).status_code == 422


async def test_con_il_motivo_si_leggono_letture_chat_memorie_e_profilo(client, utente, principal_admin, session):
    await _dati(session, utente)
    client.identita.principal = principal_admin
    r = await _accesso(client, utente.id)
    assert r.status_code == 200, r.text
    accesso = r.json()["accesso"]

    r = await client.get(f"/admin/users/{utente.id}/contenuti/letture", params={"accesso": accesso})
    assert r.status_code == 200, r.text
    lettura = r.json()["letture"][0]
    assert lettura["domanda"] == "Tornerà da me?" and lettura["sintesi"] == "Il responso finale."
    assert [t["testo"] for t in lettura["intervista"]] == ["Da quanto vi siete lasciati?", "Da tre mesi."]
    assert lettura["carte"][0]["carta"] == "maj-06" and "deck_state" not in lettura

    chat = (await client.get(f"/admin/users/{utente.id}/contenuti/chat", params={"accesso": accesso})).json()
    assert [m["testo"] for m in chat["messaggi"]] == ["Raccontami.", "Ciao, ho paura."]

    memorie = (await client.get(f"/admin/users/{utente.id}/contenuti/memorie", params={"accesso": accesso})).json()
    assert memorie["memorie"][0]["contenuto"] == "Si è separata da tre mesi."
    assert "embedding" not in memorie["memorie"][0]

    profilo = (await client.get(f"/admin/users/{utente.id}/contenuti/profilo", params={"accesso": accesso})).json()
    assert profilo["persona"]["email"] == utente.email and "consensi" in profilo

    registro = (await session.execute(
        select(AuditLog.action, AuditLog.after).where(AuditLog.target_id == str(utente.id),
                                                      AuditLog.action.like("admin.contenuti.%"))
        .order_by(AuditLog.id)
    )).all()
    assert registro[0][0] == "admin.contenuti.accesso" and registro[0][1]["motivo"] == MOTIVO
    assert [a["scheda"] for _azione, a in registro[1:]] == ["letture", "chat", "memorie", "profilo"]

    accessi = (await client.get(f"/admin/users/{utente.id}/contenuti/accessi")).json()["accessi"]
    assert accessi[-1]["motivo"] == MOTIVO and accessi[0]["scheda"] == "profilo"


async def test_un_accesso_vale_solo_per_quell_utente(client, utente, principal_admin, session):
    await _dati(session, utente)
    client.identita.principal = principal_admin
    accesso = (await _accesso(client, utente.id)).json()["accesso"]
    # l'amministratore stesso è un altro utente: l'accesso aperto per `utente` non vale per lui
    admin_id = (await session.execute(select(User.id).where(User.keycloak_sub == "sub-admin"))).scalar_one()
    r = await client.get(f"/admin/users/{admin_id}/contenuti/letture", params={"accesso": accesso})
    assert r.status_code == 403


async def test_un_utente_normale_non_entra(client, utente):
    r = await client.post(f"/admin/users/{utente.id}/contenuti/accesso", json={"motivo": MOTIVO})
    assert r.status_code == 403
