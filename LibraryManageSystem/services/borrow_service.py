from datetime import datetime, timezone
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, has_app_context
from models import db
from models.borrow import BorrowRecord
from models.book import Book
from services.book_service import BookService

class BorrowService:
    @staticmethod
    def get_all_borrow_records():
        """Get all borrow records"""
        return BorrowRecord.query.all()
    
    @staticmethod
    def get_borrow_record_by_id(record_id):
        """Get borrow record by ID"""
        return BorrowRecord.query.get(record_id)
    
    @staticmethod
    def get_active_borrows():
        """Get all active (not returned) borrow records"""
        return BorrowRecord.query.filter_by(returned=False).all()
    
    @staticmethod
    def get_overdue_borrows():
        """Get all overdue borrow records"""
        return BorrowRecord.query.filter(
            BorrowRecord.returned == False,
            BorrowRecord.due_date < datetime.utcnow()
        ).all()
    
    @staticmethod
    def get_borrower_history(borrower_email):
        """Get borrow history for a specific borrower"""
        return BorrowRecord.query.filter_by(borrower_email=borrower_email).all()
    
    @staticmethod
    def borrow_book(data):
        """Borrow a book"""
        book_id = data.get('book_id')
        book = BookService.get_book_by_id(book_id)

        if not book:
            raise ValueError("Book not found")

        if not book.available:
            raise ValueError("Book is not available for borrowing")

        # Create borrow record
        borrow_record = BorrowRecord.from_dict(data)

        # Mark book as unavailable
        book.available = False
        db.session.add(borrow_record)
        db.session.commit()

        # Notify admin via external webhook (if configured) and/or internal notification service
        payload = {
            "event": "book_borrowed",
            "user": {
                "name": data.get("borrower_name"),
                "email": data.get("borrower_email")
            },
            "book": {
                "id": book.id,
                "title": book.title
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # If an external webhook URL is configured, POST to it (kept for integrations)
        external_url = None
        if has_app_context() and current_app.config.get('ADMIN_WEBHOOK_URL'):
            external_url = current_app.config.get('ADMIN_WEBHOOK_URL')
        else:
            external_url = os.environ.get('ADMIN_WEBHOOK_URL')

        if external_url:
            try:
                requests.post(external_url, json=payload, timeout=5)
            except Exception as e:
                print(f"Failed to POST to external webhook {external_url}: {e}")

        # Create an internal notification only if we have an app context (DB available)
        if has_app_context():
            try:
                from services.notification_service import NotificationService
                message = f"{data.get('borrower_name')} borrowed '{book.title}'"
                NotificationService.create_notification(event=payload['event'], message=message, payload=payload)
            except Exception as e:
                # Non-fatal: log and continue
                print(f"Failed to create internal notification: {e}")

        # Send email notification to admin
        # Resolve admin email from app config (if available) or env
        if has_app_context() and current_app.config.get('ADMIN_EMAIL'):
            admin_email = current_app.config.get('ADMIN_EMAIL')
        else:
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

        BorrowService.send_email_notification(
            subject="Book Borrowed Notification",
            recipient=admin_email,
            body=f"A book has been borrowed:\n\n"
                 f"User: {data.get('borrower_name')} ({data.get('borrower_email')})\n"
                 f"Book: {book.title} (ID: {book.id})\n"
                 f"Timestamp: {datetime.utcnow().isoformat()}"
        )

        return borrow_record

    @staticmethod
    def notify_admin_webhook(event, user, book, timestamp):
        """Send a notification to the admin via webhook"""
        webhook_url = "https://admin-notification-service.example.com/webhook"
        payload = {
            "event": event,
            "user": user,
            "book": book,
            "timestamp": timestamp
        }

        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            # Log the error (logging setup assumed)
            print(f"Failed to send webhook: {e}")
    
    @staticmethod
    def send_email_notification(subject, recipient, body):
        """Send an email notification

        Backends supported (env or app config `EMAIL_BACKEND`):
        - 'console' (default): prints email to stdout (safe for local testing)
        - 'smtp': sends via SMTP server
        - 'dummy': no-op (useful in tests)
        """
        # Resolve backend and sender from app config or environment
        if has_app_context() and current_app.config.get('EMAIL_BACKEND'):
            backend = current_app.config.get('EMAIL_BACKEND')
        else:
            backend = os.environ.get('EMAIL_BACKEND', 'console')

        if has_app_context() and current_app.config.get('EMAIL_FROM'):
            sender_email = current_app.config.get('EMAIL_FROM')
        else:
            sender_email = os.environ.get('EMAIL_FROM', 'noreply@example.com')

        # Console backend: safe for development/testing
        if backend == 'console':
            print("--- Email Notification (console backend) ---")
            print(f"From: {sender_email}")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(body)
            print("--- End Email ---")
            return

        if backend == 'dummy':
            return

        # SMTP backend
        smtp_host = os.environ.get('SMTP_HOST', None)
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER', None)
        smtp_password = os.environ.get('SMTP_PASSWORD', None)

        # Allow app config to override
        if has_app_context():
            smtp_host = current_app.config.get('SMTP_HOST', smtp_host)
            smtp_port = int(current_app.config.get('SMTP_PORT', smtp_port))
            smtp_user = current_app.config.get('SMTP_USER', smtp_user)
            smtp_password = current_app.config.get('SMTP_PASSWORD', smtp_password)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_host or 'localhost', smtp_port, timeout=10) as server:
                server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
        except Exception as e:
            # Log but don't raise (non-critical)
            print(f"Failed to send email via SMTP: {e}")
    
    @staticmethod
    def return_book(record_id):
        """Return a borrowed book"""
        record = BorrowService.get_borrow_record_by_id(record_id)
        
        if not record:
            raise ValueError("Borrow record not found")
        
        if record.returned:
            raise ValueError("Book has already been returned")
        
        # Mark as returned
        record.returned = True
        record.return_date = datetime.utcnow()
        
        # Mark book as available
        record.book.available = True
        
        db.session.commit()
        
        return record
    
    @staticmethod
    def extend_due_date(record_id, additional_days):
        """Extend the due date of a borrowed book"""
        record = BorrowService.get_borrow_record_by_id(record_id)
        
        if not record:
            raise ValueError("Borrow record not found")
        
        if record.returned:
            raise ValueError("Cannot extend due date for returned book")
        
        from datetime import timedelta
        record.due_date += timedelta(days=additional_days)
        db.session.commit()
        
        return record
    
    @staticmethod
    def search_and_paginate_borrows(search_params, page=1, per_page=10):
        """Search borrow records with pagination and filtering"""
        from utils.pagination_helpers import PaginationHelper, SearchFilter
        
        # Start with base query
        query = BorrowRecord.query
        
        # Apply search filters
        query = SearchFilter.apply_borrow_filters(query, search_params)
        
        # Apply pagination
        paginated_result = PaginationHelper.paginate_query(query, page, per_page)
        
        return paginated_result
    
    @staticmethod
    def get_borrows_paginated(page=1, per_page=10, search=None, status=None):
        """Get paginated borrow records with search and filtering support (simplified)"""
        from utils.pagination_helpers import PaginationHelper, SearchFilter
        
        # Prepare search parameters (simplified)
        search_params = {
            'search': search or '',
            'status': status or ''
        }
        
        # Use the existing search_and_paginate_borrows method
        result = BorrowService.search_and_paginate_borrows(search_params, page, per_page)
        
        return result