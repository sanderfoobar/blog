Title: Brain Games
Author: spotless
Date: 2019-11-30 22:08
Slug: tuctf-2019-brain games
Category: CTF
Cat: misc
Tags: telnet
Summary: CTF challenge "Brain Games"

> Time to go back to the basics... you remember those, right?

`nc chal.tuctf.com 30301`

## Recon

A questionaire over a tcp session. I suppose we get the flag when we correctly answer all questions.

![zz](https://i.imgur.com/P3MmMwR.png)


## Solution

After struggling to correctly interpret ncruses, color codes etc, I decided to
OCR a terminal window, which is ~~batshit insane~~ hilarious, and worked.

The steps involved:

1. Programmatically spawn a terminal window `qterminal`
2. grab `window_id`
    - Using `wmctrl -l | grep "N\/A" | grep "~" | awk '{print $1}'`
4. Send keystrokes to window for `nc chal.tuctf.com 30301`
    - Using `xdotool type --window $WINDOW_ID "$(printf \'$CMD\r\n\')`
5. Enter a category
6. Take screenshot of terminal window
    - Using `import -screen -window %s /tmp/hax.png`
8. Crop the relevant text from picture
    - Using Python, `Pillow`
9. Parse text with OCR (tesseract)
    - Using Python, `pytesseract`
10. Answer the questions, be presented the flag when finished.

### Flag

Hacky code ahead :-)

```python
import os
import re
from time import sleep
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

from PIL import Image


def ocr(filename):
    text = pytesseract.image_to_string(
        Image.open(filename),
        config="_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return text

os.popen("killall -9 qterminal").read()
os.popen("nohup qterminal &")
sleep(1)
window_id = os.popen(
    """wmctrl -l | grep "N\/A" | grep "~" | awk '{print $1}'""").read().strip()


def sendCmd(inp):
    global window_id
    os.popen('xdotool type --window %s "$(printf \'%s\r\n\')"' % (window_id, inp))
    sleep(0.4)


sendCmd("nc chal.tuctf.com 30301")
sleep(0.6)

def cat1():
    data = ocr('/tmp/hax2.png')
    data = re.sub('\n+', ' ', data)

    if 'Brain Games' in data:
        raise IndentationError()

    data2 = ocr('/tmp/hax3.png')
    data2 = re.sub('\n+', ' ', data2)

    _re = r'(\w+) \((\w+)\) in (\w)'
    if re.match(_re, data):
        val, _from, _to = re.findall(_re, data)[0]
        _from = _from[0]
    else:
        val, _from = re.findall(r'(\w+) \((\w+)\)', data)[0]

        if 'tal?' in data:
            _to = 'O'
        elif 'in h' in data.lower():
            _to = 'H'
        elif 'in d' in data.lower():
            _to = 'D'
        elif 'in b' in data.lower():
            _to = 'B'
        elif 'in o' in data.lower() or 'in 0' in data.lower():
            _to = 'O'
        else:
            if 'ctal' in data2.lower():
                _to = 'O'
            elif 'ecimal' in data2.lower():
                _to = 'D'
            else:
                raise Exception('wut')

        _from = _from[0]
        print("%s, %s %s" % (val, _from, _to))

    # normalize to int
    if _from == 'O':
        val = int(val, 8)
    elif _from == 'H':
        val = val.replace('l', '1')
        val = val.replace('O', '0')
        val = val.replace('Q', '0')
        val = int(val, 16)
    elif _from == 'B':
        val = int(val, 2)
    elif _from == 'D':
        val = int(val)
    else:
        raise Exception(";(")

    print("val", val)

    if _to == 'D':
        answer = str(val)
    elif _to == 'H':
        answer = hex(val)
    elif _to == 'O':
        answer = oct(val).replace('o', '')
    elif _to == 'B':
        answer = bin(val)[2:]
    else:
        raise Exception('wow')

    print(answer)
    sendCmd(answer)


sendCmd("1")
while True:
    os.popen("""
        import -screen -window %s /tmp/hax.png""" % window_id).read()

    img = Image.open("/tmp/hax.png")
    size = img.size
    area = (556, 162, 960, 190)
    img = img.crop(area)
    img.save("/tmp/hax2.png")

    img = Image.open("/tmp/hax.png")
    area = (446, 184, 650, 211)
    img = img.crop(area)
    img.save("/tmp/hax3.png")

    try:
        cat1()
    except IndentationError:
        break


sendCmd("3")
for answer in ["Morris Worm", "Melissa Virus", "CIH Virus", "ILOVEYOU Worm", "Blaster Worm", "Sasser Worm", "Stuxnet", "CryptoLocker", "Mirai", "WannaCry", "Forkbomb", "Cascade", "Slammer Worm", "Conficker", "Techno", "BonziBUDDY", "Solar Sunrise", "Navashield", "Creeper", "Reaper"]:
    sendCmd(answer)


def cat2():
    data = ocr('/tmp/hax2.png')
    data = re.sub('\n+', ' ', data)

    if 'Brain Games' in data:
        raise IndentationError()

    data2 = ocr('/tmp/hax3.png')
    data2 = re.sub('\n+', ' ', data2)

    _from, _op, _to = re.findall(r'(\d+) (\w+) (\d+)', data)[0]

    if _op == 'XOR':
        answer = str(int(_from) ^ int(_to))
    elif _op == 'AND':
        answer = (str(int(_from) & int(_to)))
    elif _op == 'OR':
        answer = (str(int(_from) | int(_to)))
    else:
        raise NotImplementedError()
    sendCmd(answer)


sendCmd("2")
while True:
    os.popen("""
        import -screen -window %s /tmp/hax.png""" % window_id).read()

    img = Image.open("/tmp/hax.png")
    size = img.size
    area = (556, 162, 960, 190)
    img = img.crop(area)
    img.save("/tmp/hax2.png")

    img = Image.open("/tmp/hax.png")
    area = (446, 184, 650, 211)
    img = img.crop(area)
    img.save("/tmp/hax3.png")

    try:
        cat2()
    except IndentationError:
        break

```

`TUCTF{7H3_M0R3_Y0U_KN0W_G1F}`
