from flask import Flask ,render_template

app = Flask(__name__)

posts = [
        {
            "title":"Blog Post 1",
            "author":"Gowtham",
            "content":'''
Hello This Is The Content Of Blog Post One ( 1 )
'''
        },
        {
            "title":"Blog Post 2",
            "author":"Gowtham",
            "content":'''
Hello This Is The Content Of Blog Post One ( 1 )
'''
        }
        ]

@app.route("/")
def home():
    return render_template("index.html",posts=posts)

if __name__ == "__main__":
    app.run(debug=True)
