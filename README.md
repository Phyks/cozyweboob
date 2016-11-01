CozyWeboob
==========

This is an attempt at using [Weboob](http://weboob.org/) as a
[Cozy](http://cozy.io/) [Konnector](https://github.com/cozy-labs/konnectors).
It wraps around Weboob, receiving a JSON description of the modules to fetch
on `stdin` and returning a JSON of the fetched results on `stdout`.

Although the primary goal is to wrap around Weboob to use it in Cozy, this
script might be of interest for anyone willing to wrap around Weboob and
communicate with JSON pipes.


## Usage

First, you need to have Weboob installed on your system.

## Cozyweboob script

Typical command-line usage for this script is:
```bash
cat konnectors.json | python -m cozyweboob.__main__
```
where `konnectors.json` is a valid JSON file defining konnectors to be used.


## Server script

Typical command-line usage for this script is:
```bash
./server.py
```
This script spawns a Bottle webserver, listening on `localhost:8080` (by
default).

It exposes a couple of routes:

* the `/fetch` route, which supports `POST` method to send a valid JSON string
  defining konnectors to be used as the request body. Typical example to send
  it some content is:

  ```bash
  curl -X POST --data "$(cat konnectors.json)" "http://localhost:8080/"
  ```
  where `konnectors.json` is a valid JSON file defining konnectors to be used.
  Downloaded files will be stored in a temporary directory, and their file URI
  will be passed back in the output JSON. If you do not have a direct access
  to the filesystem, you can use the `/retrieve` endpoint below to retrieve
  such downloaded files through the network.

* the `/list` route, which will provide you a JSON dump of all the available
  modules, their descriptions and the configuration options you should provide
  them.

* the `/retrieve` route, which supports `POST` method and a single `path` `POST`
  parameter which is the path to the previously downloaded file to retrieve.
  Note that this route will not delete the temporary file whose content has
  been retrieved, and you should delete it manually.

* the `/clean` route, which will delete all temporary downloaded files. This
  route will return a JSON list of deleted folders.

**IMPORTANT:** Note this small webserver is **not** production ready and only
here as a proof of concept and to be used in a controlled development
environment. The `/retrieve` route will basically provide anyone to access any
file from your temp directory, which is a real security concern in production.

Note: You can specify the host and port to listen on using the
`COZYWEBOOB_HOST` and `COZYWEBOOB_PORT` environment variables.


## Conversation script

There is another command-line script available if you would rather communicate
with it in a conversation manner, using `stdin` and `stdout` (typically to
integrate it with Node modules using
[Python-shell](https://github.com/extrabacon/python-shell)). To run it, use:
```bash
./stdin_conversation.py
```

Then, you can write on `stdin` and fetch the responses from `stdout`.
Available commands are:
* `GET /list` to list all available modules.
* `POST /fetch JSON_PARAMS` where `JSON_PARAMS` is an input JSON for module
  parameters.
  Downloaded files will be stored in a temporary directory, and their file URI
  will be passed back in the output JSON.
* `GET /clean` to clean temporary downloaded files.
* `exit` to quit the script and end the conversation.

JSON responses are the same one as from the HTTP server script. It is
basically the same script without HTTP encapsulation.

_Note_: To simplify the script, note that it only supports single line
commands. Then, your `JSON_PARAMS` should be the same single `stdin` line as
the `GET /fetch` part.


## Notes concerning all the available scripts

Using `COZYWEBOOB_ENV=debug`, you can enable debug features for all of these
scripts, which might be useful for development. These features are:
* Logging
* If you pass a blank field in a JSON konnector description
(typically `password: ""`), the script will ask you its value at runtime,
using `getpass`.


## Input JSON file

The JSON file read on `stdin` should have a specific structure. A typical
example is given in `konnectors.json.sample`.

Basically, it consists of a list of maps. Each map corresponds to a given
Weboob module to run, with a given set of parameters (then allowing the script
to run multiple times the same module with different configurations). Each
map should have at the following three keys:
* `name` is the name of the Weboob module to run (same name as used in
  Weboob).
* `parameters` is a map of parameters to use for this particular module, as
  required by the associated Weboob backend.
* `id` should be a unique string of your choice, to uniquely identify this run
  of the specified module with the specified set of parameters.
* `actions` is an optional list of actions to perform. It should contains two
  keys, `fetch` and `download`. For each key, you can either pass `true` to
  completely handle the actions, or a map of capabilities associated to list
  of contents to fetch.
  Typically, you can pass `"fetch": { "CapDocument": ["bills"]}` to fetch only
  bills from the `CapDocuments` capability. You can also pass
  `"download": { "CapDocument": ["someID"] }` to download a specific document,
  identified by its ID.
  If not provided, the default is to fetch only, and do not download anything.


## Output JSON file

The resulting JSON file, on `stdout` is a map associating the `id` fields as
provided in input JSON file to a map of fetched data by this module.

Each module map has a `cookies` entry containing the cookies used to fetch the
data, so that any program running afterwards can download documents.

**Important** note: Most of such websites have very short lived sessions,
meaning in most cases these `cookies` will be useless for extra download as
the session will most likely be destroyed on the server side.

The other entries in these maps depend on the module capabilities as defined
by Weboob. Detailed informations about these other entires can be found in the
`doc/capabilities` folder.


## Contributing

All contributions are welcome. Feel free to make a PR :)

Python code is currently Python 2, but should be Python 3 compatible as Weboob
is moving towards Python 3. All Python code should be PEP8 compliant. I use
some extra rules, taken from PyLint.


## License

The content of this repository is licensed under an MIT license, unless
explicitly mentionned otherwise.


## Credits

* [Cozy](http://cozy.io/) and the cozy guys on #cozycloud @ freenode
* [Weboob](http://weboob.org/) and the weboob guys on #weboob @ freenode
* [Kresus](https://github.com/bnjbvr/kresus/) for giving the original idea and
  base code.
