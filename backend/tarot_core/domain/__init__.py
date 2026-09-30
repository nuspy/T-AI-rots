"""Il livello dati.

Qui si importano tutti i moduli dei modelli: le tabelle si riferiscono l'una
all'altra per nome, e SQLAlchemy risolve quei nomi solo fra le tabelle che ha
visto. Caricarne uno solo produce `NoReferencedTableError` al primo uso.
"""
from . import (  # noqa: F401
    analytics_models, base, billing_models, blog_models, chat_models, config_models, consent_models, deck_models,
    deck_upload_models, memory_models, models, ordini_models, seo_models, share_models, voting_models,
)

from .base import Base, OwnedMixin, TimestampMixin, utcnow
from .billing_models import Coupon, CouponRedemption, CreditEntry, PaymentCheckout, PaymentEvent, Plan, Subscription
from .blog_models import (
    ApiKey, BlogPost, BlogPostLink, BlogPostRevision, BlogPostTag, BlogSection, BlogTag, MediaImage,
)
from .chat_models import ChatProattivaTurno
from .config_models import ImpostazioniCrediti, LlmProvider, ModelAssignment
from .consent_models import UserConsent
from .deck_models import Deck, DeckUnlock, OffertaMazzo
from .deck_upload_models import DeckArtworkUpload
from .memory_models import UserMemory
from .models import AuditLog, DailyCard, DrawnCard, InterviewTurn, Reading, User
from .ordini_models import IndirizzoSpedizione, Ordine, RigaOrdine
from .seo_models import NotificaMotori
from .share_models import ShareEvent, ShareImage, ShareSignup, ShareVisit
from .voting_models import DeckCandidate, DeckSuggestion, DeckVote, VotingRound

__all__ = [
    "AuditLog",
    "Base",
    "ApiKey",
    "BlogPost",
    "BlogPostLink",
    "BlogPostRevision",
    "BlogPostTag",
    "BlogSection",
    "BlogTag",
    "ChatProattivaTurno",
    "MediaImage",
    "Coupon",
    "CouponRedemption",
    "CreditEntry",
    "DailyCard",
    "Deck",
    "DeckArtworkUpload",
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
    "utcnow",
    "VotingRound",
]
