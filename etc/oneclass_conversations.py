# https://community.canvaslms.com/message/57773
# https://community.canvaslms.com/groups/canvas-developers/blog/2016/12/19/delete-all-canvas-conversations
# https://canvas.instructure.com/doc/api/conversations.html


from canvas.core.courses import get_courses, get_course_people

from canvas.core.api import get

terms = ['2017-1SP']
programs = ['NFNP']
synergis = False

for course in get_courses(terms, programs, synergis):
    print(course['sis_course_id'])
    for user_id in [user['id'] for user in get_course_people(course['id'], 'student')]:
        for convo_id in get('conversations?as_user_id={}&include_all_conversation_ids=true&filter=user_{}'
                            .format(user_id, user_id)).json()['conversation_ids']:
            try:
                for message in get('conversations/{}?as_user_id={}'.format(convo_id, user_id)).json()['messages']:
                    if 'oneclass' in message['body'].lower():
                        print(user_id, convo_id, message['id'], message['body'])
            except Exception as e:
                print('>>> exception @ user {}, convo {}: {}'.format(user_id, convo_id, e))
