def get_related(obj, pieces):
    pieces = pieces.split('.')
    while len(pieces) > 0:
        obj = getattr(obj, pieces.pop(0))
    return obj


class BaseAction:
    def get_candidate_url(self):
        raise NotImplementedError

    def get_result_url(self, **kwargs):
        raise NotImplementedError

    class Meta:
        abstract = True
