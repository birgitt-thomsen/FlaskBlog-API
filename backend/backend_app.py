from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_post_data(data):
    """ Returns True if post data is valid, False otherwise. """
    if "title" not in data or "content" not in data:
        return False
    return True


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """ Returns a list of all posts. """
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """ Adds a new post to the database, returns an error message if the
    post data is incomplete. """
    data = request.get_json()

    if not validate_post_data(data):
        return jsonify({"error": "Invalid post data"}), 400

    next_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
