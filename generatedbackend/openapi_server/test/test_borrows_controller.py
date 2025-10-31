import unittest

from flask import json

from openapi_server.models.borrow_book201_response import BorrowBook201Response  # noqa: E501
from openapi_server.models.borrow_input import BorrowInput  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.extend_input import ExtendInput  # noqa: E501
from openapi_server.models.get_borrows200_response import GetBorrows200Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBorrowsController(BaseTestCase):
    """BorrowsController integration test stubs"""

    def test_borrow_book(self):
        """Test case for borrow_book

        Borrow a book
        """
        borrow_input = {"borrower_email":"john@example.com","borrower_name":"John Doe","days":14,"book_id":1}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/borrows',
            method='POST',
            headers=headers,
            data=json.dumps(borrow_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_extend_borrow(self):
        """Test case for extend_borrow

        Extend borrowing period
        """
        extend_input = {"additional_days":7}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/borrows/{borrow_id}/extend'.format(borrow_id=56),
            method='POST',
            headers=headers,
            data=json.dumps(extend_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_borrow_by_id(self):
        """Test case for get_borrow_by_id

        Get borrow record by ID
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/borrows/{borrow_id}'.format(borrow_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_borrows(self):
        """Test case for get_borrows

        Get all borrow records
        """
        query_string = [('page', 1),
                        ('per_page', 10),
                        ('returned', True),
                        ('overdue_only', False)]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/borrows',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_return_book(self):
        """Test case for return_book

        Return a borrowed book
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/borrows/{borrow_id}/return'.format(borrow_id=56),
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
