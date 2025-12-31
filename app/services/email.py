"""Email notification service."""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_TLS

        # Initialize Jinja2 environment for email templates
        try:
            self.jinja_env = Environment(
                loader=PackageLoader("app", "templates/email"),
                autoescape=select_autoescape(["html", "xml"]),
            )
        except Exception:
            self.jinja_env = None
            logger.warning("Email templates not found, using inline templates")

    def _is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
    ) -> bool:
        """Send an email."""
        if not self._is_configured():
            logger.warning(
                f"Email not configured. Would send to: {to_emails}, subject: {subject}"
            )
            return False

        try:
            import aiosmtplib

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = ", ".join(to_emails)

            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Collect all recipients
            all_recipients = list(to_emails)
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=self.use_tls,
            )

            logger.info(f"Email sent successfully to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _get_base_html(self, content: str, title: str = "Procure-Pro-ISO") -> str:
        """Get base HTML template with content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2563eb;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9fafb;
                    padding: 20px;
                    border: 1px solid #e5e7eb;
                }}
                .footer {{
                    background-color: #374151;
                    color: #9ca3af;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #2563eb;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .info-box {{
                    background-color: #dbeafe;
                    border-left: 4px solid #2563eb;
                    padding: 15px;
                    margin: 15px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th, td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }}
                th {{
                    background-color: #f3f4f6;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Procure-Pro-ISO</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>This is an automated message from Procure-Pro-ISO.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

    async def send_rfq_invitation(
        self,
        vendor_email: str,
        vendor_name: str,
        rfq_number: str,
        rfq_title: str,
        deadline: str,
        invitation_link: str,
    ) -> bool:
        """Send RFQ invitation email to vendor."""
        content = f"""
        <h2>Request for Quotation Invitation</h2>
        <p>Dear {vendor_name},</p>
        <p>You have been invited to participate in the following Request for Quotation:</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>Title:</strong> {rfq_title}</p>
            <p><strong>Submission Deadline:</strong> {deadline}</p>
        </div>

        <p>Please click the button below to view the RFQ details and submit your quotation:</p>

        <p style="text-align: center;">
            <a href="{invitation_link}" class="button">View RFQ Details</a>
        </p>

        <p>If you have any questions, please contact our procurement team.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, f"RFQ Invitation: {rfq_number}")

        text_content = f"""
Request for Quotation Invitation

Dear {vendor_name},

You have been invited to participate in the following Request for Quotation:

RFQ Number: {rfq_number}
Title: {rfq_title}
Submission Deadline: {deadline}

Please visit {invitation_link} to view the RFQ details and submit your quotation.

Best regards,
Procurement Team
        """

        return await self.send_email(
            to_emails=[vendor_email],
            subject=f"RFQ Invitation: {rfq_number} - {rfq_title}",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_rfq_published_notification(
        self,
        vendor_emails: List[str],
        rfq_number: str,
        rfq_title: str,
        deadline: str,
    ) -> bool:
        """Send notification when RFQ is published."""
        content = f"""
        <h2>RFQ Published Notification</h2>
        <p>The following Request for Quotation has been published and is now open for submissions:</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>Title:</strong> {rfq_title}</p>
            <p><strong>Submission Deadline:</strong> {deadline}</p>
        </div>

        <p>Please submit your quotation before the deadline.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, f"RFQ Published: {rfq_number}")

        return await self.send_email(
            to_emails=vendor_emails,
            subject=f"RFQ Published: {rfq_number} - {rfq_title}",
            html_content=html_content,
        )

    async def send_quotation_received_confirmation(
        self,
        vendor_email: str,
        vendor_name: str,
        rfq_number: str,
        quotation_number: str,
        total_amount: float,
        currency: str,
    ) -> bool:
        """Send confirmation when quotation is received."""
        content = f"""
        <h2>Quotation Received</h2>
        <p>Dear {vendor_name},</p>
        <p>Thank you for submitting your quotation. We have received it successfully.</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>Quotation Number:</strong> {quotation_number}</p>
            <p><strong>Total Amount:</strong> {currency} {total_amount:,.2f}</p>
        </div>

        <p>Your quotation is now under review. We will notify you of the outcome.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, f"Quotation Received: {quotation_number}")

        return await self.send_email(
            to_emails=[vendor_email],
            subject=f"Quotation Received: {quotation_number}",
            html_content=html_content,
        )

    async def send_quotation_accepted_notification(
        self,
        vendor_email: str,
        vendor_name: str,
        rfq_number: str,
        rfq_title: str,
        quotation_number: str,
    ) -> bool:
        """Send notification when quotation is accepted."""
        content = f"""
        <h2>Congratulations! Your Quotation Has Been Accepted</h2>
        <p>Dear {vendor_name},</p>
        <p>We are pleased to inform you that your quotation has been accepted.</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>RFQ Title:</strong> {rfq_title}</p>
            <p><strong>Quotation Number:</strong> {quotation_number}</p>
        </div>

        <p>Our procurement team will contact you shortly with the next steps for the purchase order.</p>

        <p>Thank you for your participation.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, "Quotation Accepted")

        return await self.send_email(
            to_emails=[vendor_email],
            subject=f"Quotation Accepted: {quotation_number} for RFQ {rfq_number}",
            html_content=html_content,
        )

    async def send_quotation_rejected_notification(
        self,
        vendor_email: str,
        vendor_name: str,
        rfq_number: str,
        rfq_title: str,
        quotation_number: str,
    ) -> bool:
        """Send notification when quotation is rejected."""
        content = f"""
        <h2>Quotation Status Update</h2>
        <p>Dear {vendor_name},</p>
        <p>Thank you for your participation in our RFQ process.</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>RFQ Title:</strong> {rfq_title}</p>
            <p><strong>Quotation Number:</strong> {quotation_number}</p>
        </div>

        <p>After careful evaluation, we regret to inform you that your quotation was not selected for this procurement.</p>

        <p>We appreciate your effort and look forward to your participation in future opportunities.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, "Quotation Status Update")

        return await self.send_email(
            to_emails=[vendor_email],
            subject=f"Quotation Status: {quotation_number} for RFQ {rfq_number}",
            html_content=html_content,
        )

    async def send_rfq_deadline_reminder(
        self,
        vendor_email: str,
        vendor_name: str,
        rfq_number: str,
        rfq_title: str,
        deadline: str,
        hours_remaining: int,
    ) -> bool:
        """Send reminder before RFQ deadline."""
        content = f"""
        <h2>RFQ Deadline Reminder</h2>
        <p>Dear {vendor_name},</p>
        <p>This is a reminder that the submission deadline for the following RFQ is approaching:</p>

        <div class="info-box">
            <p><strong>RFQ Number:</strong> {rfq_number}</p>
            <p><strong>Title:</strong> {rfq_title}</p>
            <p><strong>Deadline:</strong> {deadline}</p>
            <p><strong>Time Remaining:</strong> Approximately {hours_remaining} hours</p>
        </div>

        <p>Please ensure your quotation is submitted before the deadline.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, f"RFQ Deadline Reminder: {rfq_number}")

        return await self.send_email(
            to_emails=[vendor_email],
            subject=f"Reminder: RFQ {rfq_number} deadline in {hours_remaining} hours",
            html_content=html_content,
        )

    async def send_vendor_registration_confirmation(
        self,
        vendor_email: str,
        vendor_name: str,
        vendor_code: str,
    ) -> bool:
        """Send confirmation when vendor registers."""
        content = f"""
        <h2>Vendor Registration Confirmation</h2>
        <p>Dear {vendor_name},</p>
        <p>Thank you for registering as a vendor with Procure-Pro-ISO.</p>

        <div class="info-box">
            <p><strong>Vendor Code:</strong> {vendor_code}</p>
            <p><strong>Status:</strong> Pending Approval</p>
        </div>

        <p>Your registration is currently under review. Once approved, you will be able to participate in our procurement processes.</p>

        <p>We will notify you once your registration has been reviewed.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, "Vendor Registration Confirmation")

        return await self.send_email(
            to_emails=[vendor_email],
            subject="Vendor Registration Confirmation - Procure-Pro-ISO",
            html_content=html_content,
        )

    async def send_vendor_activation_notification(
        self,
        vendor_email: str,
        vendor_name: str,
        vendor_code: str,
    ) -> bool:
        """Send notification when vendor is activated."""
        content = f"""
        <h2>Vendor Account Activated</h2>
        <p>Dear {vendor_name},</p>
        <p>Congratulations! Your vendor account has been activated.</p>

        <div class="info-box">
            <p><strong>Vendor Code:</strong> {vendor_code}</p>
            <p><strong>Status:</strong> Active</p>
        </div>

        <p>You can now participate in our procurement processes and receive RFQ invitations.</p>

        <p>Best regards,<br>Procurement Team</p>
        """

        html_content = self._get_base_html(content, "Vendor Account Activated")

        return await self.send_email(
            to_emails=[vendor_email],
            subject="Your Vendor Account is Now Active - Procure-Pro-ISO",
            html_content=html_content,
        )


# Global email service instance
email_service = EmailService()
