class AdNotFoundException(Exception):

    def __init__(self, message='Ad not found.'):
        self.message = message
        super().__init__(self.message)


class UnauthorizedException(Exception):

    def __init__(self, message='Unauthorized.'):
        self.message = message
        super().__init__(self.message)


class AlreadyReviewedException(Exception):

    def __init__(self, message='You already reviewed this user.'):
        self.message = message
        super().__init__(self.message)
