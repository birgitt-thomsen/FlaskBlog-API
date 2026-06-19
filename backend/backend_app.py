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


def find_post_by_id(post_id):
    """ Find the post with the id `post_id`. If there is no post with this
    id, return None."""
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


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


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes the user selected post from the database and returns
    success message. Returns error message when post id does not exist.
    """
    # Find the book with the given ID
    post = find_post_by_id(post_id)

    # If the book wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id '{post_id}' not found"}), 404

    # Remove the post from the list
    POSTS.remove(post)

    # Return success message
    return (jsonify({"message": f"Post with id '{post_id}' has been "
                                "successfully deleted."}),200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
