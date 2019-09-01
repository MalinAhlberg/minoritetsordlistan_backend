# Adding a new wordlist

To add a new wordlist (a new language pair), all you have to do is to add
a configuration for the wordlist. The file to be modified is `conf/settings.json`.

A entry for a wordlist looks like this:

```json
  "term-swefin": {
    "resource": "term-swefin",
    "languages": ["sv", "fi"],
    "sourcelanguage": "sv",
    "targetsort": "targetform.sort",
    "baseform.search": "baseform.searchraw",
    "targetform.search": "targetform.searchraw",
    "mode": "term-swefin",
    "subtypes": "data/fin-subtypes.txt",
    "css": "http://liljeholmen.sprakochfolkminnen.se/KARPexport_Fi-ordlista_HTML.css"
  }
  ```

The name of the entry (`term-swefin`) is the internal name, used for the backend. **TODO** should this match something in the frontend?

All possible fields are described below. Most fields have default values (listed in grey), which will be used if the field is left out from the configuration.

- `resource`: the name of the resource, must be the same as in Karp.
- `languages`: the language codes of the resource. Must match the values given in the frontend. Not used in communication with Karp. One of them must match `sourcelanguage` (see below). `["sv", "fi"]`
- `sourcelanguage`: the default source language (as given in the frontend) `"sv"`
- `targetsort`: the name of the field, as given in Karp, to sort the target language by. `"targetform.sort"`
- `baseform.search`: the name of the field, as given in Karp, to search for baseforms of the source language.
- `targetform.search`: the name of the field, as given in Karp, to search for baseforms of the target language.
- `mode`: the Karp mode in which the wordlist lives `term-swefin`
- `subtypes`: a file (to be created) where all subtypes that are available in the backend are listed.
- `css`: an url to a css to use when creating html pages of word lists. `"http://liljeholmen.sprakochfolkminnen.se/KARPexport_Fi-ordlista_HTML.css"`
- `username`: Karp user name `user`
- `password`: Karp password `psw`
- `maxsize`: maximum number of entries to list in the reply of a query `500`
- `maxsize_export`: maximum number of entries to list when doing an export (for example, when creating html pages) `50000`
- `overflowsize`: For avoiding getting to big responses from Karp. If
  the number of entries matching a query exceeds this limit, only ask Karp for
  the words starting with 'a' (or a given symbol, see below). `1000`
- `standard_first_letter`: the first letter of the alphabet of the source languge. Used with `overflowsize`. `"a"`
- `myurl`: the base url of the application `""`

