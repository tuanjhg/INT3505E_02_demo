from flask import Blueprint, request
from services.borrow_service import BorrowService
from utils.response_helpers import success_response, error_response, validate_json, handle_service_error

borrow_bp = Blueprint('borrows', __name__, url_prefix='/api/borrows')

@borrow_bp.route('', methods=['GET'])
@handle_service_error
def get_borrow_records():
    """Get all borrow records"""
    active_only = request.args.get('active', '').lower() == 'true'
    overdue_only = request.args.get('overdue', '').lower() == 'true'
    borrower_email = request.args.get('borrower_email')
    
    if borrower_email:
        records = BorrowService.get_borrower_history(borrower_email)
    elif overdue_only:
        records = BorrowService.get_overdue_borrows()
    elif active_only:
        records = BorrowService.get_active_borrows()
    else:
        records = BorrowService.get_all_borrow_records()
    
    return success_response(
        data=[record.to_dict() for record in records],
        message=f"Found {len(records)} borrow records"
    )

@borrow_bp.route('/<int:record_id>', methods=['GET'])
@handle_service_error
def get_borrow_record(record_id):
    """Get a specific borrow record"""
    record = BorrowService.get_borrow_record_by_id(record_id)
    if not record:
        return error_response("Borrow record not found", 404)
    
    return success_response(
        data=record.to_dict(),
        message="Borrow record retrieved successfully"
    )

@borrow_bp.route('', methods=['POST'])
@validate_json(['book_id', 'borrower_name', 'borrower_email'])
@handle_service_error
def borrow_book(data):
    """Borrow a book"""
    record = BorrowService.borrow_book(data)
    return success_response(
        data=record.to_dict(),
        message="Book borrowed successfully",
        status_code=201
    )

@borrow_bp.route('/<int:record_id>/return', methods=['POST'])
@handle_service_error
def return_book(record_id):
    """Return a borrowed book"""
    record = BorrowService.return_book(record_id)
    return success_response(
        data=record.to_dict(),
        message="Book returned successfully"
    )

@borrow_bp.route('/<int:record_id>/extend', methods=['POST'])
@validate_json(['additional_days'])
@handle_service_error
def extend_due_date(data, record_id):
    """Extend the due date of a borrowed book"""
    additional_days = data.get('additional_days', 7)
    record = BorrowService.extend_due_date(record_id, additional_days)
    return success_response(
        data=record.to_dict(),
        message=f"Due date extended by {additional_days} days"
    )

@borrow_bp.route('/overdue', methods=['GET'])
@handle_service_error
def get_overdue_books():
    """Get all overdue borrow records"""
    records = BorrowService.get_overdue_borrows()
    return success_response(
        data=[record.to_dict() for record in records],
        message=f"Found {len(records)} overdue books"
    )