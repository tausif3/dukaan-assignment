import re


def square_regex(string):
    """
    This utility function strips the string for example :-
    string -> [python] decorators
    returns -> search_tag=python , search_term=decorators
    """
    start_pattern = "\["
    end_pattern = "\]"
    match_start = re.finditer(start_pattern, string)
    match_end = re.finditer(end_pattern, string)

    start_index = end_index = 0
    for index in zip(match_start, match_end):
        start_index, end_index = index[0].start(), index[1].start()

    # chop string for tag and keyword followed by tag.
    if start_index == 0 and end_index:
        search_tag = string[start_index + 1 : end_index]
        search_term = string.split("]")[1].strip()
        return search_tag, search_term
    return None, None


def colon_regex(string):
    """
    This utility function strips the string to get the search term.
    For example :-
    string -> body:How to write a for loop?
    Returns: body=True,title=False,string=How to write a for loop?

    Similarly for title:<text>
    """
    body_match = re.search("body:", string)
    title_match = re.search("title:", string)

    title = body = False
    if body_match:
        body_end = body_match.end()
        string = string[body_end:]
        body = True
    elif title_match:
        title_end = title_match.end()
        string = string[title_end:]
        title = True

    return title, body, string
