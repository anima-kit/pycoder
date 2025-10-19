### tests.unit.bases.test_unit_logger
from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from logging import Formatter, LogRecord
from pyfiles.bases.logger import ElapsedFormatter, with_spinner

class TestLoggerUnit(TestCase):
    def test_format_failure(self):
        """
        Test failed invoking of format.
        """
        record = MagicMock(spec=LogRecord)
        mock_formatter = MagicMock(spec=Formatter)
        mock_formatter.format.side_effect = Exception
        formatter = ElapsedFormatter(start_time=datetime.now())
        with self.assertRaises(Exception):
            formatter.format(record)

    def test_with_spinner_failure(self):
        """
        Test failed invoking of spinner.
        """
        description = "Test task"
        mock_logger = MagicMock()
        with patch("pyfiles.bases.logger.logger", mock_logger):
            mock_progress_cls = MagicMock()
            mock_progress_instance = MagicMock()
            mock_progress_cls.return_value.__enter__.return_value = mock_progress_instance
            mock_progress_instance.add_task.side_effect = Exception("spinner error")
            with patch("pyfiles.bases.logger.Progress", mock_progress_cls):
                with self.assertRaises(Exception):
                    with with_spinner(description):
                        pass