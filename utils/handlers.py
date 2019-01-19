""" Request handlers are defined here """
import json
import logging
import os
import os.path
import tornado.web
import urllib.request

import conf.settings as settings
import utils.errors as errors


class BaseHandler(tornado.web.RequestHandler):
    """ Base Handler. """

    def prepare(self):
        """ Set up file system """
        try:
            for mode in settings.get_modes():
                if mode == 'default':
                    continue
                typefile = settings.get('subtypes', mode)
                directory = os.path.dirname(typefile)
                # TODO this only works for paths like a/b.txt, not b.txt och a/b/c.txt
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                if not os.path.isfile(typefile):
                    open(typefile, 'w').write('')
        except errors.ConfigurationError as error:
            self.return_error(error)


    def options(self, *args, **kwargs):
        """ Option call: do nothing """
        self.set_status(204)
        self.finish()

    def set_default_headers(self):
        """ Set headers, alllowing cors """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,content-type,authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def return_error(self, error):
        """ Return an error and finish the call """
        self.set_status(error.code)
        self.set_header('Content-Type', 'text/plain')
        self.write({"error": error.message})
        self.finish()


class SafeHandler(BaseHandler):
    """ Handlers where authentication can be added """

    def authenticate(self, mode):
        """ Authenticate to Karp. """
        try:
            auth_header = self.request.headers.get('Authorization')
            basic = auth_header[6:]
            url = settings.karp + '/checkuser'
            req = urllib.request.Request(url)
            req.add_header('Authorization', 'Basic %s' % basic)
            response = json.loads(urllib.request.urlopen(req).read().decode('utf8'))
            ok = response["authenticated"]
        except:
            ok = False
        if not ok:
            logging.debug('Bad username or password?')
            error = errors.AuthenticationError("Bad username or password?")
            self.return_error(error)
            raise error
        else:
            resources = response.get("permitted_resources", {}).get("lexica", {})
            lexok = settings.get('resource', mode) in resources
            if not lexok:
                logging.debug('Cannot edit resource %s', resources)
                error = errors.AuthenticationError("You are not allowed to edit the resource")
                self.return_error(error)


    def options(self, *args, **kwargs):
        """ Options call: do nothing """
        self.set_status(204)
        self.finish()
