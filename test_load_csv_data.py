import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from pathlib import Path

from load_csv_data import load_csv_data as lcd


class TestLoadCSVData(unittest.TestCase):

    def test_ensure_data_dir_creates_directory(self):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            lcd.ensure_data_dir()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_csv_download_url(self):
        year = 2025
        url = lcd.get_csv_download_url(year)
        self.assertIn(str(year), url)
        self.assertTrue(url.startswith("https://"))

    def test_get_most_recent_weekday(self):
        # Friday
        with patch("load_csv_data.datetime") as mock_datetime:
            mock_datetime.today.return_value = datetime(2025, 5, 16)  # Friday
            self.assertEqual(
                lcd.get_most_recent_weekday(), datetime(2025, 5, 16)
            )

        # Saturday
        mock_datetime.today.return_value = datetime(2025, 5, 17)
        self.assertEqual(
            lcd.get_most_recent_weekday(), datetime(2025, 5, 16)
        )

        # Sunday
        mock_datetime.today.return_value = datetime(2025, 5, 18)
        self.assertEqual(
            lcd.get_most_recent_weekday(), datetime(2025, 5, 16)
        )

    @patch("load_csv_data.requests.Session.get")
    def test_download_csv_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.content.decode.return_value = "Date,1 Mo\n05/16/2025,4.37"
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        with patch("load_csv_data.ensure_data_dir"):
            content = lcd.download_csv(2025)
        self.assertIn("05/16/2025", content)

    @patch("load_csv_data.requests.Session.get", side_effect=Exception("Network error"))
    def test_download_csv_failure(self, _):
        with patch("load_csv_data.ensure_data_dir"):
            result = lcd.download_csv(2025)
        self.assertEqual(result, "")

    @patch("builtins.open", new_callable=mock_open)
    @patch("load_csv_data.download_csv", return_value="Date,1 Mo\n05/16/2025,4.37")
    def test_try_downloading_csv_for_current_year(self, mock_download_csv, mock_file):
        with patch("load_csv_data.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 5, 16)
            self.assertTrue(lcd.try_downloading_csv_for_current_year())
            mock_file.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data="Date,1 Mo\n05/16/2025,4.37")
    def test_read_downloaded_csv(self, mock_file):
        rows = lcd.read_downloaded_csv(2025)
        self.assertEqual(rows[1][0], "05/16/2025")

    @patch("os.listdir", return_value=["2024.csv", "2025.csv"])
    def test_get_most_recent_year_with_csv_downloaded(self, _):
        self.assertEqual(lcd.get_most_recent_year_with_csv_downloaded(), 2025)

    @patch("load_csv_data.read_downloaded_csv", return_value=[["Date"], ["05/16/2025"]])
    def test_is_csv_row_present_for_most_recent_weekday(self, _):
        with patch("load_csv_data.get_most_recent_weekday", return_value=datetime(2025, 5, 16)):
            self.assertTrue(lcd.is_csv_row_present_for_most_recent_weekday(2025))

    @patch("os.listdir", return_value=["2025.csv"])
    def test_csv_downloaded_for_year_true(self, _):
        self.assertTrue(lcd.csv_downloaded_for_year(2025))

    @patch("os.listdir", return_value=["2024.csv"])
    def test_csv_downloaded_for_year_false(self, _):
        self.assertFalse(lcd.csv_downloaded_for_year(2025))

    @patch("load_csv_data.is_csv_row_present_for_most_recent_weekday", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    @patch("load_csv_data.download_csv", return_value="Date,1 Mo\n05/16/2025,4.37")
    @patch("os.listdir", return_value=["2025.csv"])
    def test_refresh_data_downloads_if_missing(
        self, mock_listdir, mock_download, mock_open, _
    ):
        with patch("load_csv_data.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 5, 17)
            result = lcd.refresh_data()
            self.assertEqual(result, 2025)
            mock_open.assert_called_once()


if __name__ == "__main__":
    unittest.main()
