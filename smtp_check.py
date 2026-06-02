#!/usr/bin/env python3
"""Standalone Microsoft 365 / GoDaddy SMTP checker.

This script is intentionally separate from the Django app. It uses only Python's
standard library and never stores the SMTP password in code.
"""

from __future__ import annotations

import argparse
import getpass
import os
import smtplib
import socket
import ssl
import sys
from email.message import EmailMessage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Microsoft 365 SMTP login and optionally send a test email."
    )
    parser.add_argument("--host", default=os.getenv("SMTP_HOST", "smtp.office365.com"))
    parser.add_argument("--port", type=int, default=int(os.getenv("SMTP_PORT", "587")))
    parser.add_argument("--user", default=os.getenv("SMTP_USER", "contact@dolphinislandtours.com"))
    parser.add_argument("--from-email", default=os.getenv("EMAIL_FROM"))
    parser.add_argument("--to", default=os.getenv("SMTP_TEST_TO", "camandhave@gmail.com"))
    parser.add_argument("--subject", default="Dolphin Island Tours SMTP test")
    parser.add_argument("--timeout", type=int, default=int(os.getenv("SMTP_TIMEOUT", "20")))
    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Only test SMTP connection/login; do not send an email.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print SMTP protocol debug output. Do not use in shared logs.",
    )
    parser.add_argument(
        "--skip-cert-verify",
        action="store_true",
        help="Diagnostic only: skip TLS certificate verification for local testing.",
    )
    return parser.parse_args()


def get_password() -> str:
    password = os.getenv("SMTP_PASSWORD")
    if password:
        return password
    return getpass.getpass("SMTP password: ")


def build_message(args: argparse.Namespace) -> EmailMessage:
    from_email = args.from_email or args.user
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg.set_content(
        "SMTP test email from Dolphin Island Tours.\n\n"
        "If you received this, Microsoft 365 SMTP login and sending worked.\n"
    )
    return msg


def main() -> int:
    args = parse_args()
    password = get_password()

    if not args.user:
        print("ERROR: SMTP username is required. Pass --user or set SMTP_USER.", file=sys.stderr)
        return 2

    if not args.auth_only and not args.to:
        print("ERROR: recipient is required. Pass --to or set SMTP_TEST_TO.", file=sys.stderr)
        return 2

    print(f"Connecting to {args.host}:{args.port} as {args.user}")

    try:
        context = ssl._create_unverified_context() if args.skip_cert_verify else ssl.create_default_context()
        with smtplib.SMTP(args.host, args.port, timeout=args.timeout) as smtp:
            if args.debug:
                smtp.set_debuglevel(1)

            code, greeting = smtp.ehlo()
            print(f"EHLO: {code} {greeting.decode(errors='replace')}")

            if smtp.has_extn("starttls"):
                smtp.starttls(context=context)
                code, greeting = smtp.ehlo()
                print(f"STARTTLS OK; EHLO: {code} {greeting.decode(errors='replace')}")
            else:
                print("ERROR: server did not advertise STARTTLS.", file=sys.stderr)
                return 1

            smtp.login(args.user, password)
            print("SMTP login: OK")

            if args.auth_only:
                print("Auth-only mode: no email sent.")
                return 0

            msg = build_message(args)
            smtp.send_message(msg)
            print(f"Test email sent: {msg['From']} -> {msg['To']}")
            return 0

    except smtplib.SMTPAuthenticationError as exc:
        print("SMTP login failed.", file=sys.stderr)
        print(f"Server response: {exc.smtp_code} {exc.smtp_error.decode(errors='replace')}", file=sys.stderr)
        print(
            "Check that the mailbox exists, the username is the full email address, "
            "SMTP AUTH is enabled for the mailbox, and the password/app password is correct.",
            file=sys.stderr,
        )
        return 1
    except smtplib.SMTPResponseException as exc:
        print(f"SMTP error: {exc.smtp_code} {exc.smtp_error.decode(errors='replace')}", file=sys.stderr)
        return 1
    except (socket.timeout, OSError) as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
