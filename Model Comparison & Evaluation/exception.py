
import sys

def format_error_message(error, error_detail: sys):
    """
    Formats error message with details like file name and line number where the error occurred.
    
    :param error: Exception object
    :param error_detail: sys.exc_info() for accessing error details
    :return: Formatted error message as a string
    """
    _, _, exc_tb = error_detail.exc_info()

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno

    # ANSI escape codes for colors
    color_red = "\033[91m"
    color_green = "\033[92m"
    color_end = "\033[0m"  # Reset color to default

    error_message = "{color_red}Error occurred in Python script '{0}', line {1}: {2}{color_end}".format(
        file_name, line_number, str(error), color_red=color_red, color_end=color_end
    )

    return error_message

class CustomException(Exception):

    def __init__(self, error_message, error_detail: sys):
        """
        :param error_message: Error message in string format
        :param error_detail: sys.exc_info() for accessing error details
        """
        super().__init__(error_message)

        self.error_message = format_error_message(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        """
        Overrides the string representation of the exception.
        
        :return: Formatted error message
        """
        return self.error_message
