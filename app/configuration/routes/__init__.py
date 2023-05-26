from app.configuration.routes.routes import *
from app.internal.routes import user, report, auth

__routes__ = Routes(routers=(user.router,
                             report.router,
                             auth.router))
