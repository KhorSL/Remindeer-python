## Remindeer Bot
A minimalist telegram bot that sends scheduled notifications to the user.

___

Find the telegram bot at [@S_Remindeer_bot](https://t.me/S_Remindeer_bot "Remindeer").

## Setting up

### Installing `psycopg2` in `virtualenv`

Get path of `LDFLAGS`:

```console
$ pg_config --ldflag
-L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib -Wl,-dead_strip_dylibs
```

Then install `psycopg2`:

``` console
$ env LDFLAGS='-L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib -Wl,-dead_strip_dylibs' pip install psycopg2==2.8.3
```
