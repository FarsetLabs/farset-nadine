import mailchimp
import traceback
import logging
from datetime import datetime, time, date, timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import get_template, render_to_string
from django.template import Template, TemplateDoesNotExist, Context, RequestContext
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from nadine.utils.slack_api import SlackAPI
from nadine import mailgun

logger = logging.getLogger(__name__)


def valid_message_keys():
    return ["all", "introduction", "newsletter", "new_membership", "first_day_checkin",
            "exit_survey", "member_survey", "no_return", "checkin", "invalid_billing", "new_key",
            "no_signin", "no_device", "edit_profile", "slack_invite"]


def send_manual(user, message):
    message = message.lower()
    if not message in valid_message_keys():
        return False
    if message == "introduction" or message == "all":
        send_introduction(user)
    if message == "newsletter" or message == "all":
        subscribe_to_newsletter(user)
    if message == "new_member" or message == "all":
        send_new_membership(user)
    if message == "first_day_checkin" or message == "all":
        send_first_day_checkin(user)
    if message == "exit_survey" or message == "all":
        send_exit_survey(user)
    if message == "member_survey" or message == "all":
        send_member_survey(user)
    if message == "no_return_checkin" or message == "all":
        send_no_return_checkin(user)
    if message == "invalid_billing" or message == "all":
        send_invalid_billing(user)
    if message == "no_signin" or message == "all":
        send_no_signin(user)
    if message == "no_device" or message == "all":
        send_no_device(user)
    if message == "new_key" or message == "all":
        send_new_key(user)
    if message == "edit_profile" or message == "all":
        send_edit_profile(user)
    if message == "slack_invite":
        SlackAPI().invite_user(user)
    return True


#####################################################################
#                        Email Verification
#####################################################################


def send_verification(emailObj):
    """Send email verification link for this EmailAddress object.
    Raises smtplib.SMTPException, and NoRouteToHost.
    """

    # Build our context
    site = Site.objects.get_current()
    verif_key = emailObj.get_verif_key()
    context_dict = {
        'site': site,
        'user': emailObj.user,
        'verif_key': verif_key,
    }
    context_dict['verify_link'] = emailObj.get_verify_link()

    subject = "Please Verify Your Email Address"
    text_template = get_template('email/verification_email.txt')
    text_msg = text_template.render(context=context_dict)
    html_template = get_template('email/verification_email.html')
    html_msg = html_template.render(context=context_dict)
    send_email(emailObj.email, subject, text_msg, html_msg)


#####################################################################
#                        User Alerts
#####################################################################
#
# These emails go out to users.
#
#####################################################################


def send_introduction(user):
    site = Site.objects.get_current()
    subject = "Introduction to Nadine"
    message = render_to_string('email/introduction.txt', context={'user': user, 'site': site})
    send_quietly(user.email, subject, message)


def subscribe_to_newsletter(user):
    if settings.MAILCHIMP_NEWSLETTER_KEY:
        try:
            mc = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)
            mc.lists.subscribe(id=settings.MAILCHIMP_NEWSLETTER_KEY, email={'email': user.email}, send_welcome=True)
        except:
            pass


def send_new_membership(user):
    site = Site.objects.get_current()
    membership = user.profile.last_membership()
    subject = "New %s Membership" % membership.membership_plan.name
    message = render_to_string('email/new_membership.txt', context={'user': user, 'membership': membership, 'site': site})
    send(user.email, subject, message)
    announce_new_membership(user)


def send_first_day_checkin(user):
    site = Site.objects.get_current()
    subject = "How was your first day?"
    message = render_to_string('email/first_day.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_exit_survey(user):
    site = Site.objects.get_current()
    subject = "Exit Survey"
    message = render_to_string('email/exit_survey.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_member_survey(user):
    site = Site.objects.get_current()
    subject = "Coworking Survey"
    message = render_to_string('email/member_survey.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_no_return_checkin(user):
    site = Site.objects.get_current()
    subject = "Checking In"
    message = render_to_string('email/no_return.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_invalid_billing(user):
    site = Site.objects.get_current()
    subject = "Billing Problem"
    message = render_to_string('email/invalid_billing.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_no_signin(user):
    site = Site.objects.get_current()
    subject = "Forget to sign in?"
    message = render_to_string('email/no_signin.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_no_device(user):
    site = Site.objects.get_current()
    subject = "Device Registration"
    message = render_to_string('email/no_device.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_new_key(user):
    site = Site.objects.get_current()
    subject = "Key Holding Details"
    message = render_to_string('email/new_key.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


def send_user_notifications(user, target):
    site = Site.objects.get_current()
    subject = "%s is here!" % target.get_full_name()
    message = render_to_string('email/user_notification.txt', context={'user': user, 'target': target, 'site': site})
    send(user.email, subject, message)


def send_contact_request(user, target):
    site = Site.objects.get_current()
    subject = "%s wants to connect!" % user.get_full_name()
    message = render_to_string('email/contact_request.txt', context={'user': user, 'target': target, 'site': site})
    send(target.email, subject, message)


def send_edit_profile(user):
    site = Site.objects.get_current()
    subject = "Please update your Nadine profile"
    message = render_to_string('email/edit_profile.txt', context={'user': user, 'site': site})
    send(user.email, subject, message)


#####################################################################
#                        System Alerts
#####################################################################
#
# These emails go out to the team.
#
#####################################################################


def announce_new_user(user):
    subject = "New User - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s just signed in for the first time! %s" % (user.get_full_name(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_free_trial(user):
    subject = "Free Trial - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s just signed in for the first time! %s" % (user.get_full_name(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_new_membership(user):
    membership = user.profile.last_membership()
    subject = "New %s: %s" % (membership.membership_plan.name, user.get_full_name())
    message = "Team,\r\n\r\n \t%s has a new %s membership! %s" % (user.get_full_name(), membership.membership_plan.name, team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_member_checkin(user):
    membership = user.profile.last_membership()
    subject = "Member Check-in - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s has been a %s member for almost a month!  Someone go see how they are doing. %s" % (user.get_full_name(), membership.membership_plan.name, team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_need_photo(user):
    subject = "Photo Opportunity - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s just signed in and we don't have a photo of them yet. %s" % (user.get_full_name(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_billing_disable(user):
    subject = "Disabled Automatic Billing - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s just disabled their automatic billing through Nadine. %s" % (user.get_full_name(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_bad_email(user):
    subject = "Email Problem - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \tWe had a problem sending the introduction email to '%s'. %s" % (user.email, team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_anniversary(user):
    subject = "Anniversary - %s" % (user.get_full_name())
    duration = user.profile.duration_str()
    message = "Team,\r\n\r\n \t%s has been with us now for %s! %s" % (user.get_full_name(), duration, team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_new_key(user):
    subject = "New Key - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \t%s has been assigned a new key! %s" % (user.get_full_name(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


def announce_special_day(user, special_day):
    subject = "Special Day - %s" % (user.get_full_name())
    message = "Team,\r\n\r\n \tToday is a special day for %s. Today is their %s! %s" % (user.get_full_name(), special_day.description.lower(), team_signature(user))
    send_quietly(settings.TEAM_EMAIL_ADDRESS, subject, message)


# Unused and I'm not sure why this is here.
# This was also implemented in mailgun.send_manage_member
# def manage_member_email(user):
#     subject = "Email Problem - %s" % (user.get_full_name())
#     # Adjust the subject if we have a prefix
#     if hasattr(settings, "EMAIL_SUBJECT_PREFIX"):
#         subject = settings.EMAIL_SUBJECT_PREFIX.strip() + " " + subject
#
#     c = Context({
#         'user': user,
#         'domain': Site.objects.get_current().domain,
#     })
#     text_content, html_content = mailgun.render_templates(c, "manage_member")
#     logger.debug("text_context: %s" % text_content)
#     logger.debug("html_content: %s" % html_content)
#
#     mailgun_data = {"from": settings.EMAIL_ADDRESS,
#                     #		"to": [settings.TEAM_EMAIL_ADDRESS, ],
#                     "to": [settings.EMAIL_ADDRESS, ],
#                     "subject": subject,
#                     "text": text_content,
#                     "html": html_content,
#                     }
#     mailgun.mailgun_send(mailgun_data)


#####################################################################
#                        Utilities
#####################################################################


def get_templates(email_key):
    text_template = None
    html_template = None

    template_override = EmailTemplate.objects.filter(key=email_key).first()
    if template_override:
        if template_override.text_body:
            text_template = Template(template_override.text_body)
        if t.html_body:
            html_template = Template(template_override.html_body)
    else:
        try:
            text_template = get_template("email/%s.txt" % email_key)
            html_template = get_template("email/%s.html" % email_key)
        except TemplateDoesNotExist:
            logger.debug('There is no template for email key "%s"' % email_key)
            logger.debug('Exiting quietly')

    return (text_template, html_template)


def render_templates(context, email_key):
    text_content = None
    html_content = None
    text_template, html_template = get_templates(location, email_key)
    if text_template:
        text_content = text_template.render(context)
    if html_template:
        html_content = html_template.render(context)
    return (text_content, html_content)


def team_signature(user):
    site = Site.objects.get_current()
    return render_to_string('email/team_email_signature.txt', context={'user': user, 'site': site})


def send(recipient, subject, text_message, html_message=None):
    send_email(recipient, subject, text_message, html_message=html_message, fail_silently=False)


def send_quietly(recipient, subject, text_message, html_message=None):
    send_email(recipient, subject, text_message, html_message=html_message, fail_silently=True)


def send_email(recipient, subject, text_message, html_message=None, fail_silently=False):
    # Pull the user from the email address
    user = User.objects.filter(email=recipient).first()

    # A little safety net when debugging
    if settings.DEBUG:
        recipient = settings.EMAIL_ADDRESS

    # Adjust the subject if we have a prefix
    if hasattr(settings, "EMAIL_SUBJECT_PREFIX"):
        subject = settings.EMAIL_SUBJECT_PREFIX.strip() + " " + subject.strip()

    note = None
    success = False
    try:
        msg = EmailMultiAlternatives(subject, text_message, settings.EMAIL_ADDRESS, [recipient])
        if html_message:
            msg.attach_alternative(html_message, 'text/html')
        msg.send(fail_silently=False)
        success = True
    except:
        note = traceback.format_exc()
        if fail_silently:
            pass
        raise
    finally:
        if user:
            try:
                from nadine.models.core import SentEmailLog
                log = SentEmailLog(user=user, recipient=recipient, subject=subject, success=success)
                if note:
                    log.note = note
                log.save()
            except Exception as e:
                logger.error(e)


# Copyright 2016 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
