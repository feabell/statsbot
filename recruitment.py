import sqlite3, pprint
from time import strftime, gmtime
import datetime

#database = '/home/feabell/services/agentapi.db'
database = '/var/www/agentapi/agentapi.db'

def list(recruits=False, invited=False, inducted=False, rejected=False, showfull=False, recid=False):

  output = 'ID | Date Added | Pilot & Capability | Agent Last Edit & Date\r\n'
  
  if rejected:
    status =3
  elif invited:
    status =2
  elif inducted:
    status =1
  elif recruits:
    status =0
  else:
    status =0
  
  if recid:
    results = query_db('SELECT id, '
                       'name, keyid, vcode, dateadded, blob, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE id=? '
                       , [recid])
  else:
    results = query_db('SELECT id, '
                       'name, keyid, vcode, dateadded, blob, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE status=? '
                       'ORDER BY dateadded', [status])

  for record in results:
      lastdate = False
      date = datetime.datetime.strptime(record['dateadded'], '%Y-%m-%d %H:%M:%S')
      if record['datelasttouch']:
        lastdate = datetime.datetime.strptime(record['datelasttouch'], '%Y-%m-%d %H:%M:%S')
      canfly =''

      if record['sb']:
        canfly += 'Bomber '
      if record['astero']:
        canfly += 'Astero '
      if record['strat']:
        canfly += 'Stratios '
      if record['recon']:
        canfly += 'Recon '
      if record['blops']:
        canfly += 'Blops '
      if record['t3']:
        canfly += 'T3 '

      output += '>' + str(record['id']).center(6) + '| ' 
      output +=  date.strftime("%d %b %H:%M")
      output += ' | <' + 'http://ridetheclown.com/eveapi/audit.php?usid='
      output += str(record['keyid'])+'&apik='+record['vcode'] + '|' 
      output += record['name'] + '> : ' 
      output += canfly
      if record['lastagent']:
         output += ' | ' + record['lastagent']  
      if lastdate: 
         output += ' - '+ lastdate.strftime("%d %b %H:%M")
      if showfull:
         output += ' ``` '+record['blob']+' ``` \r\n'

  return output

def update(param, users, agent):
  
  recruits = ''.join(users).split(',')

  for recruit in recruits:
	update = insert_db('UPDATE recruits '
                           'SET status=?, lastagent=?,  datelasttouch=datetime() '
                           'WHERE id=?', [param, agent, recruit])

  return

def getNew(recId):
  return query_db('SELECT id '
                  'FROM recruits WHERE id>?'
                       , [recId])

def query_db(query, args=(), one=False):
  """
  Method returns SQL elements from DB.
  """
  cur = get_db().execute(query, args)
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rv else None) if one else rv


def get_db():
  """
  Method checks if DB exists, if not creates connection. 
  Returns DB connection object.
  """
  db = connect_db()
  db.row_factory = sqlite3.Row

  return db

def connect_db():
  """
  Connects to DB.
  """
  return sqlite3.connect(database)

def insert_db(query, args=()):
  """
  Method inserts elements into DB, then closes the connection.
  """
  con = get_db()
  cur = con.execute(query, args)
  #print(query)
  #print(cur.rowcount)
  con.commit()
  cur.close()
