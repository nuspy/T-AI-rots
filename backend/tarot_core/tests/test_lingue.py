"""La lingua del quesito: rilevamento, istruzione al modello, testi fissi."""
from __future__ import annotations

import pytest

from tarot_core.tarot.lingue import (
    LINGUE, TRADOTTE, in_lingua, istruzione_lingua, lingua, rileva_lingua,
)

QUESITI = {
    "it": "Devo accettare la nuova offerta di lavoro in un'altra città?",
    "en": "Should I take the new job offer in another city?",
    "hu": "El kell fogadnom az új állásajánlatot egy másik városban?",
    "de": "Soll ich das neue Jobangebot in einer anderen Stadt annehmen?",
    "fr": "Dois-je accepter la nouvelle offre d'emploi dans une autre ville ?",
    "es": "¿Debo aceptar la nueva oferta de trabajo en otra ciudad?",
    "pt": "Devo aceitar a nova oferta de emprego em outra cidade?",
    "ro": "Ar trebui să accept noua ofertă de muncă într-un alt oraș?",
    "pl": "Czy powinienem przyjąć nową ofertę pracy w innym mieście?",
    "ru": "Стоит ли мне принять новое предложение о работе в другом городе?",
    "uk": "Чи варто мені прийняти нову пропозицію роботи в іншому місті?",
    "zh": "我应该接受另一个城市的新工作机会吗？",
    "hi": "क्या मुझे दूसरे शहर में नई नौकरी का प्रस्ताव स्वीकार करना चाहिए?",
    "ko": "다른 도시의 새 일자리 제안을 받아들여야 할까요?",
    "ar": "هل يجب أن أقبل عرض العمل الجديد في مدينة أخرى؟",
}


def test_ci_sono_le_quindici_lingue():
    assert list(LINGUE) == list(QUESITI) or set(LINGUE) == set(QUESITI)
    assert len(LINGUE) == 15 and set(TRADOTTE) == {"it", "en", "hu"}


@pytest.mark.parametrize("codice", list(QUESITI))
def test_riconosce_la_lingua_del_quesito(codice):
    # Anche se l'interfaccia è in un'altra lingua: vale il quesito.
    interfaccia = "it" if codice != "it" else "en"
    assert rileva_lingua(QUESITI[codice], fallback=interfaccia) == codice


def test_senza_indizi_si_tiene_la_lingua_dell_interfaccia():
    assert rileva_lingua("", fallback="hu") == "hu"
    assert rileva_lingua("???", fallback="de") == "de"
    assert rileva_lingua("Tarot", fallback="fr") == "fr"


def test_il_giapponese_non_c_e_si_tiene_l_interfaccia():
    assert rileva_lingua("私は新しい仕事を受けるべきですか？", fallback="en") == "en"


def test_l_istruzione_nomina_la_lingua_del_quesito():
    assert "ungherese" in istruzione_lingua("hu")
    assert "la lingua in cui chi consulta ha posto il quesito" in istruzione_lingua("it")
    assert "italiano" not in istruzione_lingua("hu")
    # Una lingua non supportata ricade sull'italiano, come sempre.
    assert lingua("xx") == "it" and lingua("pt-BR") == "pt" and lingua("ZH_cn") == "zh"


def test_i_testi_fissi_ricadono_sull_inglese():
    testi = {"it": "ciao", "en": "hello", "hu": "szia"}
    assert in_lingua(testi, "hu") == "szia" and in_lingua(testi, "it") == "ciao"
    assert in_lingua(testi, "de") == "hello" and in_lingua(testi, "zh") == "hello"


@pytest.mark.parametrize("quesito, atteso", [
    ("Compatibilità con Marco", "it"),
    ("Relazione di coppia con Marco", "it"),
    ("Compatibility with Marco", "en"),
    ("Couple relationship with Marco", "en"),
    ("Kompatibilitás vele: Marco", "hu"),
    ("Párkapcsolat vele: Marco", "hu"),
])
def test_i_quesiti_generati_per_le_letture_speciali_hanno_la_lingua_giusta(quesito, atteso):
    # Il quesito di ripiego è breve e decide la lingua di tutta la lettura: il nome del
    # partner non deve spostarla, qualunque sia la lingua dell'interfaccia.
    for interfaccia in ("it", "en", "hu"):
        assert rileva_lingua(quesito, fallback=interfaccia) == atteso
