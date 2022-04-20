"""Model"""
from pathlib import Path

import sqlalchemy as sqla

from bemserver_core.database import Base
from bemserver_core.authorization import AuthMixin


AUTH_POLAR_FILES = [
    Path(__file__).parent / "authorization.polar",
]


class TestPluginEnableCampaign(AuthMixin, Base):
    __tablename__ = "p_enable_campaigns"

    id = sqla.Column(sqla.Integer, primary_key=True)
    campaign_id = sqla.Column(
        sqla.ForeignKey("campaigns.id"), unique=True, nullable=False
    )
    enabled = sqla.Column(sqla.Boolean, nullable=False)


AUTH_MODEL_CLASSES = [
    TestPluginEnableCampaign,
]
