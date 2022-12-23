"""
Custom errors used by Mímir
"""

class CannotMoveFileError(Exception):
    """
    Raised if 'move' or 'mv' commands fail.

    Params:
    err_class: the type of error returned by run_command
    """
    def __init__(self, err_class, message="Unable to move output file to destination"):
        self.err_type = type(err_class)
        if self.err_type == FileNotFoundError:
            self.stderr_msg = None
        else:
            self.stderr_msg = err_class.stderr
        self.message = message

        super().__init__(self.message)

class ConflictingAssignmentID(Exception):
    """
    Raised if assignment ID does not match between JSON and the code file it points to.

    Params:
    msg: Message to display with exception
    """
    def __init__(self, msg="Assignment ID in code file does not match ID in JSON"):
        self.message = msg
        super().__init__(self.message)

