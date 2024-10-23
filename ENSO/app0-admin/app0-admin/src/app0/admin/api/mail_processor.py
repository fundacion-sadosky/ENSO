"""
Tmails: mail-processor
"""
import io
from datetime import datetime
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2
from jinja2.loaders import BaseLoader
from hopeit.app.context import EventContext
from hopeit.app.logger import app_extra_logger

from app0.admin.util.object_storage import ObjectStorage, ObjectStorageConf, ObjectStorageConnConfig
from app0.admin.db import db
from app0.admin.util.tmail_util import get_tmail_by_name
from app0.admin.tmail import TmailSend
from app0.admin import mail
from app0.admin.util import app_util

MAIL_USER = "ingar-app"
MAIL_PASS = "appNGR3657"
MAIL_MAIL = "ingar-app@santafe-conicet.gov.ar"
SMTP_PASS = "yAppFsNg25"
SMTP_SERVER = "smtp2.santafe-conicet.gov.ar"
SMTP_PORT = 25

TEMPLATES_FOLDER: Optional[str] = None
FROM_MAIL: Optional[str] = None

logger, extra = app_extra_logger()
object_store: Optional[ObjectStorage] = None

__steps__ = ['process']


async def __init_event__(context: EventContext):
    global TEMPLATES_FOLDER, FROM_MAIL, object_store
    if TEMPLATES_FOLDER is None:
        TEMPLATES_FOLDER = str(context.env["email_templates"]["templates_folder"])
    if FROM_MAIL is None:
        FROM_MAIL = str(context.env["env_config"]["mail_app_from"])
    if object_store is None:
        config: ObjectStorageConnConfig = context.settings(key='s3_store', datatype=ObjectStorageConnConfig)
        bucket: ObjectStorageConf = context.settings(key='bucket_docs', datatype=ObjectStorageConf)
        object_store = await ObjectStorage().connect(conn_config=config, bucket=bucket.bucket)


async def process(payload: TmailSend, context: EventContext):
    """
    process mail send
    """
    es = db(context.env)
    # load mail template
    tmail = await get_tmail_by_name(es, payload.template)
    assert tmail and TEMPLATES_FOLDER and object_store
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATES_FOLDER)
    template_env = jinja2.Environment(loader=template_loader)
    # template for req
    template = template_env.get_template(tmail.template)
    if tmail.content:
        # replace variables in html content
        body_template = jinja2.Environment(loader=BaseLoader).from_string(tmail.content)  # type: ignore
        body_template_rep = body_template.render(payload.replacements)
        payload.replacements[mail.VAR_CONTENT] = body_template_rep  # type: ignore
    # replace variables in template
    content_html = template.render(payload.replacements)
    # send_email
    for destination in payload.destinations:
        try:
            msg = MIMEMultipart()
            msg["Subject"] = tmail.subject
            msg["From"] = MAIL_MAIL
            # only send real name in production
            if destination.endswith('app0.me') or destination == "superuser":
                msg["To"] = "fhernandez@santafe-conicet.gov.ar"
            else:
                msg["To"] = destination

            body = MIMEText(content_html, "html")
            msg.attach(body)

            # # Log in Conicet SMTP server
            # smtp = SMTP(hostname=SMTP_SERVER, port=SMTP_PORT,
            #             username=MAIL_USER, password=SMTP_PASS,
            #             use_tls=True, start_tls=True)

            # await smtp.connect()
            # await smtp.starttls()
            # await smtp.login(MAIL_MAIL, SMTP_PASS)

            #  # Send the email
            # await smtp.send_message(msg)
        
            # write to disc for logging/testing purpose
            mailkey = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{destination}.html"
            object_id = f"{app_util.APP_APP_MAILS_RESOURCE_FOLDER}/{mailkey}"
            await object_store.store(key=object_id, file_obj=io.BytesIO(content_html.encode("utf-8")))
            logger.info(context, f"Mail send OK: {mailkey}")
        except (Exception, IOError) as e:  # pylint: disable=broad-except
            # TODO save error log if not sended
            # TODO write to disc
            logger.warning(context, f"Mail send ERROR {e}")
