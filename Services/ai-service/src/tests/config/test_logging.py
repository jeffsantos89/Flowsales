import logging
import os
import pytest
from unittest.mock import patch, MagicMock
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
import tempfile
from typing import Generator

class TestLoggingConfig:
    @pytest.fixture
    def temp_log_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def logger_config(self) -> dict:
        """Basic logger configuration fixture."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'detailed'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }

    @pytest.fixture
    def setup_logging(self, temp_log_dir: str, logger_config: dict) -> logging.Logger:
        """Setup logging configuration for tests."""
        log_file = os.path.join(temp_log_dir, 'test.log')
        logger_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 3,
            'formatter': 'detailed'
        }
        logger_config['root']['handlers'].append('file')
        
        logging.config.dictConfig(logger_config)
        return logging.getLogger('test_logger')

    def test_logger_initialization(self, setup_logging: logging.Logger):
        """Test if logger is properly initialized."""
        assert isinstance(setup_logging, logging.Logger)
        assert setup_logging.level == logging.INFO
        assert len(setup_logging.handlers) > 0

    def test_log_message_creation(self, setup_logging: logging.Logger, temp_log_dir: str):
        """Test if log messages are properly created and stored."""
        test_message = "Test log message"
        setup_logging.info(test_message)

        log_file = os.path.join(temp_log_dir, 'test.log')
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert test_message in log_content

    @pytest.mark.parametrize("log_level,message", [
        (logging.DEBUG, "Debug message"),
        (logging.INFO, "Info message"),
        (logging.WARNING, "Warning message"),
        (logging.ERROR, "Error message"),
        (logging.CRITICAL, "Critical message")
    ])
    def test_different_log_levels(self, setup_logging: logging.Logger, log_level: int, message: str):
        """Test logging at different levels."""
        with patch.object(setup_logging, 'log') as mock_log:
            setup_logging.log(log_level, message)
            mock_log.assert_called_once_with(log_level, message)

    def test_rotating_file_handler_configuration(self, setup_logging: logging.Logger):
        """Test if RotatingFileHandler is properly configured."""
        file_handlers = [h for h in setup_logging.handlers if isinstance(h, RotatingFileHandler)]
        assert len(file_handlers) > 0
        handler = file_handlers[0]
        assert handler.maxBytes == 1024 * 1024  # 1MB
        assert handler.backupCount == 3

    @pytest.mark.asyncio
    async def test_async_logging(self, setup_logging: logging.Logger):
        """Test logging in async context."""
        async def async_operation():
            setup_logging.info("Async operation started")
            return True

        result = await async_operation()
        assert result is True

    def test_logging_performance(self, setup_logging: logging.Logger, benchmark):
        """Test logging performance."""
        def log_messages():
            for i in range(100):
                setup_logging.info(f"Performance test message {i}")

        benchmark(log_messages)

    def test_error_handling(self, setup_logging: logging.Logger):
        """Test error handling in logging."""
        with patch.object(setup_logging.handlers[0], 'emit') as mock_emit:
            mock_emit.side_effect = Exception("Simulated error")
            
            # Should not raise exception
            setup_logging.info("This should handle the error gracefully")

    def test_logging_context(self, setup_logging: logging.Logger):
        """Test logging with context manager."""
        extra_context = {'request_id': '123', 'user_id': '456'}
        
        with patch.object(setup_logging, 'info') as mock_info:
            adapter = logging.LoggerAdapter(setup_logging, extra_context)
            adapter.info("Test message with context")
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0]
            assert "Test message with context" in str(call_args)
