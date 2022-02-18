Title: clean cURL commands
Author: Sander
Date: 2022-1-13 01:29
Slug: clean-curl-commands-with-python-script
Category: project
Tags: python
Summary: Copying unnecessarily verbose cURL commands

# cURL

Often times you'll use Firefox's devtools to turn a network request into a `curl` command:

![](../downloads/devtool_curl.png)

Which will result in the following being inserted into the clipboard:

```bash
curl 'http://natas11.natas.labs.overthewire.org/' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate' -H 'DNT: 1' -H 'Authorization: Basic bmFOEMxiETpVODJxeiOIEegmOXh1Rm9JM2RZWDYxczdPWkQ5SktvSw==' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache'
```

Depending on what you're doing, this is often unnecessarily verbose. During CTF games, or wargaming, you'll probably only need:

1. The URL
2. Cookies and/or Authorization header
3. POST payload (if present)

So I made a small tool that cleans the command up a bit. The result will be:

```bash
curl -vvk -H 'Authorization: Basic bmFOEMxiETpVODJxeiOIEegmOXh1Rm9JM2RZWDYxczdPWkQ5SktvSw==' 'http://natas11.natas.labs.overthewire.org/'
```

## Running it

The following hacky program may be placed in `/usr/bin/cleancurl`

```python3
#!/usr/bin/python3
# sander@sanderf.nl
# sudo apt install -y xsel
import re
import sys
from subprocess import Popen, PIPE, DEVNULL, STDOUT

r = R"( \-\w \'(.+?)\')"

print(f"Cleans a cURL command. Enter command below")
inp = input().replace("\n", ""),replace("\\\n","").strip()
if not inp.startswith("curl "):
    sys.stderr.write("input must start with 'curl '\n")
    sys.exit()
inp = inp[5:]

cmd = ["curl", "-vvk"]
for kv in re.findall(r, inp):
    val = kv[0]
    inp = inp.replace(val, "")
    for needle in ["authorization:", "cookie:", " -d ", " -b ", " -X"]:
        if needle in val:
            cmd.append(val.strip()) 
cmd.append(inp)

result = " ".join(cmd)

p = Popen(['xsel', '-b'], stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)
p.communicate(input=result.encode())

sys.stderr.write("\nCopied cleaned cURL command to clipboard\n")
```

Usage is just running the program without arguments.

## Requirements

`sudo apt install -y xsel`

## Closing note

What is also handy is automatically converting cURL commands to Python, PHP, NodeJS code using the following website: [curlconverter.com](https://curlconverter.com/)
