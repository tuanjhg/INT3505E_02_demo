import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book_input import BookInput  # noqa: E501
from openapi_server.models.book_list_response import BookListResponse  # noqa: E501
from openapi_server.models.create_book201_response import CreateBook201Response  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.success_response import SuccessResponse  # noqa: E501
from openapi_server import util


def create_book(body):  # noqa: E501
    """Create a new book

    Add a new book to the library # noqa: E501

    :param book_input: 
    :type book_input: dict | bytes

    :rtype: Union[CreateBook201Response, Tuple[CreateBook201Response, int], Tuple[CreateBook201Response, int, Dict[str, str]]
    """
    book_input = body
    if connexion.request.is_json:
        book_input = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_book(book_id):  # noqa: E501
    """Delete book

    Delete a book from the library # noqa: E501

    :param book_id: Book ID
    :type book_id: int

    :rtype: Union[SuccessResponse, Tuple[SuccessResponse, int], Tuple[SuccessResponse, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_book_by_id(book_id):  # noqa: E501
    """Get book by ID

    Retrieve details of a specific book # noqa: E501

    :param book_id: Book ID
    :type book_id: int

    :rtype: Union[CreateBook201Response, Tuple[CreateBook201Response, int], Tuple[CreateBook201Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_books(page=None, per_page=None, search=None, available_only=None):  # noqa: E501
    """Get all books

    Retrieve a paginated list of books with optional search and filtering # noqa: E501

    :param page: Page number
    :type page: int
    :param per_page: Items per page
    :type per_page: int
    :param search: Search query for title or author
    :type search: str
    :param available_only: Show only available books
    :type available_only: bool

    :rtype: Union[BookListResponse, Tuple[BookListResponse, int], Tuple[BookListResponse, int, Dict[str, str]]
    """
    return 'do some magic!'


def update_book(book_id, body):  # noqa: E501
    """Update book

    Update an existing book&#39;s information # noqa: E501

    :param book_id: Book ID
    :type book_id: int
    :param book_input: 
    :type book_input: dict | bytes

    :rtype: Union[CreateBook201Response, Tuple[CreateBook201Response, int], Tuple[CreateBook201Response, int, Dict[str, str]]
    """
    book_input = body
    if connexion.request.is_json:
        book_input = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
