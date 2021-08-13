"""Users resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import User

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import UserSchema, UserQueryArgsSchema, BooleanValueSchema


blp = Blueprint(
    'User',
    __name__,
    url_prefix='/users',
    description="Operations on users"
)


@blp.route('/')
class UserViews(MethodView):

    @blp.login_required(role="admin")
    @blp.etag
    @blp.arguments(UserQueryArgsSchema, location='query')
    @blp.response(200, UserSchema(many=True))
    def get(self, args):
        """List users"""
        return db.session.query(User).filter_by(**args)

    @blp.login_required(role="admin")
    @blp.etag
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user"""
        password = new_item.pop("password")
        item = User.new(**new_item)
        item.set_password(password)
        item.is_admin = False
        item.is_active = True
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class UserByIdViews(MethodView):

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.response(200, UserSchema)
    def get(self, item_id):
        """Get user by ID"""
        item = db.session.get(User, item_id)
        if item is None:
            abort(404)
        if blp.current_user() and not item.can_read(blp.current_user()):
            abort(403)
        return item

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing user"""
        item = db.session.get(User, item_id)
        if item is None:
            abort(404)
        if blp.current_user() and not item.can_write(blp.current_user()):
            abort(403)
        password = new_item.pop("password")
        blp.check_etag(item, UserSchema)
        item.update(**new_item)
        item.set_password(password)
        db.session.commit()
        return item

    @blp.login_required(role="admin")
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a user"""
        item = db.session.get(User, item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, UserSchema)
        db.session.delete(item)
        db.session.commit()


@blp.route('/<int:item_id>/set_admin', methods=('PUT', ))
@blp.login_required(role="admin")
@blp.etag
@blp.arguments(BooleanValueSchema)
@blp.response(204)
def set_admin(args, item_id):
    item = db.session.get(User, item_id)
    if item is None:
        abort(404)
    blp.check_etag(item, UserSchema)
    item.is_admin = args["value"]
    db.session.commit()
    blp.set_etag(item, UserSchema)


@blp.route('/<int:item_id>/set_active', methods=('PUT', ))
@blp.login_required(role="admin")
@blp.etag
@blp.arguments(BooleanValueSchema)
@blp.response(204)
def set_active(args, item_id):
    item = db.session.get(User, item_id)
    if item is None:
        abort(404)
    blp.check_etag(item, UserSchema)
    item.is_active = args["value"]
    db.session.commit()
    blp.set_etag(item, UserSchema)
