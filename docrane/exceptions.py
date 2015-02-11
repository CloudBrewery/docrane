class ImageNotFoundError(Exception):
    def __init__(self, image, tag):
        super(ImageNotFoundError, self).__init__(
            "Image %s with tag %s not found." % (image, tag))
