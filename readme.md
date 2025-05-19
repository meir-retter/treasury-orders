First `cd` into `treasury-orders/`. Then run:

```
./scripts/build.sh
```

to build the docker image.

Then,

```
./scripts/run.sh
```

to run it.

Open `http://0.0.0.0:8279/` in a browser. The app may take 10-15 seconds to load the first time because of docker -- refreshes should be fast.

Notes:
- The app uses sqlite to persist the user's orders. Sqlite is lightweight and suitable for a single user in an app like this, but if this was a production app hosted online and there were multiple users, it would be best to use something like Postgres instead. Also, usernames would need to be tracked per order, and authentication / a login system would be needed, etc.
- All the historical yield data is read from files every time. These files are stored in the repo along with the code. This is okay because their small size means it's very quick to read and doesn't take up much space
- I used GPT for
  1. speeding up bugfixing
  2. Plotly Dash aesthetic improvement (css styling, getting the components aligned etc)
  3. Suggesting a potential name for this app -- my favorite was "YieldStation".

Potential improvements:
- Add an auto-incrementing id column to the db table. Timestamp with per-second-granularity is not actually a good way to identify and sort the rows (there could be two orders within the same second that would result in identical-looking rows)
- Show the current yield curve against other dates' yield curves
- Show the projected value of the user's orders after they get their money back (factoring in payments and the yield rate)
- Right now, the app can only add orders to the orders table, and can't delete or edit them. That makes sense if the app is meant to simulate one where the user is placing actual orders (e.g. in Zelle you don't have free-for-all access to edit your transaction history). But if it was instead more of a note-keeping app, the user should be able to edit and delete items in that table too (e.g. orders that they added mistakenly).