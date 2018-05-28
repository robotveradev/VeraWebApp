def get_related(obj, pieces):
    pieces = pieces.split('.')
    while len(pieces) > 0:
        obj = getattr(obj, pieces.pop(0))
    return obj
