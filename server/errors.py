class BackendError(Exception):
    def __init__(self, code: str, *args: object, extra_data: dict[str, str | int | bool],  **kwargs) -> None:
        self.code = code
        self.extra_data = extra_data
        super().__init__(*args, **kwargs)

class MaxPollReachedError(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('MAX_POLL_REACHED', *args, extra_data={}, **kwargs)

class MaxBallotReachedError(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('MAX_BALLOT_REACHED', *args, extra_data={}, **kwargs)

class InvalidDataError(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('INVALID_DATA', *args, extra_data={}, **kwargs)

class PollNotFound(BackendError):
    def __init__(self, poll_id: str, *args: object, **kwargs) -> None:
        super().__init__('POLL_NOT_FOUND', *args, extra_data={'id': poll_id}, **kwargs)

class InvalidInternalState(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('INVALID_SERVER_STATE', *args, extra_data={}, **kwargs)

class NoSession(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('NO_SESSION', *args, extra_data={}, **kwargs)

class PermissionDenied(BackendError):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__('PERMISSION_DENIED', *args, extra_data={}, **kwargs)
