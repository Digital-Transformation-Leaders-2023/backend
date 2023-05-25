from app.configuration.routes.routes import *
from app.internal.routes import user, utils, report, auth

__routes__ = Routes(routers=(user.router,
                             utils.router,
                             report.router,
                             auth.router))
