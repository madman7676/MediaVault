from flask import g

from mv_back.routes.bookmarks_routes import bookmarks as bookmarks_router
from mv_back.routes.media_routes import media as media_router
from mv_back.routes.movies_routes import movies as movies_router
from mv_back.routes.series_routes import series as series_router
from mv_back.routes.tags_routes import tags as tags_router
from mv_back.routes.thumbnails_routes import thumbnails as thumbnails_router
from mv_back.routes.video_routes import video as video_router
from mv_back.routes.select_folder_routes import select_folder as select_folder_router
from mv_back.routes.test_routes import test as test_router

from mv_back.routes.metadata_old_routes import metadata as metadata_router


def register_routes(app):
    app.register_blueprint(bookmarks_router)
    app.register_blueprint(series_router)
    app.register_blueprint(movies_router)
    app.register_blueprint(media_router)
    app.register_blueprint(tags_router)
    app.register_blueprint(thumbnails_router)
    app.register_blueprint(video_router)
    app.register_blueprint(select_folder_router)
    app.register_blueprint(test_router)
    
    app.register_blueprint(metadata_router)
    

def register_teardown(app):
    @app.teardown_appcontext
    def close_db(exception):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()