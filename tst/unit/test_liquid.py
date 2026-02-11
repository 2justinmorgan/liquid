from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from http import HTTPMethod
from src.liquid import Liquid


def append_target_module(var_name: str) -> str:
    return f"src.liquid.{var_name}"


class TestLiquidClient(TestCase):

    def setUp(self) -> None:
        self.base_url = "https://api.test.com"
        self.username = "test_user"
        self.password = "test_pass"
        self.account_id = "12345"
        
        with patch(append_target_module("_request")) as mock_req:
            mock_req.return_value.json.return_value = {"sessionToken": "initial_token"}
            mock_req.return_value.status_code = 200
            self.client = Liquid(self.username, self.password, self.base_url, self.account_id)

    def test_init_sets_account_code(self) -> None:
        self.assertEqual(self.client._account_code, "default%3A12345")
        self.assertEqual(self.client._session_token, "initial_token")

    @patch(append_target_module("_request"))
    def test_get_session_token_failure(self, mock_req: MagicMock) -> None:
        mock_req.return_value.json.return_value = {"error": "invalid"}
        with self.assertRaises(TypeError):
            self.client._get_session_token("user", "pass")

    @patch(append_target_module('_request'))
    @patch(append_target_module('_to_dict'))
    def test_query_reauth_on_unauthorized(self, mock_to_dict: MagicMock, mock_req: MagicMock) -> None:
        """Tests that _query calls _get_session_token if 'Authorization required' is returned."""
        mock_to_dict.side_effect = [{"description": "Authorization required"}, {"description": "something"}, {"description": "OK"}]
        
        resp_unauth = MagicMock()
        resp_unauth.text = "Authorization required"
        
        resp_login = MagicMock()
        resp_login.json.return_value = {"sessionToken": "new_token"}
        
        resp_success = MagicMock()
        resp_success.json.return_value = {"data": "success"}
        
        mock_req.side_effect = [resp_unauth, resp_login, resp_success]

        result = self.client._query(HTTPMethod.GET, "/test-path")
        
        self.assertEqual(self.client._session_token, "new_token")
        self.assertEqual(result.json(), {"data": "success"})
        self.assertEqual(mock_req.call_count, 3)

    @patch(append_target_module('_request'))
    def test_get_instruments_success(self, mock_req: MagicMock) -> None:
        mock_req.return_value.json.return_value = {
            "instruments": []
        }
        with patch('src.defines.instrument.InstrumentsDtoCollection') as MockDto:
            MockDto.return_value.instruments = []
            res = self.client.get_instruments()
            self.assertIsInstance(res, list)

    def test_get_market_data_invalid_times(self) -> None:
        from_time = datetime.now()
        to_time = from_time - timedelta(hours=1)
        with self.assertRaises(ValueError):
            self.client.get_market_data("AAPL", "1m", from_time, to_time)

    @patch(append_target_module('_request'))
    def test_place_order_success(self, mock_req):
        mock_req.return_value.json.return_value = {
            "orderId": "OID123",
            "updateOrderId": "UP123"
        }
        
        order_id, update_id = self.client.place_order(
            symbol="EUR/USD",
            order_type="LIMIT",
            side="BUY",
            effect="OPEN",
            quantity=1000.0,
            limit_price=1.10
        )
        
        self.assertEqual(order_id, "OID123")
        self.assertEqual(update_id, "UP123")
        sent_json = mock_req.call_args.kwargs['json']
        self.assertEqual(len(sent_json['orderCode']), 7)

    @patch(append_target_module('_request'))
    def test_get_order_history_params(self, mock_req: MagicMock) -> None:
        mock_req.return_value.json.return_value = {"orders": []}
        
        self.client.get_order_history(symbol="BTC/USD", order_id="999")
        
        sent_params = mock_req.call_args.kwargs['params']
        self.assertEqual(sent_params["for-instrument"], "BTC/USD")
        self.assertEqual(sent_params["with-order-id"], "999")
