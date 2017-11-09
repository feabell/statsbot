import sqlite3, pprint
from time import strftime, gmtime
import datetime
import yaml

#database = '/home/feabell/services/agentapi.db'
database = '/var/www/agentapi/agentapi.db'
config = yaml.load(file('plugins/stats/statsbot.conf', 'r'))
api_base_url = config["API_BASE_URL"]
skills_base_url = config["SKILLS_BASE_URL"]


def list(recruits=False, invited=False, inducted=False, rejected=False, showfull=False, recid=False, trial=False, endOfTrial=False,findByName=False,searchString = ''):

  output =''
  if endOfTrial:
    output+='AUTOGENERATED ALERT : PILOTS WHO END THEIR TRIAL WITHIN 48HOURS\r\n'

  output += 'ID | Date Added | Pilot & Capability | Agent Last Edit & Date\r\n'
  
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
                       'name, keyid, vcode, token, dateadded, blob, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE id=? '
                       , [recid])
  elif trial:
    weeksago_t = datetime.datetime.now() - datetime.timedelta(days=21)
    weeksago = weeksago_t.strftime('%Y-%m-%d %H:%M:%S')

    results = query_db('SELECT id, '
                       'name, keyid, vcode, token, dateadded, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE status=2 '
                       'AND datelasttouch > ? ', [weeksago]) 
  elif endOfTrial:
    weeksago_t = datetime.datetime.now() - datetime.timedelta(days=21)
    weeksago2_t = datetime.datetime.now() - datetime.timedelta(days=19)

    weeksago = weeksago_t.strftime('%Y-%m-%d %H:%M:%S')
    weeksago2 = weeksago2_t.strftime('%Y-%m-%d %H:%M:%S')

    results = query_db('SELECT id, '
                       'name, keyid, vcode, token, dateadded, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE status=2 '
                       'AND datelasttouch > ? AND datelasttouch < ?', [weeksago, weeksago2]) 
  elif findByName:
    results = query_db('SELECT id, '
                       'name, keyid, vcode, token, dateadded, blob, sb, astero, '
                       'strat, recon, t3, blops, '
                       'lastagent, datelasttouch FROM recruits WHERE name like ? '
                       , ['%'+searchString+'%'])
  else:
    results = query_db('SELECT id, '
                       'name, keyid, vcode, token, dateadded, blob, sb, astero, '
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

      #if record['token']:
      output += ' | <' + skills_base_url + record['name'] + '|'
      #else:
      #  output += ' | <' + api_base_url + '?usid='
      #  output += str(record['keyid'])+'&apik='+record['vcode'] + '|' 

      output += record['name'] + '> : ' 
      output += canfly
      if record['lastagent']:
         output += ' | ' + record['lastagent']  
      if lastdate: 
         output += ' - '+ lastdate.strftime("%d %b %H:%M")
      if showfull:
         output += ' ``` '+record['blob']+' ``` \r\n'
      else:
         output +=' \r\n'

  return output

def newMembers():
    
    dayago_t = datetime.datetime.now() - datetime.timedelta(days=1)
    dayago = dayago_t.strftime('%Y-%m-%d %H:%M:%S')

    results = query_db('SELECT name '
                       'FROM recruits WHERE status=2 '
                       'AND datelasttouch > ? ', [dayago]) 

    if len(results) > 0:
      output ='Please welcome the new agents who have joined in the last 24hours!\r\n'
      output += ",".join(pilots)

      return output    

    return False
   
def update(param, recruit, agent, note=''):
  
  results = query_db('SELECT note '
                     'FROM recruits WHERE id=?', [recruit])

  if len(results) == 1:
      dbnote = results[0]['notes']
  else:
      return False

  currtime = strftime('%H:%M %d-%m', gmtime()) 

  if param == 1:
    upd_type = 'Induction'
  elif param == 2:
    upd_type = 'Invite'
  elif param == 3: 
    upd_type = 'Rejection'
  else:
    upd_type = 'Other'

  dbnote += '==== ' +upd_type+ ' update by ' +agent+ ' at ' +currtime+ ' ====\r\n'
  dbnote += note
  dbnote +='\r\n'

  update = insert_db('UPDATE recruits '
                     'SET status=?, lastagent=?, datelasttouch=datetime(), '
                     'note=? '
                     'WHERE id=?', [param, agent, dbnote, recruit])

  return update

def getNew(recId):
  return query_db('SELECT id '
                  'FROM recruits WHERE id>? and status >=0'
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
  rows_affected = cur.rowcount
  #print(query)
  #print(cur.rowcount)
  con.commit()
  cur.close()

  return rows_affected
