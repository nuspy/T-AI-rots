"""Il livello dati.

Qui si importano tutti i moduli dei modelli: le tabelle si riferiscono l'una
all'altra per nome, e SQLAlchemy risolve quei nomi solo fra le tabelle che ha
visto. Caricarne uno solo produce `NoReferencedTableError` al primo uso.
"""
from . import (  # noqa: F401
    analytics_models, backup_models, base, billing_models, blog_models, chat_models, config_models, consent_models, deck_models,
    deck_upload_models, memory_models, models, ordini_models, seo_models, share_models, voting_models,
)
from . import integrazioni_models  # noqa: F401  (v8.6: Google e Reddit dalla console)
from . import app_mobili_models  # noqa: F401  (v9 Fase 3: account degli store, prodotti, pulsante Stripe)
from . import abbonamenti_models  # noqa: F401  (v9 Fase 2b: impostazioni degli abbonamenti, prove, email)
from . import configurazioni_models  # noqa: F401  (v9 Fase 2c: Stripe, SMTP, titolare e segreti dalla console)
from . import acquisti_store_models  # noqa: F401  (v9 Fase 4: gli acquisti verificati di Google Play e App Store)
from . import notifiche_models  # noqa: F401  (v9 Fase 5: dispositivi, preferenze, campagne e invii delle notifiche)
from . import accesso_nativo_models  # noqa: F401  (v9 Fase 6: segreto di Apple per Keycloak, codici di collegamento)
from . import consumi_models  # noqa: F401  (i consumi delle chiamate ai modelli e i listini della pagina «Costi»)

from .backup_models import BackupEsecuzione, ImpostazioniBackup
from .base import Base, OwnedMixin, TimestampMixin, utcnow
from .billing_models import Coupon, CouponRedemption, CreditEntry, PaymentCheckout, PaymentEvent, Plan, Subscription
from .blog_models import (
    ApiKey, BlogPost, BlogPostLink, BlogPostRevision, BlogPostTag, BlogSection, BlogTag, CatalogoImmagine, MediaImage,
)
from .chat_models import ChatProattivaTurno
from .config_models import ImpostazioniCrediti, LlmProvider, ModelAssignment
from .consent_models import ConsensoStorico, UserConsent
from .deck_models import Deck, DeckCardImage, DeckUnlock, OffertaMazzo
from .deck_upload_models import DeckArtworkUpload
from .memory_models import MemoriaStato, UserMemory
from .models import AuditLog, DailyCard, DrawnCard, InterviewTurn, Reading, User
from .ordini_models import IndirizzoSpedizione, Ordine, RigaOrdine
from .seo_models import NotificaMotori
from .share_models import ShareEvent, ShareImage, ShareSignup, ShareVisit
from .voting_models import DeckCandidate, DeckSuggestion, DeckVote, VotingRound

__all__ = [
    "AuditLog",
    "BackupEsecuzione",
    "ImpostazioniBackup",
    "Base",
    "ApiKey",
    "BlogPost",
    "BlogPostLink",
    "BlogPostRevision",
    "BlogPostTag",
    "BlogSection",
    "BlogTag",
    "CatalogoImmagine",
    "ChatProattivaTurno",
    "ConsensoStorico",
    "MediaImage",
    "Coupon",
    "CouponRedemption",
    "CreditEntry",
    "DailyCard",
    "Deck",
    "DeckArtworkUpload",
    "DeckCardImage",
    "DeckCandidate",
    "DeckSuggestion",
    "DeckUnlock",
    "DeckVote",
    "DrawnCard",
    "ImpostazioniCrediti",
    "IndirizzoSpedizione",
    "InterviewTurn",
    "LlmProvider",
    "ModelAssignment",
    "NotificaMotori",
    "OffertaMazzo",
    "Ordine",
    "OwnedMixin",
    "PaymentCheckout",
    "PaymentEvent",
    "Plan",
    "Reading",
    "RigaOrdine",
    "ShareEvent",
    "ShareImage",
    "ShareSignup",
    "ShareVisit",
    "Subscription",
    "TimestampMixin",
    "User",
    "UserConsent",
    "UserMemory",
    "MemoriaStato",
    "utcnow",
    "VotingRound",
]
