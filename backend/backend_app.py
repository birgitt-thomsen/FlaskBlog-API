from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_post_data(data):
    """ Takes the POST data and returns missing fields. """
    required_fields = ["title", "content"]

    missing_fields = [
        field for field in required_fields
        if field not in data or not data[field]
    ]
    return missing_fields


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """ Returns a list of all posts. """
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """ Adds a new post to the database, returns an error message if the
    post data is incomplete. """
    data = request.get_json()

    missing_fields = validate_post_data(data)

    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: "
                     f"{", ".join(missing_fields)}"
        }), 400

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
