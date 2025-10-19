### pyfiles.bases.logger
## This setups a logger for the given repository. 
# Handlers are created for writing to both a file and to the console.

## External imports
from datetime import datetime
from contextlib import contextmanager
from logging import (
    FileHandler, 
    Formatter, 
    Logger, 
    LogRecord, 
    getLogger, 
    INFO
)
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Generator


class ElapsedFormatter(Formatter):
    """
    A custom logging formatter that adds an 'elapsed' attribute to log records,
    representing the time elapsed since the start of the logging session.

    Attributes
    ------------
        start_time: datetime (datetime)
                The starting timestamp for calculating elapsed time
    """

    def __init__(
        self, 
        start_time: datetime, 
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize the ElapsedFormatter with a specified start time.

        Args
        ------------
            start_time: datetime (datetime)
                The starting timestamp for calculating elapsed time
            *args:
                Additional arguments passed to the parent Formatter
            **kwargs: 
                Keyword arguments passed to the parent Formatter 
        """
        super().__init__(*args, **kwargs)
        self.start_time = start_time  


    def format(
        self, 
        record: LogRecord
    ) -> str:
        """
        Format the log record by adding an 'elapsed' attribute with the time since
        the start_time.

        Args
        ------------
            record: LogRecord (logging)
                The log record to be formatted

        Returns
        ------------
            str: 
                The formatted log message, including the elapsed time
            
        Raises
        ------------
            Exception: 
                If formatting the log fails, error is logged and raised
        """
        try:
            # Calculate the elapsed time since the start of the logging session
            elapsed: float = (datetime.now() - self.start_time).total_seconds()
            # Attach the elapsed time
            record.elapsed = elapsed
            # Parent class's format method
            return super().format(record)
        except Exception as e:
            raise


@contextmanager
def with_spinner(
    description: str
) -> Generator:
    """
    A reusable context manager that shows a spinner and logs status during long-running tasks.

    Args
    ------------
        descriptions: str
            Description of the task to show in the log and spinner
        
    Raises
    ------------
        Exception: 
            If managing the spinner fails, error is logged and raised
    """
    try:
        logger.info(f"⚙️ Starting task: {description}")
        # Create progress spinner
        with Progress(
            SpinnerColumn(),                                         # Shows a rotating spinner
            TextColumn("[progress.description]{task.description}"),  # Task description
            transient=True,                                          # Automatically removes when done
        ) as progress:
            task = progress.add_task(description)
            # Yield control to the user's code
            yield               
            # Log completion after the task finishes
            logger.info(f"✅ Completed task: {description}")
    except Exception as e:
        logger.error(f"❌ Task failed: {description} - Error: {str(e)}")
        raise


## Create a logger object for this module
logger: Logger = getLogger(__name__)

## Set minimum log level to INFO
# Only messages with level INFO or higher will be processed (i.e. no DEBUG)
logger.setLevel(INFO)

## Define where the log file will be saved
log_path: str = 'code-agent.log'

# Record start time
start_time: datetime = datetime.now()

## Create formatters for both file and console to define how log messages should look
# File handler | Formatted as: timestamp - log level - elapsed time - message
file_formatter: Formatter = ElapsedFormatter(
    start_time, 
    '%(asctime)s - %(levelname)s - %(elapsed).2fs - %(message)s'
)

# Rich console handler | Formatted as: timestamp - message
console_formatter: Formatter = ElapsedFormatter(
    start_time, 
    '%(asctime)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

## Create handlers to write logs to a file and to the console
file_handler: FileHandler = FileHandler(log_path, encoding="UTF-8")
rich_handler: RichHandler = RichHandler(
    level=0, 
    show_time=False, 
    rich_tracebacks=True,
    show_level=True,
    show_path=True,
    enable_link_path=False
)

## Set formatters
file_handler.setFormatter(file_formatter)
rich_handler.setFormatter(console_formatter)

## Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(rich_handler)