""" Module for creating queries to Karp and keeping track of published subtypes """
import base64
import json
import logging
import urllib.request
import urllib.parse

import conf.settings as settings
import utils.errors as errors
import utils.handlers as handlers
import utils.convert as convert


class Info(handlers.BaseHandler):
    """ Return general information """
    # TODO add example calls here!
    def get(self):
        info = ['Minoritetsordlistans API.']

        self.write({
            'info': ' '.join(info)
        })


class CSSHandler(handlers.BaseHandler):
    """ Proxy for css files """
    def get(self, *args):
        mode = self.get_query_argument('mode', settings.get('mode'))
        full_url = settings.get('css', mode)
        req = urllib.request.Request(full_url)
        self.set_header('Content-Type', 'text/css')
        self.write(urllib.request.urlopen(req).read())


class PublishHandler(handlers.SafeHandler):
    """ Publish a subtype """

    def get(self, *args):
        mode = self.get_query_argument('mode', settings.get('mode'))
        self.authenticate(mode)
        subtype = args[0]
        existing = set(get_subtypes(mode))
        if subtype not in existing:
            existing.add(subtype)
            update_subtypes(existing, mode)
        subtypes = get_subtypes(mode)
        self.write({'subtype': subtype, 'publish': True, 'subtypes': subtypes})


class UnpublishHandler(handlers.SafeHandler):
    """ Unpublish a subtype """

    def get(self, *args):
        mode = self.get_query_argument('mode', settings.get('mode'))
        self.authenticate(mode)
        subtype = args[0]
        existing = set(get_subtypes(mode))
        if subtype in existing:
            existing.remove(subtype)
            update_subtypes(existing, mode)
        subtypes = get_subtypes(mode)
        self.write({'subtype': subtype, 'publish': False, 'subtypes': subtypes})


class SubtypeHandler(handlers.BaseHandler):
    """ Return subtype information """
    def get(self):
        unpublished = self.get_query_argument('unpublished', False)
        mode = self.get_query_argument('mode', settings.get('mode'))
        try:
            subtypes = get_subtypes(mode)
        except errors.ConfigurationError:
            logging.debug('asked for subtypes of unpublished mode')
            subtypes = []
        logging.debug(' * Subtypes %s' % subtypes)
        if unpublished in [True, "true", "True"]:
            all_subtypes = get_karp_subtypes(mode)
            unpub_subtypes = list(all_subtypes.difference(subtypes))
            self.write({'published': subtypes, 'unpublished': unpub_subtypes})
        else:
            self.write({'subtypes': subtypes})


class ModeHandler(handlers.BaseHandler):
    """ Return mode information """
    def get(self):
        modes = settings.get_modes()
        self.write({'modes': list(modes)})


class SearchHandler(handlers.BaseHandler):
    """ Return general information """

    def get(self):
        answer = []
        logging.debug(' * Searching!')
        mode = self.get_query_argument('mode', settings.get('mode'))
        if not mode in settings.get_modes():
            message = "Unknown mode: {}. Available: {}".format(mode, ', '.join(settings.get_modes()))
            error = errors.ConfigurationError(message, code=400)
            self.return_error(error)
            return

        toformat = self.get_query_argument('format', False)
        inp_subtypes = self.get_query_argument('subtypes', [])
        if inp_subtypes:
            inp_subtypes = inp_subtypes.split(',')
        logging.debug('inp_subtypes %s', inp_subtypes)
        word = self.get_query_argument('q', '')
        contains = self.get_query_argument('contains', '') in [True, 'true', 'True']
        logging.debug('word %s', word)
        lang = self.get_query_argument('lang', 'sv')
        if lang not in settings.get('languages', mode):
            message = "Unknown language: {}. Available: {}".format(lang, ', '.join(settings.get('languages', mode)))
            error = errors.QueryError(message)
            self.return_error(error)
            return

        if toformat in ['html', 'pdf']:
            size = int(settings.get('maxsize_export', mode))
        else:
            size = int(self.get_query_argument('size', settings.get('maxsize', mode)))

        subtypes = filter_public_subtypes(inp_subtypes, mode)
        logging.debug(' * Subtypes %s', subtypes)
        if not subtypes:
            logging.warning(' * No public subtypes!')
            message = "Subtype(s) {} not public".format(', '.join(inp_subtypes))
            error = errors.QueryError(message)
            self.return_error(error)
            return

        url = settings.karp + '/query?%s'

        params = {'resource': settings.get('resource', mode),
                  'mode': settings.get('mode', mode),
                  'size': size}

        overflow = False
        if not word and toformat not in ['html', 'pdf']:
            word = limit_query(subtypes, lang, mode)
            if word:
                overflow = True

        params['q'] = build_query(word, subtypes, contains, lang, mode)
        if lang != settings.get('sourcelanguage', mode):
            params['sort'] = settings.get('targetsort', mode)

        data = make_call(url, params, mode)
        if toformat == 'html':
            if settings.get('myurl', mode):
                cssurl = settings.get('myurl', mode)
            else:
                cssurl = "{}://{}".format(self.request.protocol, self.request.host)
            cssurl += "/css?mode=" + mode
            html = convert.format_posts(data, settings.get('mode', mode), toformat='html', css=cssurl)
            self.write(html)
            return

        total = data.get('hits', {}).get('total', 0)
        hits = data.get('hits', {}).get('hits', [])
        for ans in hits:
            source = ans.get('_source', {})
            answer.append(source)

        logging.debug('overflow? %s > %s', total, size)
        self.write({'result': answer, 'overflow': overflow or total > size})


def make_call(url, params, mode):
    data = urllib.parse.urlencode(params)
    logging.debug('data %s', params)
    full_url = url % data
    logging.debug(str(full_url))
    req = urllib.request.Request(full_url)
    add_credentials(req, mode)

    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode())


def build_query(word, subtypes, contains, lang, mode):
    """ Construct the query string to Karp """
    wordfield = settings.get('baseform.search', mode)
    if lang != settings.get('sourcelanguage', mode):
        wordfield = settings.get('targetform.search', mode)

    if word and contains:
        word = word.lower()
        word_q = 'extended||and|{}|regexp|.*{}.*'.format(wordfield, word)
    elif word:
        word = word.lower()
        op = 'startswith'
        if contains:
            word = '.*{}.*'.format(word)
            op = 'regexp'
        word_q = 'extended||and|{}|{}|{}'.format(wordfield, op, word)
    else:
        word_q = 'extended||and|{}|regexp|.*'.format(wordfield)

    # TODO check status?  f'||and|termstatus.bucket|exists' #equals|{settings.ok_status}'
    if subtypes:
        subtype = '|'.join(subtypes)
        query = '{}||and|subtype.search|equals|{}'.format(word_q, subtype)
    else:
        query = word_q
    return query


def limit_query(subtypes, lang, mode):
    url = settings.karp + '/query?%s'
    params = {'resource': settings.get('resource', mode),
              'mode': settings.get('mode', mode),
              'size': 0}
    params['q'] = build_query('', subtypes, False, lang, mode)
    data = make_call(url, params, mode)
    if int(data['hits']['total']) > settings.get('overflowsize'):
        return settings.get_first_letter(lang, mode)
    return ''



def get_subtypes(mode):
    """ Read all subtypes for this mode from file """
    return [s.strip() for s in open(settings.get('subtypes', mode), encoding='utf-8').readlines() if s]


def update_subtypes(subtypes, mode):
    """ Update the subtypes file """
    open(settings.get('subtypes', mode), encoding='utf-8', mode='w').write('\n'.join(subtypes))


def get_karp_subtypes(mode):
    """ Ask Karp about all available subtypes """
    logging.debug(' * Searching!')
    url = settings.karp + '/statlist?%s'
    size = settings.get('overflowsize', 1000)
    params = {'resource': settings.get('resource', mode),
              'mode': settings.get('mode', mode),
              'size': size,
              'buckets': 'subtype'}
    params['q'] = build_query('', '', False, settings.get('sourcelanguage'), mode)
    data = urllib.parse.urlencode(params)
    logging.debug('data %s', params)
    full_url = url % data
    logging.debug(str(full_url))
    req = urllib.request.Request(full_url)
    add_credentials(req, mode)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode())
    res = set()
    for subtype in data['stat_table']:
        if subtype[0]:
            res.add(subtype[0])
    return res


def filter_public_subtypes(wanted, mode):
    """ Get the subtypes as specified by the user """
    existing_subtypes = set(get_subtypes(mode))
    if not wanted:
        return list(existing_subtypes)
    logging.debug(' * Intersection %s / %s', existing_subtypes, wanted)
    return list(existing_subtypes.intersection(set(wanted)))


def add_credentials(request, mode):
    """ Prepare a request by adding login credentials """
    credentials = ('%s:%s' % (settings.get('username', mode), settings.get('password', mode)))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))
    request.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
