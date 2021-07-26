from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'baileydog9999taco'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

RESPONSES = []

@app.route('/')
def home():
    surveytitles = []
    surveynames = [survey for survey in surveys]
    for name in surveynames:
        surveytitles.append(surveys[name].title)
    return render_template('home.html', surveytitles=surveytitles, surveynames=surveynames)\

@app.route('/survey', methods=["POST"])
def redirect_to_survey():
    survey = request.form["survey"]
    return redirect(f'{survey}/questions')

@app.route('/<survey>/questions')
def front_page(survey):
    """Show Front Page for Survey"""
    title = surveys[survey].title 
    instructions = surveys[survey].instructions
    return render_template("front.html", title=title, instructions=instructions, survey=survey)
    
@app.route('/<survey>/questions/<int:questnum>')
def question_form(survey, questnum):
    """show form"""
    title = surveys[survey].title 
    instructions = surveys[survey].instructions
    if questnum > len(surveys[survey].questions) - 1:
        flash('Please answer questions in order', 'error')
        questnum = len(RESPONSES)
        return redirect(f'{survey}/questions/{questnum}')
    question = surveys[survey].questions[questnum].question
    choices = surveys[survey].questions[questnum].choices
    allow_text = surveys[survey].questions[questnum].allow_text
    if questnum is not len(RESPONSES):
        flash('Please answer questions in order', 'error')
        return redirect(f'{survey}/questions/{len(RESPONSES)}')
    return render_template("question.html", choices=choices, question=question, instructions = instructions, title = title, questnum=questnum, survey=survey, allow_text=allow_text)

@app.route('/<survey>/answer', methods=["POST"])
def form_answer(survey):
    questnum = int(list(request.form.keys())[0][-1])
    choicenum = int(request.form[f'choice{questnum}'][-1])
    answer = surveys[survey].questions[questnum].choices[choicenum]
    if surveys[survey].questions[questnum].allow_text == True:
        comment = request.form['comment']
        RESPONSES.append(f'{answer}, {comment}')
    else:
        RESPONSES.append(answer)
    if questnum >= len(surveys[survey].questions) - 1:
        return redirect(f'./thanks')
    else:
        return redirect(f'./questions/{questnum+1}')
    
@app.route('/<survey>/thanks')
def thanks(survey):
    questions = []
    for question in surveys[survey].questions:
        questions.append(question.question)
    return render_template('thanks.html', responses=RESPONSES, questions=questions, survey=survey)