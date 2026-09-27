"""Il livello dati.

Qui si importano tutti i moduli dei modelli: le tabelle si riferiscono l'una
all'altra per nome, e SQLAlchemy risolve quei nomi solo fra le tabelle che ha
visto. Caricarne uno solo produce `NoReferencedTableError` al primo uso.
"""
from . import (  # noqa: F401
    base, billing_models, blog_models, config_models, deck_models, models, ordini_models, share_models,
)

from .base import Base, OwnedMixin, TimestampMixin, utcnow
from .billing_models import Coupon, CouponRedemption, CreditEntry, PaymentCheckout, PaymentEvent, Plan, Subscription
from .blog_models import (
    ApiKey, BlogPost, BlogPostLink, BlogPostRevision, BlogPostTag, BlogSection, BlogTag, MediaImage,
)
from .config_models import ImpostazioniCrediti, LlmProvider, ModelAssignment
from .deck_models import Deck, DeckUnlock, OffertaMazzo
from .models import AuditLog, DailyCard, DrawnCard, InterviewTurn, Reading, User
from .ordini_models import Ordine, RigaOrdine
from .share_models import ShareEvent, ShareImage, ShareSignup, ShareVisit

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
    "MediaImage",
    "Coupon",
    "CouponRedemption",
    "CreditEntry",
    "DailyCard",
    "Deck",
    "DeckUnlock",
    "DrawnCard",
    "ImpostazioniCrediti",
    "InterviewTurn",
    "LlmProvider",
    "ModelAssignment",
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
    "utcnow",
]
