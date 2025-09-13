from flask import g

from mv_back.routes.bookmarks_routes import bookmarks as bookmarks_router
from mv_back.routes.series_routes import series as series_router
from mv_back.routes.media_routes import media as media_router
from mv_back.routes.tags_routes import tags as tags_router


def register_routes(app):
    app.register_blueprint(bookmarks_router)
    app.register_blueprint(series_router)
    app.register_blueprint(media_router)
    app.register_blueprint(tags_router)
    

def register_teardown(app):
    @app.teardown_appcontext
    def close_db(exception):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()