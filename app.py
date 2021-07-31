from flask import Flask, request, render_template, redirect, flash, jsonify, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'baileydog9999taco'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

debug = DebugToolbarExtension(app)

@app.route('/')
def home():
    surveytitles = []
    surveynames = [survey for survey in surveys]
    for name in surveynames:
        surveytitles.append(surveys[name].title)
    html = render_template('home.html', surveytitles=surveytitles, surveynames=surveynames)
    resp = make_response(html)
    if session.get('responses') == True:
        session['responses'].clear()
    resp.delete_cookie('session')
    return resp

@app.route('/survey', methods=["POST"])
def redirect_to_survey():
    survey = request.form["survey"]
    survey_status = request.cookies.get(survey)
    if survey_status == 'completed':
        return render_template('already-complete.html')
    session['responses'] = [];
    return redirect(f'{survey}/questions')

@app.route('/<survey>/questions')
def front_page(survey):
    """Show Front Page for Survey"""
    if session.get('responses') == False:
        return redirect('/')
    else:
        title = surveys[survey].title 
        instructions = surveys[survey].instructions
        return render_template("front.html", title=title, instructions=instructions, survey=survey)
    
@app.route('/<survey>/questions/<int:questnum>')
def question_form(survey, questnum):
    """show form"""
    if session.get('responses') == False:
        return redirect('/')
    else:
        title = surveys[survey].title 
        instructions = surveys[survey].instructions
        responses = session['responses']
        if questnum > len(surveys[survey].questions) - 1:
            flash('Please answer questions in order', 'error')
            questnum = len(responses)
            return redirect(f'../../{survey}/questions/{questnum}')
        question = surveys[survey].questions[questnum].question
        choices = surveys[survey].questions[questnum].choices
        allow_text = surveys[survey].questions[questnum].allow_text
        if questnum is not len(responses):
            flash('Please answer questions in order', 'error')
            return redirect(f'../../{survey}/questions/{len(responses)}')
        return render_template("question.html", choices=choices, question=question, instructions = instructions, title = title, questnum=questnum, survey=survey, allow_text=allow_text)

@app.route('/<survey>/answer', methods=["POST"])
def form_answer(survey):
    if session.get('responses') == False:
        return redirect ('/')
    else:
        questnum = int(list(request.form.keys())[0][-1])
        choicenum = int(request.form[f'choice{questnum}'][-1])
        answer = surveys[survey].questions[questnum].choices[choicenum]
        responses = session['responses']
        if surveys[survey].questions[questnum].allow_text == True:
            comment = request.form['comment']
            responses.append(f'{answer}, {comment}')
        else:
            responses.append(answer)
        session['responses'] = responses
        print(session['responses'])
        if questnum >= len(surveys[survey].questions) - 1:
            return redirect(f'./thanks')
        else:
            return redirect(f'./questions/{questnum+1}')
    
@app.route('/<survey>/thanks')
def thanks(survey):
    questions = []
    for question in surveys[survey].questions:
        questions.append(question.question)
    
    html = render_template('thanks.html', responses=session['responses'], questions=questions, survey=survey)
    response = make_response(html)
    response.set_cookie(survey, 'completed')
    return response

@app.route('/return')
def return_home():
    session.clear()
    return redirect('/')
    