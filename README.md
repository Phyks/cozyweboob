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

Then, typical command-line usage is:
```bash
cat konnectors.json | ./cozyweboob.py
```


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


## Output JSON file

The resulting JSON file, on `stdout` is a map associating the `id` fields as
provided in input JSON file to a map of fetched data by this module.

Each module map has a `cookies` entry containing the cookies used to fetch the
data, so that any program running afterwards can download documents.

The other entries in these maps depend on the module capabilities as defined
by Weboob.


## License

The content of this repository is licensed under an MIT license, unless
explicitly mentionned otherwise.
