# coding:utf-8
""" Convert lexicon entries from json to html """
import logging
import re
import xml.etree.ElementTree as etree


def format_posts(ans, mode, toformat='html', css=''):
    " Helper for formatting a search result "
    logging.debug('will format')
    hits = ans.get('hits', {}).get('hits', [])
    func = mode_conv.get(mode, default)
    ok, tab = func([hit['_source'] for hit in hits], css=css)
    return tab


def termswefin(objs, css=''):
    """ Converts a list of term-swefin objects to HTML.
        The HTML header and the CSS template are written by
        Eva Lindström (evali@ling.su) and
        Gunnar Eriksson (gunnar.eriksson@sprakochfolkminnen.se)
        at Språkrådet, May 2018.
    """
    # '<!DOCTYPE html>' is added after parsing, to avoid parser confusion
    # Make sure all tags are properly closed, to avoid xml parser confusion
    if not css:
        css = "https://liljeholmen.sprakochfolkminnen.se/KARPexport_Fi-ordlista_HTML.css"
    header = """
    <html lang="sv">
       <head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="stylesheet" type="text/css" href="{css}"/>
	<link rel="icon" href=" http://liljeholmen.sprakochfolkminnen.se/favicon1.jpg" type="image/gif"/>
	<title>Sverigefinska ordlistor från Språkrådet</title>
	<meta name="description" content="Sverigefinska ordlistor från Språkrådet"/>
	<meta name="keywords" content="sverigefinska, lexikon, svenska, finska, finska i Sverige, öppna data, Språkrådet, ISOF"/>
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
       </head>
    </html>
    """.format(css=css)
    header = re.sub('[\n\t]', '', header)
    doc = etree.fromstring(header.encode('utf8'))
    body = etree.SubElement(doc, 'body')
    # Don't use title
    # title = etree.SubElement(body, 'div', {"class": "title clearfix"})
    # titles = set()
    if objs:
        logging.debug('will format, start with %s', objs[0])
    main = etree.SubElement(body, 'div', {"class": "main"})
    for obj in objs:
        # make one html entry for every subtype (sakområde)
        for subtype in obj.get('subtype', ["-"]):
            #titles.add(subtype.title())
            uppslag = etree.SubElement(main, 'div', {"class": "uppslag"})
            p = etree.SubElement(uppslag, 'p', {"class": "lex"})
            lexem = etree.SubElement(p, 'span', {"class": "lexem"})
            lexem.text = escape(obj['baselang'].get('form')[0].get('wordform'))
            trans = etree.SubElement(p, 'span', {"class": "comm-sv"})
            trans.text = escape(obj['baselang'].get('form')[0].get('comment', ''))
            # TODO ';' (separating forms/comments) not implemented
            for target in obj.get('targetlang'):
                num_tform = len(target.get('form', []))
                for ix, tform in enumerate(target.get('form', [])):
                    comm = escape(tform.get('comment', ''), tail=False)
                    form = escape(tform.get('wordform', ''), tail=comm)
                    trans = etree.SubElement(p, 'span', {"class": "fi_trans", "lang": "fi"})
                    trans.text = form
                    last = trans
                    if comm:
                        transcomm = etree.SubElement(p, 'span', {"class": "comm"})
                        transcomm.text = comm
                        last = transcomm
                    # find out whether a comma should be appended
                    if ix < num_tform-1:
                        last.tail = ', '
                    else:
                        last.tail = ' '

            # create html for "sammansättningar"
            subupp = etree.SubElement(uppslag, 'div', {"class": "uppslag_sub"})
            for i, ex in enumerate(obj.get('baselang').get('compound', [])):
                lex_sub = etree.SubElement(subupp, 'p', {"class": "lex_sub"})
                dash = etree.SubElement(lex_sub, 'span', {"class": "dash"})
                dash.text = u'– '  # other dash version: u'— '
                lexem_sub = etree.SubElement(lex_sub, 'span', {"class": "lexem_sub"})
                # TODO future, when field structure is improved
                # comm = escape(ex.get('comment', ''), tail=False)
                # form = escape(ex.get('form', ''), tail=comm)
                lexem_sub.text = escape(ex)
                try:
                    target = escape(obj.get('targetlang', [{}])[0].get('compound')[i])
                    # Put tags around span with 'comm' class around "(ark.)"
                    if '(ark.)' in target:
                        target = re.sub(r'(\(ark\.\))', r'<span class="comm">\1</span>', target)

                    # TODO future, when field structure is improved
                    # targetcomm = escape(target.get('comment', ''), tail=False)
                    # targetform = escape(target.get('form', ''), tail=comm)
                except IndexError:
                    # The json format does not guarantee that there are enough
                    # subemma translations. Just leave the field blank, in that case.
                    target = ''
                if target:
                    # Cannot use proper etree handling here, since we manually
                    # insert tags around (ark.).
                    target = u'<span class="fi_trans_sub" lang="fi">' + target + u'</span>'
                    lex_sub.append(etree.fromstring(target.encode('utf8')))

    # etree.SubElement(title, 'h1').text = ', '.join(titles)
    root = etree.tostring(doc, method="html", encoding='unicode')
    logging.debug(root)
    logging.debug(type(root))
    root = '<!DOCTYPE html>\n' + root
    return len(objs), root #.encode('utf8')


def escape(string, tail=True):
    " Help format strings "
    tail = ' ' if tail else ''
    return string.strip() + tail


def default(obj, toformat):
    " Default translation to html (do nothing) "
    return 0, "no translation available"


mode_conv = {"term-swefin": termswefin,
             # In the future, yiddish will probably need it's on convertion.
             # For now, use swef-fin.
             "term-sweyid": termswefin,
            }
