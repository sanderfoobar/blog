Title: A few Greasemonkey scripts
Author: Sander
Date: 2022-1-12 08:32
Slug: improve-internet-browsing-experience-with-greasemonkey
Category: project
Tags: python
Summary: to clean up the internet

# Greasemonkey

I like websites that look simple, do not include a ton of javascript, and generally is easy on the eyes. As such I use a couple of Firefox Greasemonkey plugins to make part of the internet look like the mid 2000s.

For example:

- Instead of Twitter we can use a [Nitter](https://github.com/zedeus/nitter) instance
- Instead of Reddit we can use a [Teddit](https://codeberg.org/teddit/teddit) instance
- Instead of YouTube we can use an [Invidious](https://github.com/iv-org/invidious) instance

## Twitter

Redirect any twitter link to nitter instance.

```javascript
// ==UserScript==
// @name         twitter to nitter
// @namespace    https://gist.github.com/bitraid/d1901de54382532a03b9b22a207f0417
// @version      1.0
// @description  twitter to nitter
// @match        *://twitter.com/*
// @match        *://mobile.twitter.com/*
// @run-at       document-start
// ==/UserScript==

(function () {
	'use strict';
	top.location.hostname = "nitter.sanderf.nl";
})();
```

## Reddit

Redirect any Reddit link to a Teddit instance.

```javascript
// ==UserScript==
// @name         reddit to teddit
// @namespace    https://gist.github.com/bitraid/d1901de54382532a03b9b22a207f0417
// @version      1.0
// @description  reddit to teddit
// @match        *://*.reddit.com/*
// @match        *://reddit.com/*
// @run-at       document-start
// ==/UserScript==

(function () {
	'use strict';
	top.location.hostname = "teddit.sanderf.nl";
})();
```

## YouTube

Redirect any youtube link to an invidious instance.

```javascript
// ==UserScript==
// @name         youtube to invidious
// @version      1.0
// @description  youtube to invidious
// @match        *://*.youtube.com/watch?v=*
// @match        *://youtube.com/watch?v=*
// @run-at       document-start
// ==/UserScript==

(function () {
	'use strict';
	top.location.hostname = "invidious.namazso.eu";
})();
```

## NPO player fix

Now this one is for Dutch people. As you may know the website [npostart.nl](https://npostart.nl) really sucks, especially the video player. The following greasemonkey script will fix some of its shortcomings.

```javascript
// ==UserScript==
// @name         Fix NPO player
// @version      1.0
// @description  Make NPO player useable. Removes player header(s) and the 50% transparent overlay on mouse move.
// @match        *://www.npostart.nl/*
// @match        *://start-player.npo.nl/*
// @run-at       document-start
// ==/UserScript==
// sander@sanderf.nl 2022

var fix_css = `
.npo-player-header, #playerHeader {
	display: none !important
}
.video-js:before {
  background: transparent !important;
}`;
var ref = document.referrer;
var player = "start-player.npo.nl";
var max_tries = 30;
var tries = 0;

function get_iframe_src_attr() {
  let frame = document.getElementsByTagName("iframe");
  if(frame.length <= 0) return "";
  return frame[0].src;
}

function tryRedirect() {
  // wait for iframe to spawn
  setTimeout(() => {
    tries += 1;
    if(tries >= max_tries) {console.log('iframe never appeared'); return;}
    
    src = get_iframe_src_attr();
		if(!src) { return tryRedirect(); }
    
    window.location.href = src;
  }, 50);
}

(function () {
	'use strict';

  if(top.location.hostname.indexOf(player) >= 0) {
    setTimeout(() => {
      var el = document.head.appendChild(document.createElement("style"));
      el.innerHTML = fix_css; }, 500);
  } else {
    tryRedirect();
  }
})();
```

Enjoy your new-found zen browsing experience.
