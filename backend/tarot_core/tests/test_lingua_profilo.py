"""La lingua scelta dal menu del sito aggiorna il profilo (v9, Fase 2d), e il claim `locale` del token non la annulla.

Regola: il claim vale alla nascita dell'utente e finché la persona non sceglie dal sito (menu o profilo,
`users.locale_scelta_il`); dopo, la lingua è quella scelta, e oracolo, email e notifiche la seguono.
"""
from __future__ import annotations

import re
from pathlib import Path

from tarot_core.auth.keycloak import Principal
from tarot_core.domain.repositories import UserRepository
from tarot_core.tarot.lingue import LINGUE

from .conftest import richiede_database


def _con_claim(sub: str, locale: str) -> Principal:
    return Principal(subject=sub, email=f"{sub}@example.com", display_name="Lingua", roles={"user"},
                     raw_claims={"sub": sub, "locale": locale}, locale=locale)


@richiede_database
async def test_il_claim_vale_alla_nascita_e_finche_non_si_sceglie_dal_sito(session):
    repo = UserRepository(session)
    utente = await repo.ensure(_con_claim("sub-l1", "hu"))
    assert utente.locale == "hu" and utente.locale_scelta_il is None
    # Prima di una scelta dal sito il claim segue Keycloak, com'era.
    assert (await repo.ensure(_con_claim("sub-l1", "es"))).locale == "es"
    # Una lingua che il sito non ha non si scrive; «pt-BR» diventa «pt».
    assert (await repo.ensure(_con_claim("sub-l1", "xx"))).locale == "es"
    assert (await repo.ensure(_con_claim("sub-l1", "pt-BR"))).locale == "pt"


@richiede_database
async def test_la_scelta_dal_menu_va_nel_profilo_e_il_token_non_la_annulla(client, session):
    principal_utente = _con_claim("sub-l2", "it")
    client.identita.principal = principal_utente
    assert (await client.get("/me/profile")).json()["locale"] == "it"
    r = await client.patch("/me/profile", json={"locale": "uk"})
    assert r.status_code == 200, r.text
    assert r.json()["locale"] == "uk" and r.json()["locale_scelta_il"]
    # Le richieste dopo portano ancora il claim «it» (la lingua della pagina di accesso): la scelta resta.
    profilo = (await client.get("/me/profile")).json()
    assert profilo["locale"] == "uk"
    utente = await UserRepository(session).ensure(principal_utente)
    assert utente.locale == "uk"
    # Una lingua che il sito non ha si rifiuta.
    assert (await client.patch("/me/profile", json={"locale": "xx"})).status_code == 422


def test_le_lingue_del_menu_sono_quelle_del_profilo():
    """Il menu offre le quindici lingue di `frontend/lib/i18n/lingue.ts`; `users.locale` accetta quelle di
    `tarot/lingue.py`: devono essere le stesse, o una scelta dal menu verrebbe rifiutata dal profilo."""
    radice = Path(__file__).resolve().parents[3]
    sorgente = (radice / "frontend" / "lib" / "i18n" / "lingue.ts").read_text(encoding="utf-8")
    menu = re.findall(r'\{\s*codice:\s*"([a-z]{2})"', sorgente)
    assert menu and set(menu) == set(LINGUE)
