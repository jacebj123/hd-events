from google.appengine.api import mail
from django.template.defaultfilters import slugify
from google.appengine.ext import deferred
import random
import os

FROM_ADDRESS = 'Dojo Events <robot@hackerdojo.com>'
NEW_EVENT_ADDRESS = 'events@hackerdojo.com'
STAFF_ADDRESS = 'staff@hackerdojo.com'

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    MAIL_OVERRIDE = "nowhere@nowhere.com"
else:
    MAIL_OVERRIDE = False
        
def bug_owner_pending(e):
  body = """
Event: %s
Owner: %s
Date: %s
URL: http://%s/event/%s-%s
""" % (
    e.name, 
    str(e.member),
    e.start_time.strftime('%A, %B %d'),
    os.environ.get('HTTP_HOST'),
    e.key().id(),
    slugify(e.name),)
  
  if not e.is_approved():
    body += """
Alert! The events team has not approved your event yet.
Please e-mail them at events@hackerdojo.com to see whats up.
"""

  body += """

Cheers,
Hacker Dojo Events Team
events@hackerdojo.com
"""
 
  deferred.defer(mail.send_mail, sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(e.member.email()),
   subject="[Pending Event] Your event is still pending: " + e.name,
   body=body, _queue="emailthrottle")

def schedule_reminder_email(e):
  body = """

*REMINDER*

Event: %s
Owner: %s
Date: %s
URL: http://%s/event/%s-%s
""" % (
    e.name, 
    str(e.owner()),
    e.start_time.strftime('%A, %B %d'),
    os.environ.get('HTTP_HOST'),
    e.key().id(),
    slugify(e.name),)
  body += """

Hello!  Friendly reminder that your event is scheduled to happen at Hacker Dojo.

 * The person named above must be physically present
 * If the event has been cancelled, resecheduled or moved, you must login and cancel the event on our system

Cheers,
Hacker Dojo Events Team
events@hackerdojo.com

"""
 
  deferred.defer(mail.send_mail, sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(e.member.email()),
   subject="[Event Reminder] " + e.name,
   body=body, _queue="emailthrottle")
             
def notify_owner_confirmation(event):
    deferred.defer(mail.send_mail ,sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(event.member.email()),
        subject="[New Event] Submitted but **not yet approved**",
        body="""This is a confirmation that your event:

%s
on %s

has been submitted to be approved. You will be notified as soon as it's
approved and on the calendar. Here is a link to the event page:

http://events.hackerdojo.com/event/%s-%s

Again, your event is NOT YET APPROVED and not on the calendar.

Cheers,
Hacker Dojo Events Team
events@hackerdojo.com

""" % (
    event.name, 
    event.start_time.strftime('%A, %B %d'),
    event.key().id(),
    slugify(event.name),))


def notify_new_event(event):
    deferred.defer(mail.send_mail, sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(NEW_EVENT_ADDRESS),
        subject='[New Event] %s on %s' % (event.name, event.start_time.strftime('%a %b %d')),
        body="""Event: %s
Member: %s
When: %s to %s
Type: %s
Size: %s
Rooms: %s
Contact: %s (%s)
URL: %s
Fee: %s

Details: %s

Notes: %s

http://events.hackerdojo.com/event/%s-%s
""" % (
    event.name, 
    event.member.email(), 
    event.start_time.strftime('%l, %F %j %Y %I:%M%p'),
    event.end_time.strftime('%l, %F %j %Y %I:%M%p'),
    event.type,
    event.estimated_size,
    event.roomlist(),
    event.contact_name,
    event.contact_phone,
    event.url,
    event.fee,
    event.details,
    event.notes,
    event.key().id(),
    slugify(event.name),))


def notify_owner_approved(event):
    deferred.defer(mail.send_mail,sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(event.member.email()),
        subject="[Event Approved] %s" % event.name,
        body="""Your event is approved and on the calendar!

Friendly Reminder: You must be present at the event and make sure Dojo policies are followed.

Note: If you cancel or reschedule the event, please log in to our system and cancel the event!

http://events.hackerdojo.com/event/%s-%s

Cheers,
Hacker Dojo Events Team
events@hackerdojo.com

""" % (event.key().id(), slugify(event.name)))

def notify_owner_rsvp(event,user):
    deferred.defer(mail.send_mail,sender=FROM_ADDRESS, to=possibly_OVERRIDE_to_address(event.member.email()),
        subject="[Event RSVP] %s" % event.name,
        body="""Good news!  %s <%s> has RSVPd to your event.
        
Friendly Reminder: As per policy, all members are welcome to sit in on any event at Hacker Dojo.

As a courtesy, the Event RSVP system was built such that event hosts won't be surprised by the number of members attending their event.  Members can RSVP up to 48 hours before the event, after that the RSVP list is locked.

http://events.hackerdojo.com/event/%s-%s

Cheers,
Hacker Dojo Events Team
events@hackerdojo.com

""" % (user.nickname(),user.email(),event.key().id(), slugify(event.name)))

def possibly_OVERRIDE_to_address(default):
    if MAIL_OVERRIDE:
        return MAIL_OVERRIDE
    else:
        return default

def notify_owner_expiring(event):
    pass

def notify_owner_expired(event):
    pass
