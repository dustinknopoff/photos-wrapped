import json
import logging
import sqlite3
import time

from photos_wrapped.stats import load_stats

con = sqlite3.connect("database.db")

cur = con.cursor()

WAIT_TIME = 0.1

while True:
    try:
        con.execute("BEGIN TRANSACTION")

        # Get the first row to be put into the queue, ordered by id
        cur.execute("SELECT * FROM queue WHERE status = 0 ORDER BY id LIMIT 1")
        row = cur.fetchone()

        if row is None:
            # No row available
            # Continue to the next iteration
            con.execute("ROLLBACK")
            logging.debug("No rows found")
            time.sleep(WAIT_TIME)
            continue

        # Parse out the values of the row
        _id, payload, response, status = row

        # Let other workers know that we are working on this task
        cur.execute("UPDATE queue SET status = 1 WHERE id = ?", (_id,))

        if cur.rowcount == 0:
            # Another worker beat us to this row
            # Rollback and continue
            con.execute("ROLLBACK")
            time.sleep(WAIT_TIME)
            continue

        con.commit()

        try:
            json.loads(payload)["year"]
        except:
            con.execute("UPDATE queue SET status = -1 WHERE id = ?", (_id,))
            con.commit()

        stats = load_stats(json.loads(payload)["year"], force_reload=True)

        # Mark it complete
        con.execute("UPDATE queue SET status = 2, response = ? WHERE id = ?", (json.dumps(stats), _id,))
        con.commit()

    except sqlite3.OperationalError:
        # Often, we get a database locked error here
        con.execute("ROLLBACK")
    except Exception as e:
        con.execute("ROLLBACK")
        print(f"Error processing queue: {e}")