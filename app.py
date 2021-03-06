from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "abc"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_blog.db'
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.Date, nullable=False,
                            default=datetime.now().date())
    likes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return 'Blog post ' + str(self.id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Username :' + str(self.id)



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
        db.session.add(new_post)

        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        if isLogged():
            user = "Logged As " + session['user']
        else:
            user = ""

        return render_template('posts.html', posts=all_posts,
                               isAdmin=isAdmin(), isLogged=isLogged(), user=user,inSearchMode=False)


@app.route('/posts/delete/<int:id>')
def delete(id):
    if isAdmin():
        post = BlogPost.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return redirect('/posts')
    else:
        return redirect('/posts')


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if isAdmin():
        post = BlogPost.query.get_or_404(id)

        if request.method == 'POST':
            post.title = request.form['title']
            post.author = request.form['author']
            post.content = request.form['content']
            db.session.commit()
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
    users = User.query.all()
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


@app.route('/posts/like/<int:id>')
def like(id):
    post = BlogPost.query.get_or_404(id)
    post.likes += 1
    db.session.commit()
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
            db.session.add(usr)
            db.session.commit()
            # print(User.query.all())

            session.pop("user", None)
            session['user'] = username.lower()

            return redirect("/posts")
        except sqlalchemy.exc.IntegrityError:
            isError = True
            db.session.rollback()
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
