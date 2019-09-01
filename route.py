"""Main module, this is where the applications routes are specified."""
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import utils.wordlists as wordlists

define("port", default=4000, help="run on the given port", type=int)
define("develop", default=False, help="Run in develop environment", type=bool)


# Setup the Tornado Application
tornado_settings = {"debug": False}


class Application(tornado.web.Application):
    """The main application."""

    def __init__(self, settings):
        """Set up routes."""
        self.declared_handlers = [
            (r"/", wordlists.Info),
            (r"/search", wordlists.SearchHandler),
            (r"/subtypes", wordlists.SubtypeHandler),
            (r"/modes", wordlists.ModeHandler),
            (r"/publish/(.*)", wordlists.PublishHandler),
            (r"/unpublish/(.*)", wordlists.UnpublishHandler),
            (r"/css", wordlists.CSSHandler),
        ]

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, self.declared_handlers, **settings)


if __name__ == '__main__':
    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()

    if options.develop:
        tornado_settings['debug'] = True
        tornado_settings['develop'] = True
        logging.getLogger().setLevel(logging.DEBUG)

    # Instantiate Application
    application = Application(tornado_settings)
    application.listen(options.port)
    print('Running on port', options.port)

    # Start HTTP Server
    http_server = tornado.httpserver.HTTPServer(application)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
