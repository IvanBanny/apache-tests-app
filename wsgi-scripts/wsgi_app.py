import os
from urllib.parse import parse_qs
import redis
from jinja2 import Environment, FileSystemLoader
import sqlite3
from http import cookies

localpath = os.path.dirname(__file__)
html_dir = os.path.join(localpath, '../static')
con = sqlite3.connect(os.path.join(localpath, "../tests.db"), check_same_thread=False)
cur = con.cursor()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_test():
    questions = {}

    res = cur.execute("SELECT Q.qid, question_text, Op.oid, option_text, if_correct FROM questions Q, answer_options Op, answers A"
                      " WHERE Q.qid = A.qid AND Op.oid = A.oid")

    for x in res.fetchall():
        if x[0] not in questions:
            questions[x[0]] = {}
            questions[x[0]]['question-text'] = x[1]
            questions[x[0]]['options'] = {}
            questions[x[0]]['answer_oid'] = None
        questions[x[0]]['options'][x[2]] = x[3]
        if x[4]:
            questions[x[0]]['answer_oid'] = x[2]

    return questions


def get_post_form(environ):
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    post_data = environ['wsgi.input'].read(content_length).decode()
    form = parse_qs(post_data)
    return form


def submit_page(environ):
    questions = get_test()

    # Get POST parameters
    user_answers = get_post_form(environ)

    # Calculate the grade
    num_correct = 0
    for qid, oid_list in user_answers.items():
        if questions[int(qid)]['answer_oid'] == int(oid_list[0]):
            num_correct += 1
    result = num_correct / len(questions)

    # Update the results stored in redis
    user_id = cookies.SimpleCookie(environ.get('HTTP_COOKIES', ''))

    r.lpush(f'user:{user_id}', int(result*100))
    results = r.lrange(f'user:{user_id}', 0, -1)

    # Load and render the HTML template with the questions data
    page_path = 'result-page.html'
    env = Environment(loader=FileSystemLoader(html_dir))
    template = env.get_template(page_path)
    output = template.render(results=results)

    return output


def tests_page(environ):
    questions = get_test()

    # Load and render the HTML template with the questions data
    page_path = 'testing-page.html'
    env = Environment(loader=FileSystemLoader(html_dir))
    template = env.get_template(page_path)
    output = template.render(questions=questions)

    return output


def application(environ, start_response):
    # Assign cookies if needed
    cookie = cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    if 'uid' not in cookie:
        user_id = r.incr('uid_cnt')
        cookie['uid'] = str(user_id)
    cookie_string = cookie.output()

    # Serve the test submit page
    if environ['PATH_INFO'] == '/submit':
        # Generate the page
        response = submit_page(environ)

        # Send response
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response)))]
        if cookie_string:
            headers.append(('Set-Cookie', cookie_string))
        start_response('200 OK', headers)
        return [response.encode()]

    # Otherwise, serve the tests page

    # Generate the page
    response = tests_page(environ)

    # Send response
    headers = [('Content-type', 'text/html'),
               ('Content-Length', str(len(response)))]
    if cookie_string:
        headers.append(('Set-Cookie', cookie_string))
    start_response('200 OK', headers)
    return [response.encode()]
