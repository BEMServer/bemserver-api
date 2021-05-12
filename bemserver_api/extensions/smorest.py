"""REST API extension"""

import marshmallow as ma
import flask_smorest
import marshmallow_sqlalchemy as msa


class Api(flask_smorest.Api):
    """Api class"""


class Blueprint(flask_smorest.Blueprint):
    """Blueprint class"""


class Schema(ma.Schema):
    """Schema class"""

    # Ensures the fields are ordered
    set_class = ma.orderedset.OrderedSet

    def update(self, obj, data):
        """Update object nullifying missing data"""
        loadable_fields = [
            k for k, v in self.fields.items() if not v.dump_only
        ]
        for name in loadable_fields:
            setattr(obj, name, data.get(name))

    # The API assumes missing = None/null
    @ma.post_dump
    def remove_none_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value is not None
        }


class AutoSchema(msa.SQLAlchemyAutoSchema, Schema):
    """Auto-schema class"""


class SQLCursorPage(flask_smorest.Page):
    """SQL cursor pager"""

    @property
    def item_count(self):
        return self.collection.count()
