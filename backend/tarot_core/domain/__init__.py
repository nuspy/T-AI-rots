"""Il livello dati.

Qui si importano tutti i moduli dei modelli: le tabelle si riferiscono l'una
all'altra per nome, e SQLAlchemy risolve quei nomi solo fra le tabelle che ha
visto. Caricarne uno solo produce `NoReferencedTableError` al primo uso.
"""
from . import base, billing_models, blog_models, config_models, models, share_models  # noqa: F401

from .base import Base, OwnedMixin, TimestampMixin, utcnow
from .billing_models import Coupon, CouponRedemption, CreditEntry, PaymentCheckout, PaymentEvent, Plan, Subscription
from .blog_models import (
    ApiKey, BlogPost, BlogPostLink, BlogPostRevision, BlogPostTag, BlogSection, BlogTag, MediaImage,
)
from .config_models import ModelAssignment
from .models import AuditLog, DailyCard, DrawnCard, InterviewTurn, Reading, User
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
    "DrawnCard",
    "InterviewTurn",
    "ModelAssignment",
    "OwnedMixin",
    "PaymentCheckout",
    "PaymentEvent",
    "Plan",
    "Reading",
    "ShareEvent",
    "ShareImage",
    "ShareSignup",
    "ShareVisit",
    "Subscription",
    "TimestampMixin",
    "User",
    "utcnow",
]
