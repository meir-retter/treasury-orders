From within `treasury_orders/`, run:

```
./scripts/build.sh
```

to build the docker image.

Then,

```
./scripts/run.sh
```

to run it. Then open `http://0.0.0.0:8279/` in a browser. The app may take 10-15 seconds to load the first time -- refreshes should be fast.

Notes:
- The app uses sqlite to persist the user's orders. Sqlite is lightweight and suitable for a single user in an app like this, but if this was a production app hosted online and there were multiple users and this was hosted online, I'd
  1. use Postgres instead, and
  2. need an additional column for username, need auth, etc
- All the historical yield data is read from files every time. These files are stored in the repo along with the code. This is okay because their small size means it's very quick to read and doesn't take up much space
- I used GPT for
  1. speeding up bugfixing
  2. Plotly Dash aesthetic improvement (css styling, getting the components aligned etc)


I also asked GPT to suggest names for this app -- my favorite was "YieldStation".

- More exception handling, type hints, and tests could be added. Also the db logic could be separated out better. But I estimated that my time spent was past 6 hours, so those would have to be done as a follow-up.

Potential improvements:
- Show the current yield curve against other days' yield curves
- Show the projected value of the user's orders after they get their money back (factoring in payments and the yield rate)
- Make it load faster at the start
