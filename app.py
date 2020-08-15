from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)
from datetime import datetime
from flask_mongoengine import MongoEngine
app = Flask(__name__)
app.secret_key = "abc"

app.config['MONGODB_DB'] = 'project1'

db = MongoEngine()
db.init_app(app)



class BlogPost(db.Document):
    title = db.StringField(max_length=120, required=True)
    author = db.StringField(max_length=20)
    content = db.StringField()
    tags = db.ListField(db.StringField(max_length=30))
    likes = db.IntField(default=0)
    date_posted = db.DateTimeField(required=True,default=datetime.now().date())
    def __repr__(self):
        return 'Blog post ' + self.title

class User(db.Document):
    username = db.StringField(max_length=50)
    password = db.StringField(max_length=50)

    def __repr__(self):
        return 'Username :' + self.username


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/posts", methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(title=post_title, content=post_content,
                            author=post_author)
        new_post.save()

        return redirect('/posts')
    else:
        all_posts = BlogPost.objects
        if isLogged():
            user = "Logged As " + session['user']
        else:
            user = ""

        return render_template('posts.html', posts=all_posts,
                               isAdmin=isAdmin(), isLogged=isLogged(), user=user, inSearchMode=False)

@app.route('/posts/delete/<string:id>')
def delete(id):
    if isAdmin():
        post = BlogPost.objects.get_or_404(pk=id)
        BlogPost.delete(post)
        
        return redirect('/posts')
    else:
        return redirect('/posts')


@app.route('/posts/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):

    if isAdmin():
        post = BlogPost.objects.get_or_404(pk=id)

        if request.method == 'POST':
            post.title = request.form['title']
            post.author = request.form['author']
            post.content = request.form['content']
            post.save()
            return redirect('/posts')
        else:
            return render_template('edit.html', post=post)
    else:
        return redirect('/posts')


@app.route('/login', methods=['GET', 'POST'])
def login():
    isError = False
    if request.method == 'POST':
        session.pop("user", None)
        username = request.form['username'].lower()
        password = request.form['password']
        if valid(username, password):
            session['user'] = username

            return redirect("/posts")
        else:
            isError = True
            return render_template("login.html", isError=isError)

    return render_template("login.html")


def valid(username, password):
    isValid = False
    users = User.objects
    for user in users:
        if (user.username == username) and (user.password == password):
            isValid = True
            return isValid
        else:
            isValid = False
    return isValid

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if isAdmin():
        if request.method == 'POST':
            post.title = request.form['title']
            post.author = request.form['author']
            post.content = request.form['content']
            new_post = BlogPost(
                title=post_title, content=post_content, author=post_author)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/posts')
        else:
            return render_template('new_post.html')
    else:
        return redirect('/posts')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect("/posts")


@app.route('/posts/like/<string:id>')
def like(id):
    post = BlogPost.objects.get_or_404(pk=id)
    post.likes += 1
    post.save()
    return redirect('/posts')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    isError = False

    if request.method == 'POST':
        session.pop("user", None)
        username = request.form['username'].lower()
        password = request.form['password']
        usr = User(username=username, password=password)
        try:
            isError = False
            usr.save()

            session.pop("user", None)
            session['user'] = username.lower()

            return redirect("/posts")
        except Exception as e:
            print(e)
            isError = True
            return render_template("signup.html", isError=isError)

    return render_template("signup.html")


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchQuery = request.form['search']
        posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        final_posts = []
        for post in posts:

            if searchQuery in post.title:
                final_posts.append(post)
                # print(final_posts)
                # print(str(posts.index(post)))

        if isLogged():
            user = "Logged As " + session['user']
        else:
            user = ""

        return render_template('posts.html',
                               posts=final_posts, isAdmin=isAdmin(), isLogged=isLogged(), user=user, inSearchMode=True)

    return redirect("/posts")


def isLogged():

    if 'user' in session:
        return True
    else:
        return False


def isAdmin():
    if isLogged():
        if session['user'] == 'admin':
            return True
        else:
            return False
    else:
        return False

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000, use_reloader=True)
