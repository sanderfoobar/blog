Title: SubZerod
Author: Sander
Date: 2021-10-23 01:29
Slug: python-subzerod-domain-enumeration-security
Category: project
Tags: python, quart
Summary: subdomain enumeration tool

# SubZerod

SubZerod is a python3 asyncio console application designed to enumerate sub-domains of websites using OSINT. It helps penetration testers
and bug hunters collect and gather sub-domains for the domain they are targeting.

SubZerod enumerates sub-domains using search engines such as Yahoo, DuckDuckGo, Baidu, etc.

## Usage

Discovering subdomains given a domain.

```bash
subzerod lobste.rs
```

output:

```text
lobste.rs
l.lobste.rs
www.lobste.rs
```

Discover domain(s) on an IPv4

```bash
subzerod 135.125.235.26
```

output:

```text
sanderf.nl
photos.sanderf.nl
```

### As a webservice

```
subzerod web
```

`http://127.0.0.1:9342/scan/135.125.235.26`

Responses are returned in JSON.

### Programmatically

```python
from subzerod import SubZerod

subdomains = await SubZerod.find_subdomains("lobste.rs")
domains = await SubZerod.find_domains("135.125.235.26")
```

## Installation

```
pip install subzerod
```

## Legacy

SubZerod is a fork of [Sublist3r](https://github.com/aboul3la/Sublist3r) with some improvements:

- modern python 3
- asyncio instead of threading
- scans are considerably faster
- comes with a webserver because why not
