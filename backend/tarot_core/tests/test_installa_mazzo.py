"""L'installazione di un mazzo nuovo (v8.5): controllo dei 78+1 file e copia nel frontend, idempotente."""
from __future__ import annotations

import pytest

from tarot_core.tools import installa_mazzo


def _mazzo(radice, nome_set, togli=()):
    web = radice / "Grafica" / "Cards" / nome_set / "Web"
    web.mkdir(parents=True)
    for nome in installa_mazzo.nomi_attesi():
        if nome not in togli:
            (web / nome).write_bytes(nome.encode())
    return web


def test_i_nomi_attesi_sono_le_78_carte_e_il_dorso():
    nomi = installa_mazzo.nomi_attesi()
    assert len(nomi) == 79 and "dorso.webp" in nomi and "maj-00.webp" in nomi and "dischi-principessa.webp" in nomi


def test_un_mazzo_completo_si_copia_una_volta_sola(tmp_path):
    _mazzo(tmp_path, "Prova")
    assert installa_mazzo.installa_file("Prova", "prova", radice=tmp_path) == 79
    assert len(list((tmp_path / "frontend" / "public" / "cards" / "prova").glob("*.webp"))) == 79
    assert installa_mazzo.installa_file("Prova", "prova", radice=tmp_path) == 0


def test_un_mazzo_incompleto_non_si_installa(tmp_path):
    _mazzo(tmp_path, "Monco", togli=("maj-13.webp", "dorso.webp"))
    with pytest.raises(SystemExit, match="mancano 2 file"):
        installa_mazzo.installa_file("Monco", "monco", radice=tmp_path)
    assert not (tmp_path / "frontend").exists()
