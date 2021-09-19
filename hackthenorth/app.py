from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, getConnection, executeReadQuery, executeWriteQuery, getusermsgs, apology
from ChatBot import ChatBot

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached

db = getConnection("htn.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# home
@app.route("/")
@login_required
def hello():
    hello.user_info = [None, None, None, None, None]
    username = executeReadQuery(db, "SELECT username FROM users WHERE id = ?", (session["user_id"],))[0][0]
    return render_template("index.html", username=username)


# not needed but ok
@app.route("/game")
@login_required
def notneededbutok():
    if hello.user_info:
        return redirect("/game/entryform")

    return redirect("/")


# chat with chatbot
@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatwithbot():
    if request.method == "GET":
        outputs = getusermsgs(db, (session["user_id"],))
        return render_template("chatbot.html", outputs=outputs[::-1])

    else:
        userinput = request.form.get("userinput")
        chatbotoutput = ChatBot(userinput)
        usr_id = session["user_id"]
        outputs = getusermsgs(db, (usr_id,))
        outputs.append((userinput, 'user',))
        for msg in chatbotoutput:
            outputs.append((msg, 'bot',))
        query = "INSERT INTO msgs VALUES (?, ?, 'user');"
        if executeWriteQuery(db, query, (usr_id, userinput,)):
            for msg in chatbotoutput:
                query = "INSERT INTO msgs VALUES (?, ?, 'bot');"
                executeWriteQuery(db, query, (usr_id, msg,))
            return render_template("chatbot.html", outputs=outputs[::-1])


# clear chat with chatbot
@app.route("/clearchat", methods=["GET", "POST"])
@login_required
def clearchat():
    if request.method == "GET":
        return redirect("/chatbot")

    query = "DELETE FROM msgs WHERE msgr_id = ?;"
    if executeWriteQuery(db, query, (session["user_id"],)):
        return redirect("/chatbot")


# sign in
@app.route("/signin", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("signin.html")

    username = request.form.get("username")
    pw = request.form.get("pw")
    query = "SELECT id, password FROM users WHERE username = ?"
    results = executeReadQuery(db, query, (username,))
    if len(results) != 1:
        return render_template("signin.html", problem="Incorrect username")
    
    if not check_password_hash(results[0][1], pw):
        return render_template("signin.html", problem="Incorrect password")

    session["user_id"] = results[0][0]

    return redirect("/")


# sign up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    username = request.form.get("username")
    pw = request.form.get("pw")
    query = "SELECT id FROM users WHERE username = ?"
    if len(executeReadQuery(db, query, (username,))) != 0:
        return render_template("signup.html", problem="Username is already in use", error=True)

    encrypted_pw = generate_password_hash(pw)
    query = "SELECT id FROM users WHERE password = ?"
    if len(executeReadQuery(db, query, (encrypted_pw,))) != 0:
        return render_template("signup.html", problem="Password is already in use", error=True)

    query = "INSERT INTO users (username, password) VALUES (?, ?);"
    if executeWriteQuery(db, query, (username, encrypted_pw,)):
        query = "SELECT id FROM users WHERE username = ?"
        session["user_id"] = executeReadQuery(db, query, (username,))[0][0]
        return redirect("/")


# 1st level
@app.route("/game/level1", methods=["GET", "POST"])
@login_required
def level1():
    if request.method == "GET":
        answers = []
        for i in hello.user_info[:3]:
            if i == None:
                answers.append("")
            else:
                answers.append(i)
        return render_template("gamelvl1.html", answers=answers, answered=True)

    emo = request.form.get("val1")
    print(emo)
    mem = request.form.get("val2")
    print(mem)
    sui = request.form.get("val3")
    print(sui)
    hello.user_info[0] = emo
    hello.user_info[1] = mem
    hello.user_info[2] = sui
    for i in range(len(hello.user_info)):
        if hello.user_info[i] == '':
            hello.user_info[i] = None
    print(hello.user_info)
    return redirect("/game/level2")


# 2nd level
@app.route("/game/level2")
@login_required
def level2():
    answers = []
    for i in hello.user_info[3:]:
        if i == None:
            answers.append("")
        else:
            answers.append(i)
    return render_template("gamelvl2.html", answers=answers, answered=True)


# processing user's answers
@app.route("/processing", methods=["GET", "POST"])
@login_required
def processing():
    if request.method == "GET":
        return redirect("/game/level1")

    val1 = request.form.get("val1")
    print(val1)
    val2 = request.form.get("val2")
    print(val2)
    hello.user_info[3] = val1
    hello.user_info[4] = val2
    print(hello.user_info)
    for i in range(len(hello.user_info)):
        if hello.user_info[i] == '':
            hello.user_info[i] = None
    processing.vals = []
    for i in hello.user_info:
        if i == "Too much" or i == "Always" or i == "A lot":
            processing.vals.append(100)
        elif i == "Enough" or i == "Sometimes":
            processing.vals.append(50)
        elif i == "Never" or i == "Not enough":
            processing.vals.append(0)
        else:
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(processing.vals)
    return redirect("/results")


# showing results of basic analysis
@app.route('/results')
def results():
    # 0-emotions, 1-memory, 2-suicidal, 3-sleep, 4-overwhelming
    print(processing.vals)
    diagnosis = []
    if processing.vals[2] == 100:
        diagnosis.append("Clinically depressed")
    if processing.vals[2] == 50 and processing.vals[0] == 100:
        diagnosis.append("Deeply depressed") 
    if processing.vals[2] == 0 and processing.vals[0] == 50:
        diagnosis.append("Possibly in depression, further evaluation needed")
    if processing.vals[1] == 100:
        diagnosis.append("Possibly suffers from memory loss, further tests needed")
    if processing.vals[3] == 100:
        diagnosis.append("Possible hypersomnia")
    elif processing.vals[3] == 0:
        diagnosis.append("Possibly an insomniac")
    if processing.vals[4] >= 50:
        diagnosis.append("Stressed out, needs a holiday, or a break at least")
    if len(diagnosis) == 0:
        return render_template("results.html", diagnosis=diagnosis, empty=True)
    return render_template("results.html", diagnosis=diagnosis, empty=False)


# before starting game, this is shown
@app.route('/game/entryform')
@login_required
def entryform():
    return render_template("entryform.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/aboutus")
def aboutus():
    names = ["Devansh Sharma", "Prakamya Singh", "Praneeth Suresh"]
    return render_template("about.html", names=names)


# error handling
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)