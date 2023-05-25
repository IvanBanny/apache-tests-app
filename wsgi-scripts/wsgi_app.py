import os
from jinja2 import Environment, FileSystemLoader

questions = [
    {
        'id': 'q0',
        'title': 'Question 1',
        'options': [
            {'id': 'op00', 'label': 'Option 1'},
            {'id': 'op01', 'label': 'Option 2'},
            {'id': 'op02', 'label': 'Option 3'}
        ],
        'correct': 'op01'
    },
    {
        'id': 'q1',
        'title': 'Question 2',
        'options': [
            {'id': 'op10', 'label': 'Option 1'},
            {'id': 'op11', 'label': 'Option 2'},
            {'id': 'op12', 'label': 'Option 3'}
        ],
        'correct': 'op12'
    }
]


def application(environ, start_response):
    if environ['PATH_INFO'] == '/submit':
        # Get query parameters
        query_string = environ['QUERY_STRING']
        submitted_answers = {}
        if query_string:
            # print(query_string)
            query_params = query_string.split('&')
            for param in query_params:
                key, value = param.split('=')
                submitted_answers[key] = value

        # Compare submitted answers with correct answers
        num_correct = 0
        for question in questions:
            question_id = question['id']
            correct_answer = question['correct']

            # print(submitted_answers[question_id], correct_answer)
            if question_id in submitted_answers and submitted_answers[question_id] == correct_answer:
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
    localpath = os.path.dirname(__file__)
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
