class AdNotFoundException(Exception):

  def __init__(self, message="Ad not found."):
        self.message = message
        super().__init__(self.message)
