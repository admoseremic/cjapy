# Adobe Customer Journey API

-----------------------

This is a python wrapper for the Adobe Customer Journey API.\
One important element when starting with CJA API is that you need to have your adobe console.io Project containing access to AEP **and** CJA.\
You cannot use the API without having access to both elements.

## Documentation

[Getting Started details on Github](./docs/getting_started.md).

## Versions

A documentation about the releases information can be found here : [cjapy releases](./docs/releases.md)

## Functionalities

Functionalities that are covered :

* Get Dimensions & Metrics
* Get, Update and Delete Tags & Shares
* Get, Update and Delete Dataview
* Get, Update and Delete Filters
* Get Top items for a dimension
* Run a report

documentation on reporting [here](./docs/main.md)

## Getting Started

To install the library with PIP use:

```cli
pip install cjapy
```

or, to get the latest version from github

```cli
python -m pip install --upgrade git+<https://github.com/pitchmuc/cjapy.git#egg=cjapy>
```

## Dependencies

In order to use this API in python, you would need to have those libraries installed :

* pandas
* requests
* json
* PyJWT
* PyJWT[crypto]
* pathlib
* pytest

## Test

TBW

## Others Sources

You can find information about the CJA API here :

* [https://www.adobe.io/cja-apis/docs/api/]
* [https://www.adobe.io/cja-apis/docs/use-cases/]

[1]: https://www.datanalyst.info