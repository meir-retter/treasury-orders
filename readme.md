From within `treasury_orders/`, run:

```
./scripts/build.sh
```

to build the docker image.

Then,

```
./scripts/run.sh
```

to run it.

Notes:
- The app uses sqlite to persist the user's orders. Sqlite is lightweight and suitable for a single user in an app like this, but if this was a production app hosted online and there were multiple users and this was hosted online, I'd
  1. use Postgres instead, and
  2. need an additional column for username, need auth, etc
- All the historical yield data is read from files every time. This is okay because their small size means it's very quick, but with larger amounts of data it wouldn't be good


Potential improvements:
- Could be nice to show the current yield curve against other days' yield curves
