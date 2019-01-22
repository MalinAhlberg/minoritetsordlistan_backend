# Installation
**Download**

`git clone git@github.com:MalinAhlberg/minoritetsordlistan_backend.git`


**Prepare:**

 - `cp conf/settings_default.json conf/settings.json`
 - Open and update this file, in most cases you will only need to update the `username` and `password`.

Public subtypes are set in `data/{fin,yid}-subtypes.txt`.

**Run:**

```
 docker-compose build
 docker-compose up -d
```


Runs on port 4000.


**Examples:**

- `curl 'http://localhost:4000/subtypes'`

- `curl 'http://localhost:4000/publish/muminfigurer?mode=term-swefin'`

- `curl 'http://localhost:4000/search?q=o&subtype=muminfigurer&mode=term-swefin' -i`
