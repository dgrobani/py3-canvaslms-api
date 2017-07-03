# https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.create
# https://canvas.instructure.com/doc/api/quiz_questions.html#method.quizzes/quiz_questions.create

import canvas.core.api as api


# def create_formative_survey(course_id):
#    """ create a formative survey by creating a quiz and its questions """
course_id = '1826505'

quiz_text = 'Ongoing feedback is essential for learning and improvement. ' \
            'Please give me feedback so that we can work together to improve learning.\n\n' \
            'Your feedback is anonymous. If you would like me to get in touch with you personally ' \
            'about your feedback, please add your name and email address to your comments.'

question_descriptions = [
    'What’s working for you in this class? Which activities or strategies are most helpful to your learning?',
    'What’s not working for you? Which activities or strategies could I change to improve your learning?',
    'Are there content, concepts, or skills we\'ve covered that you don’t fully understand or '
    'that are giving you trouble?',
    'Would you like to share any other comments with me?'
]

quiz_data = {
    'quiz[title]': 'Formative Evaluation Survey',
    'quiz[description]': quiz_text,
    'quiz[quiz_type]': 'survey',
    'quiz[allowed_attempts]': -1,
    'quiz[published]': False
}
quiz_id = api.post('courses/{}/quizzes'.format(course_id), quiz_data).json()['id']

for question_position, question_description in enumerate(question_descriptions):
    question_data = {
        'question[question_name]': question_position + 1,
        'question[question_text]': question_description,
        'question[question_type]': 'essay_question',
        'question[position]': question_position + 1
    }
    api.post('courses/{}/quizzes/{}/questions'.format(course_id, quiz_id), question_data).json()
