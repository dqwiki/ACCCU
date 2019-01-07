#!/usr/bin/python
import MySQLdb, time, urllib, json, datetime
cautiousblocks = ["{{anonblock}}","{{schoolblock}}","vandalism", "school"]
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="dqscript",         # your username
                     passwd="BravoackenDelta",  # your password
                     db="production")        # name of the data base
cur = db.cursor()
cur.execute("SELECT id,status,forwardedip FROM production.request where status != 'Closed' and status != 'Hold' and status != 'Checkuser' and emailconfirm RLIKE 'confirmed' and blockcheck = 0;")
table = cur.fetchall()
requestnumbers=list()
blocklist=list()
warnlist=list()
for row in table:
    #if search for comma
    requestnumbers.append(row[0])
    ip = row[2]
    try:
        ip = ip.split(", ")
    except:
        a=1 #just continue
    for item in ip:
        time.sleep(5)
        url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=&list=blocks&titles=&bkip="+item
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        try:blockdata=data["query"]["blocks"][0]
        except:
            cur.execute("UPDATE production.request SET blockcheck='1' WHERE id="+str(row[0])+";")
            db.commit()
            continue
        reason = blockdata["reason"]
        if "ACC ignore" in reason:
            cur.execute("UPDATE production.request SET blockcheck='1' WHERE id="+str(row[0])+";")
            db.commit()
            continue
        ip = blockdata["user"]
        first = True
        warn=False
        for blockreason in cautiousblocks:
            if blockreason.lower() in reason.lower():
                warn = True
                cur.execute("UPDATE production.request SET blockcheck='1' WHERE id="+str(row[0])+";")
                db.commit()
                continue
        if warn:continue
        blocklist.append(row[0])
        try:cidr = ip.split("/")
        except:cidr = False
        print "-------------"
        cur.execute("UPDATE production.request SET blockcheck='1' WHERE id="+str(row[0])+";")
        db.commit()
        cur.execute("UPDATE production.request SET status='Checkuser' WHERE id="+str(row[0])+";")
        db.commit()
        cur.execute("INSERT INTO production.comment (time, user, comment, visibility, request) VALUES (\""+time.strftime('%Y-%m-%d %H:%M:%S')+"\", '1733', \"Block detected requiring CU check\", \"user\", "+str(row[0])+");")
        db.commit()
        time.sleep(1)
        cur.execute("INSERT INTO production.log (objectid, objecttype, user, action, timestamp) VALUES ("+str(row[0])+", \"Request\", 1733, \"Deferred to checkusers\", \""+time.strftime('%Y-%m-%d %H:%M:%S')+"\");")
        db.commit()
        print "Done - " + str(row[0])
        cur.execute("UPDATE production.request SET blockcheck = 1 where status=\"Checkuser\";")
        db.commit()
db.close()
