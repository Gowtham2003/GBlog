from flask import Flask ,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
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
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
            return 'Blog post ' + str(self.id)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(20),nullable=False)
    
    def __repr__(self):
        return 'Username :' + str(self.id)
    


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/posts" , methods=['GET', 'POST'])
def posts():
    isAdmin = False
    isLogged = False
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)

        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        if 'user' in session:
            isLogged = True
            if session['user'] == 'admin':
                isAdmin = True
            else:
                isAdmin = False
        else:
            isLogged = False


        return render_template('posts.html', posts=all_posts,isAdmin=isAdmin,isLogged=isLogged)

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post=post)

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop("user",None)
        username = request.form['username']
        password = request.form['password']
        if valid(username,password):
            session['user'] = username

            return redirect("/posts")
        else:
            return render_template("login.html")

    return render_template("login.html")


def valid(username,password):
    users = User.query.all()
    for user in users:
        if ( user.username == username) and (user.password ==password):
            return True
        else:
            return False


@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('new_post.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect("/posts")





if __name__ == "__main__":
    app.run(debug=True)
