#!/srv/newsblur/venv/newsblur/bin/python

import sys
sys.path.append('/srv/newsblur')

import subprocess
import requests
import settings
import socket

def main():
    df = subprocess.Popen(["df", "/"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
    hostname = socket.gethostname()
    admin_email = settings.ADMINS[0][1]

    r = requests.get("https://api.mailgun.net/v3/newsletters.newsblur.com/stats/total",
                     auth=("api", settings.MAILGUN_ACCESS_KEY),
                     params={"event": ["accepted", "delivered", "failed"],
                             "duration": "2h"})
    stats = r.json()['stats'][0]
    delivered = stats['delivered']['total']
    accepted = stats['delivered']['total']
    bounced = stats['failed']['permanent']['total'] + stats['failed']['temporary']['total']
    
    if bounced / float(delivered) > 0.1:
        requests.post(
                "https://api.mailgun.net/v2/%s/messages" % settings.MAILGUN_SERVER_NAME,
                auth=("api", settings.MAILGUN_ACCESS_KEY),
                data={"from": "NewsBlur Monitor: %s <%s>" % (hostname, admin_email),
                      "to": [admin_email],
                      "subject": "%s newsletters bounced: %s > %s > %s" % (hostname, accepted, delivered, bounced),
                      "text": "Usage on %s: %s" % (hostname, output)})
        print " ---> %s newsletters bounced: %s > %s > %s" % (hostname, accepted, delivered, bounced)
    else:
        print " ---> %s newsletters OK: %s > %s > %s" % (hostname, accepted, delivered, bounced)
        
if __name__ == '__main__':
    main()
