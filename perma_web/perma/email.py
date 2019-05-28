import logging

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Registrar, LinkUser
from .utils import tz_datetime

logger = logging.getLogger(__name__)


###
### Send email
###

def send_user_email(to_address, template, context):
    email_text = render_to_string(template, context=context)
    title, email_text = email_text.split("\n\n", 1)
    title = title.split("TITLE: ")[-1]
    success_count = send_mail(
        title,
        email_text,
        settings.DEFAULT_FROM_EMAIL,
        [to_address],
        fail_silently=False
    )
    return success_count

# def send_mass_user_email(template, recipients):
    # '''
    #     Opens a single connection to the mail server and sends many emails.
    #     Pass in recipients as a list of tuples (email, context):
    #     [('recipient@example.com', {'first_name': 'Joe', 'last_name': 'Yacoboski' }), (), ...]
    # '''
    # to_send = []
    # for recipient in recipients:
    #     to_address, context = recipient
    #     email_text = render_to_string(template, context)
    #     title, email_text = email_text.split("\n\n", 1)
    #     title = title.split("TITLE: ")[-1]
    #     to_send.append(( title,
    #                      email_text,
    #                      settings.DEFAULT_FROM_EMAIL,
    #                      [to_address]))

    # success_count = send_mass_mail(tuple(to_send), fail_silently=False)
    # return success_count

def send_admin_email(title, from_address, request, template="email/default.txt", context={}):
    """
        Send a message on behalf of a user to the admins.
        Use reply-to for the user address so we can use email services that require authenticated from addresses.
    """
    EmailMessage(
        title,
        render_to_string(template, context=context, request=request),
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        headers={'Reply-To': from_address}
    ).send(fail_silently=False)


def send_self_email(title, request, template="email/default.txt", context={}, devs_only=True):
    """
        Send a message to ourselves. By default, sends only to settings.ADMINS.
        To contact the main Perma email address, set devs_only=False
    """
    if devs_only:
        EmailMessage(
            title,
            render_to_string(template, context=context, request=request),
            settings.DEFAULT_FROM_EMAIL,
            [admin[1] for admin in settings.ADMINS]
        ).send(fail_silently=False)
    else:
        # Use a special reply-to address to avoid Freshdesk's filters: a ticket will be opened.
        EmailMessage(
            title,
            render_to_string(template, context=context, request=request),
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            headers={'Reply-To': settings.DEFAULT_REPLYTO_EMAIL}
        ).send(fail_silently=False)


def send_user_email_copy_admins(title, from_address, to_addresses, request, template="email/default.txt", context={}):
    """
        Send a message on behalf of a user to another user, cc'ing
        the sender and the Perma admins.
        Use reply-to for the user address so we can use email services that require authenticated from addresses.
    """
    EmailMessage(
        title,
        render_to_string(template, context=context, request=request),
        settings.DEFAULT_FROM_EMAIL,
        to_addresses,
        cc=[settings.DEFAULT_FROM_EMAIL, from_address],
        reply_to=[from_address]
    ).send(fail_silently=False)

###
### Collect user data, bundled for emails ###
###

def registrar_users(registrars=None):
    '''
        Returns all active registrar users plus assorted metadata as
        a list of dicts.
    '''
    users = []
    if registrars is None:
        registrars = Registrar.objects.all()
    for registrar in registrars:
        registrar_users = LinkUser.objects.filter(registrar = registrar.pk,
                                                  is_active = True,
                                                  is_confirmed = True)
        for user in registrar_users:
            users.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            })
    return users


def registrar_users_plus_stats(registrars=None, year=None):
    '''
        Returns all active registrar users plus assorted metadata as
        a list of dicts. By default, uses stats from current
        calendar year.
    '''
    users = []
    if year is None:
        year = timezone.now().year
    start_time = tz_datetime(year, 1, 1)
    end_time = tz_datetime(year + 1, 1, 1)
    if registrars is None:
        registrars = Registrar.objects.all()
    for registrar in registrars:
        registrar_users = LinkUser.objects.filter(registrar = registrar.pk,
                                                  is_active = True,
                                                  is_confirmed = True)
        for user in registrar_users:
            users.append({ "first_name": user.first_name,
                           "last_name": user.last_name,
                           "email": user.email,
                           "registrar_id": registrar.id,
                           "registrar_email": registrar.email,
                           "registrar_name": registrar.name,
                           "total_links": registrar.link_count,
                           "year_links": registrar.link_count_in_time_period(start_time, end_time),
                           "most_active_org": registrar.most_active_org_in_time_period(start_time, end_time),
                           "registrar_users": registrar_users })
    return users

