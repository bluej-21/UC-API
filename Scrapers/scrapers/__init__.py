# strucutre for scraping

def get_urls(url, fun, tag=None, *args):
    # string, fun, params to fun after url -> (dept, list of urls)
    # the function `fun` should return a list of strings
    
    if args:
        return (tag, fun(url, *args))
    return (tag, fun(url))

def get_data(url, fun, tag=None, *args):
    # string, function, params to fun after url -> dict of course_data
    if args:
        return (tag, fun(url, *args))
    return (tag, fun(url))

def unpack_data(data):
    # data looks like
    # data = [ dept, dept, dept, dept, ...]
    # dept = [ course, course, ...]
    # course = { stuff }
    pass
