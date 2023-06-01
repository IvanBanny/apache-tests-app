import os
import cgi
from urllib.parse import parse_qs
from jinja2 import Environment, FileSystemLoader
import sqlite3

localpath = os.path.dirname(__file__)
con = sqlite3.connect(os.path.join(localpath, "../tests.db"), check_same_thread=False)
cur = con.cursor()

# questions = {
#     0: {
#         'question-text': 'Question 1',
#         'options': {
#             0: "Option 1.1",
#             1: "Option 1.2",
#             2: "Option 1.3"
#         }
#     },
#     1: {
#         'question-text': 'Question 2',
#         'options': {
#             3: "Option 2.1",
#             4: "Option 2.2",
#             5: "Option 2.3"
#         }
#     },
#     2: {
#         'question-text': 'Question 3',
#         'options': {
#             6: "Option 3.1",
#             7: "Option 3.2",
#             8: "Option 3.3"
#         }
#     }
# }


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


def application(environ, start_response):
    questions = get_test()

    if environ['PATH_INFO'] == '/submit':
        # Get POST parameters
        user_answers = get_post_form(environ)

        # Calculate the grade
        num_correct = 0
        for qid, oid_list in user_answers.items():
            if questions[int(qid)]['answer_oid'] == int(oid_list[0]):
                num_correct += 1

        # Response message
        response = f'You answered {num_correct}/{len(questions)} questions correctly.'

        # Send response
        status = '200 OK'
        headers = [('Content-type', 'text/plain'),
                   ('Content-Length', str(len(response)))]
        start_response(status, headers)
        return [response.encode()]

    # For GET requests, serve the HTML page
    status = '200 OK'
    html_dir = os.path.join(localpath, '../static')
    page_path = 'testing-page.html'

    # Load and render the HTML template with the questions data

    # with open(os.path.join(html_dir, page_path), 'r') as page_file:
    #     output = page_file.read().encode()
    #
    # headers = [('Content-type', 'text/html'),
    #            ('Content-Length', str(len(output)))]
    # start_response(status, headers)
    # return [output]

    env = Environment(loader=FileSystemLoader(html_dir))
    template = env.get_template(page_path)
    output = template.render(questions=questions)

    headers = [('Content-type', 'text/html'),
               ('Content-Length', str(len(output)))]
    start_response(status, headers)
    return [output.encode()]
