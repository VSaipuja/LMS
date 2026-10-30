from app import create_app, db
from app.models import User, Course, Lesson, Quiz, Question, Attempt, Enrollment

app = create_app()


def _add_quiz_with_questions(course, title, questions_data, passing=60):
    quiz = Quiz(title=title, description=f'Quiz for {title}', course_id=course.id,
                time_limit_minutes=10, passing_score=passing)
    db.session.add(quiz)
    db.session.flush()
    for i, q in enumerate(questions_data):
        db.session.add(Question(
            quiz_id=quiz.id,
            text=q['text'],
            option_a=q['a'], option_b=q['b'], option_c=q['c'], option_d=q['d'],
            correct_option=q['ans'],
            order=i
        ))
    return quiz


def seed_data():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@lms.local', role='admin', department='GENERAL')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Admin → admin / admin123")

    instructors = [
        ('prof_cse', 'cse@lms.local', 'CSE'),
        ('prof_ece', 'ece@lms.local', 'ECE'),
        ('prof_eee', 'eee@lms.local', 'EEE'),
        ('prof_mech', 'mech@lms.local', 'MECH'),
        ('prof_civil', 'civil@lms.local', 'CIVIL'),
        ('prof_it', 'it@lms.local', 'IT'),
    ]
    instructor_map = {}
    for username, email, dept in instructors:
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=email, role='instructor', department=dept)
            user.set_password('teach123')
            db.session.add(user)
            db.session.flush()
        instructor_map[dept] = user
    db.session.commit()

    if Course.query.count() > 0:
        return  # already seeded

    # Real working YouTube educational videos (verified public IDs)
    # Format: course + list of lessons (title, youtube_id, quiz questions)
    catalog = [
        {
            'title': 'Python Programming Fundamentals',
            'dept': 'CSE',
            'desc': 'Learn Python step by step. Pass each quiz to unlock the next video.',
            'instructor': 'CSE',
            'lessons': [
                {
                    'title': 'Lesson 1: Python Full Course for Beginners',
                    'video': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
                    'desc': 'Complete Python tutorial by freeCodeCamp (49M+ views). Variables, strings, lists, functions, and more.',
                    'quiz': [
                        {'text': 'Which keyword defines a function in Python?',
                         'a': 'func', 'b': 'def', 'c': 'function', 'd': 'define', 'ans': 'B'},
                        {'text': 'What is print(2 ** 3)?',
                         'a': '6', 'b': '8', 'c': '9', 'd': '5', 'ans': 'B'},
                        {'text': 'Which type is immutable?',
                         'a': 'list', 'b': 'dict', 'c': 'tuple', 'd': 'set', 'ans': 'C'},
                    ]
                },
                {
                    'title': 'Lesson 2: Python for Beginners (Projects)',
                    'video': 'https://www.youtube.com/watch?v=eWRfhZUzrAc',
                    'desc': 'Hands-on Python with mini projects by freeCodeCamp.',
                    'quiz': [
                        {'text': 'Best loop when you know iteration count?',
                         'a': 'while', 'b': 'for', 'c': 'do-while', 'd': 'switch', 'ans': 'B'},
                        {'text': 'What does break do?',
                         'a': 'Skip iteration', 'b': 'Exit the loop', 'c': 'Restart', 'd': 'Pause', 'ans': 'B'},
                        {'text': 'range(3) produces?',
                         'a': '1,2,3', 'b': '0,1,2', 'c': '0,1,2,3', 'd': '1,2', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 3: Intermediate Python',
                    'video': 'https://www.youtube.com/watch?v=HGOBQPFzWKo',
                    'desc': 'Intermediate Python: OOP, modules, and advanced features.',
                    'quiz': [
                        {'text': 'No return statement → function returns?',
                         'a': '0', 'b': 'None', 'c': 'Error', 'd': 'Empty string', 'ans': 'B'},
                        {'text': 'How to import math module?',
                         'a': 'include math', 'b': 'using math', 'c': 'import math', 'd': 'require math', 'ans': 'C'},
                    ]
                },
            ]
        },
        {
            'title': 'Data Structures & Algorithms',
            'dept': 'CSE',
            'desc': 'Core DSA concepts. Unlock each topic by passing the quiz.',
            'instructor': 'CSE',
            'lessons': [
                {
                    'title': 'Lesson 1: DSA in Python – Full Course',
                    'video': 'https://www.youtube.com/watch?v=pkYVOmU3MgA',
                    'desc': 'Data Structures and Algorithms in Python – full beginner course (freeCodeCamp).',
                    'quiz': [
                        {'text': 'Array index access time complexity?',
                         'a': 'O(n)', 'b': 'O(1)', 'c': 'O(log n)', 'd': 'O(n²)', 'ans': 'B'},
                        {'text': 'Faster for random access?',
                         'a': 'Linked List', 'b': 'Array', 'c': 'Same', 'd': 'Depends', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 2: DSA Visual Crash Course',
                    'video': 'https://www.youtube.com/watch?v=RpLnQnurpLY',
                    'desc': 'Visual introduction to arrays, lists, stacks, queues, trees, and graphs.',
                    'quiz': [
                        {'text': 'Stack order is?',
                         'a': 'FIFO', 'b': 'LIFO', 'c': 'Random', 'd': 'Sorted', 'ans': 'B'},
                        {'text': 'Insert at head of linked list is usually?',
                         'a': 'O(n)', 'b': 'O(1)', 'c': 'O(log n)', 'd': 'O(n²)', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Database Management Systems',
            'dept': 'CSE',
            'desc': 'SQL and database design fundamentals.',
            'instructor': 'CSE',
            'lessons': [
                {
                    'title': 'Lesson 1: SQL Full Database Course',
                    'video': 'https://www.youtube.com/watch?v=HXV3zeQKqGY',
                    'desc': 'Complete SQL tutorial for beginners (21M+ views) – freeCodeCamp.',
                    'quiz': [
                        {'text': 'Command to retrieve data?',
                         'a': 'GET', 'b': 'SELECT', 'c': 'FETCH', 'd': 'QUERY', 'ans': 'B'},
                        {'text': 'PRIMARY KEY ensures?',
                         'a': 'Duplicates allowed', 'b': 'Unique non-null values', 'c': 'Faster joins only', 'd': 'Sorting', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 2: SQL for Web Developers',
                    'video': 'https://www.youtube.com/watch?v=KBDSJU3cGkc',
                    'desc': 'SQL for web developers – tables, CRUD, joins, and normalization.',
                    'quiz': [
                        {'text': 'INNER JOIN returns rows when?',
                         'a': 'Always all rows', 'b': 'Match exists in both', 'c': 'Only left', 'd': 'Only right', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Digital Electronics',
            'dept': 'ECE',
            'desc': 'Logic gates to sequential circuits. Pass quizzes to progress.',
            'instructor': 'ECE',
            'lessons': [
                {
                    'title': 'Lesson 1: Introduction to Digital Electronics',
                    'video': 'https://www.youtube.com/watch?v=2xXErGeeb_Q',
                    'desc': 'Introduction to digital systems by Neso Academy.',
                    'quiz': [
                        {'text': 'AND gate output is 1 when?',
                         'a': 'Any input is 1', 'b': 'All inputs are 1', 'c': 'All inputs are 0', 'd': 'Inputs differ', 'ans': 'B'},
                        {'text': 'NOT gate is also called?',
                         'a': 'Buffer', 'b': 'Inverter', 'c': 'Amplifier', 'd': 'Adder', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 2: Binary Coded Decimal (BCD)',
                    'video': 'https://www.youtube.com/watch?v=0rLiYpy2CqQ',
                    'desc': 'BCD code explained – Neso Academy.',
                    'quiz': [
                        {'text': 'A half adder adds how many bits?',
                         'a': '1', 'b': '2', 'c': '3', 'd': '4', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Basic Electrical Engineering',
            'dept': 'EEE',
            'desc': 'Circuit laws and fundamentals for EEE students.',
            'instructor': 'EEE',
            'lessons': [
                {
                    'title': 'Lesson 1: Introduction to BEE',
                    'video': 'https://www.youtube.com/watch?v=Vd2UJiIPbag',
                    'desc': 'Basic Electrical Engineering introduction (5M+ views).',
                    'quiz': [
                        {'text': "Ohm's law states?",
                         'a': 'V = I/R', 'b': 'V = IR', 'c': 'V = I+R', 'd': 'V = I²R', 'ans': 'B'},
                        {'text': 'KCL conserves?',
                         'a': 'Energy', 'b': 'Charge', 'c': 'Power', 'd': 'Voltage', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 2: Ohm\'s Law & KVL',
                    'video': 'https://www.youtube.com/watch?v=FjaJEo7knF4',
                    'desc': 'DC networks – Ohm\'s law and Kirchhoff\'s Voltage Law.',
                    'quiz': [
                        {'text': 'RMS of sine wave peak Vp is?',
                         'a': 'Vp', 'b': 'Vp/√2', 'c': 'Vp/2', 'd': '2Vp', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Engineering Mechanics',
            'dept': 'MECH',
            'desc': 'Statics fundamentals. Progress by completing quizzes.',
            'instructor': 'MECH',
            'lessons': [
                {
                    'title': 'Lesson 1: Engineering Mechanics Statics',
                    'video': 'https://www.youtube.com/watch?v=bMroBAdCE3s',
                    'desc': 'Forces, equilibrium, and free-body diagrams (popular statics lecture).',
                    'quiz': [
                        {'text': 'Body in equilibrium → net force is?',
                         'a': 'Maximum', 'b': 'Zero', 'c': 'Equal to weight', 'd': 'Infinite', 'ans': 'B'},
                        {'text': 'Moment of force = force × ?',
                         'a': 'Mass', 'b': 'Perpendicular distance', 'c': 'Velocity', 'd': 'Time', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Web Development Basics',
            'dept': 'IT',
            'desc': 'HTML, CSS and JavaScript. Unlock each part with a quiz.',
            'instructor': 'IT',
            'lessons': [
                {
                    'title': 'Lesson 1: CSS Full Course for Beginners',
                    'video': 'https://www.youtube.com/watch?v=OXGznpKZ_sA',
                    'desc': 'Complete CSS course by freeCodeCamp (3M+ views).',
                    'quiz': [
                        {'text': 'Tag for hyperlink?',
                         'a': '<link>', 'b': '<a>', 'c': '<href>', 'd': '<url>', 'ans': 'B'},
                        {'text': 'CSS stands for?',
                         'a': 'Computer Style Sheets', 'b': 'Cascading Style Sheets', 'c': 'Creative Style System', 'd': 'Colorful Style Sheets', 'ans': 'B'},
                    ]
                },
                {
                    'title': 'Lesson 2: JavaScript Full Course',
                    'video': 'https://www.youtube.com/watch?v=jS4aFq5-91M',
                    'desc': 'JavaScript programming full course – freeCodeCamp (4M+ views).',
                    'quiz': [
                        {'text': 'Block-scoped variable keyword?',
                         'a': 'var', 'b': 'let', 'c': 'define', 'd': 'int', 'ans': 'B'},
                        {'text': 'document.getElementById is used to?',
                         'a': 'Create element', 'b': 'Select element by id', 'c': 'Delete element', 'd': 'Style only', 'ans': 'B'},
                    ]
                },
            ]
        },
        {
            'title': 'Soft Skills & Communication',
            'dept': 'GENERAL',
            'desc': 'Available to all departments.',
            'instructor': 'CSE',
            'lessons': [
                {
                    'title': 'Lesson 1: Communication Skills',
                    'video': 'https://www.youtube.com/watch?v=HAnw168huqA',
                    'desc': 'Professional communication and presentation skills.',
                    'quiz': [
                        {'text': 'Good email subject should be?',
                         'a': 'Empty', 'b': 'Clear and specific', 'c': 'Very long', 'd': 'Only emojis', 'ans': 'B'},
                        {'text': 'Eye contact in presentations helps to?',
                         'a': 'Confuse audience', 'b': 'Build connection', 'c': 'Save time', 'd': 'Avoid questions', 'ans': 'B'},
                    ]
                },
            ]
        },
    ]

    for cdata in catalog:
        instructor = instructor_map.get(cdata['instructor']) or instructor_map['CSE']
        course = Course(
            title=cdata['title'],
            description=cdata['desc'],
            department=cdata['dept'],
            instructor_id=instructor.id,
            is_published=True
        )
        db.session.add(course)
        db.session.flush()

        for i, ld in enumerate(cdata['lessons']):
            quiz = _add_quiz_with_questions(
                course,
                title=f"Quiz: {ld['title']}",
                questions_data=ld['quiz'],
                passing=60
            )
            lesson = Lesson(
                course_id=course.id,
                title=ld['title'],
                description=ld.get('desc', ''),
                video_url=ld['video'],
                order=i,
                quiz_id=quiz.id
            )
            db.session.add(lesson)

    db.session.commit()
    print(f"Seeded {len(catalog)} courses with sequential video lessons + quizzes.")


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Course': Course, 'Lesson': Lesson,
        'Quiz': Quiz, 'Question': Question, 'Attempt': Attempt, 'Enrollment': Enrollment
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
