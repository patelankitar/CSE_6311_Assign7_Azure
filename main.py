from flask import Blueprint, render_template, request, redirect, url_for,jsonify 
from flask_login import current_user, login_required

from flask_qa.extensions import db
from flask_qa.models import Question, User

import jsonpickle
from datetime import datetime,timedelta

from sqlalchemy.sql import func

main = Blueprint('main', __name__)

allUsers = []
role = ''
startTime = []
endTime = []

# home route
@main.route('/')
def index():
    objects = Question.query.all()
    for o in objects:
        db.session.delete(o)
        db.session.commit()

    return render_template('index.html')

@main.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get("askQ"):
            print("Home Button Clicked...")
        else : 
            role = request.form['roleSelect']
            allUsers.append(role)
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html', role=role, **context)
    else:
        return render_template('home.html')


@main.route('/ask/<string:role>', methods=['GET', 'POST'])
def ask(role):
    if request.method == 'POST':
        question = request.form['question']
        
        question = Question(
            question=question, 
            score=0, 
            asked_by_id=0,
            hint ='',
            hint_requested = False
        )

        db.session.add(question)
        db.session.commit()

        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)
    else:
        # GET part 
        experts = User.query.filter_by(expert=True).all()

        context = {
            'experts' : experts
        }
        return render_template('ask.html',role=role, **context)

@main.route('/answer/<int:question_id>/<string:role>', methods=['GET', 'POST'])
def answer(question_id,role):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        if request.form.get("submitBtn"):
            question.answer = request.form['answer']
            db.session.commit()
            
        elif(request.form.get("hintBtn")):
            question.hint_requested = True
            db.session.commit()
        else:
            print("")
        
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)
    
        #return redirect(url_for('main.unanswered',role=role))

    context = {
        'question' : question
    }

    return render_template('answer.html',role=role, **context)


@main.route('/answered/<string:role>', methods=['GET', 'POST'])
def answered(role):
    answered_questions = Question.query\
        .filter(Question.answer != None)\
        .all()
    if len(answered_questions) > 0:
        context = {
            'answered_questions' : answered_questions
        }
        return render_template('answered.html',role=role, **context)
    else :
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)
    
@main.route('/score/<int:question_id>/<string:role>', methods=['GET', 'POST'])
def score(question_id,role):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.score = request.form['score']
        db.session.commit()

        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }

        return render_template('home.html', role=role, **context)

    else : 
        # GET Method 
        context = {
            'question' : question
        }

        return render_template('score.html',question_id=question_id,role=role, **context)

@main.route('/question/<int:question_id>')
def question(question_id):
    question = Question.query.get_or_404(question_id)

    context = {
        'question' : question
    }

    return render_template('question.html', **context)

@main.route('/unanswered/<string:role>', methods=['GET', 'POST'])
def unanswered(role):
    unanswered_questions = Question.query\
        .filter(Question.answer == None)\
        .all()
    if len(unanswered_questions) > 0:
        context = {
            'unanswered_questions' : unanswered_questions
        }
        return render_template('unanswered.html',role=role, **context)
    else :
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)

@main.route('/hintRequested/<string:role>', methods=['GET', 'POST'])
def hintRequested(role):
    hintRequested_questions = Question.query\
        .filter(Question.hint_requested == True)\
        .all()
    if len(hintRequested_questions) > 0:
        context = {
            'hintRequested_questions' : hintRequested_questions
        }
        return render_template('hintRequested.html',role=role, **context)
    else :
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)

@main.route('/hint/<int:question_id>/<string:role>', methods=['GET', 'POST'])
def hint(question_id,role):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.hint = request.form['hint']
        db.session.commit()
        
        questions = Question.query.filter(Question.answer != None).all()

        context = {
         'questions' : questions
        }
        return render_template('home.html',role=role,  **context)

    context = {
        'question' : question
    }

    return render_template('hint.html',role=role, **context)

@main.route("/results", methods=['GET', 'POST'])
def results():
    questions = Question.query.all()
    context = {
        'questions' : questions
    }
    
    avgScore = ''
    avgScore_val = Question.query.with_entities(func.avg(Question.score)).all()
  
    if (len(avgScore_val) > 0):
        print(avgScore_val[0])
        avgScore = str(avgScore_val[0]).replace(",","")

    return render_template('results.html', avgScore = avgScore, **context)
    
@main.route('/ChekUsers')
def ChekUsers():
    start= False
    print(allUsers)
    if "student" in allUsers and "teacher" in allUsers and "admin" in allUsers :
        print("contains")
        start = True
        startTime.append(datetime.now())
        endTime.append(datetime.now() + timedelta(minutes=2))
    return jsonify(start)

@main.route('/timer')
def timer():
    # startTime= datetime.now().strftime("%H:%M:%S")
    # print("here")
    # i = 0
    # print(startTime)
    # print(endTime)

    time1= datetime.now()
    # # time2 = datetime.now() + timedelta(minutes=2)

    seconds = 1
    if(len(endTime) > 0 ):
        time_delta = endTime[0] - time1
        seconds = time_delta.seconds
    
    minutes = 1 


    if seconds <= 0:
        context = {
            'seconds' : seconds, 
            'timeUp' : True
        }
    else:
        context = {
            'seconds' : seconds, 
            'timeUp' : False
        }
    return jsonify(context)
