""" Module handles backend flask routing to navigate the blog application. """

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'FlaskBlog-API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_post_data(data):
    """ Takes the POST input data and returns any missing fields. """
    required_fields = ["title", "content"]

    missing_fields = [
        field for field in required_fields
        if field not in data or not data[field]
    ]
    return missing_fields


def find_post_by_id(post_id):
    """
    Finds the post with the id `post_id`. If there is no post with this
    id, return None.
    """
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Returns a list of all posts and allows user to sort by either title
    or content. Ascending order is default unless user specifies descending
    order. Returns an error message when sort field is invalid.
    """

    # return jsonify(POSTS)
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    results = POSTS.copy()

    if sort_field:
        if sort_field not in ["title", "content"]:
            return jsonify({
                "error": "sort field must be 'title' or 'content'."
            }), 400

        results = sorted(
            results,
            key=lambda post: post[sort_field].lower(),
            reverse=(direction.lower() == "desc")
        )

    return jsonify(results), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Adds a new post to the database, returns an error message if the
    post data is incomplete.
    """
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
    Deletes the selected post from the database and returns a
    success message. Returns error message when post id does not exist.
    """
    # Find the post with the given ID
    post = find_post_by_id(post_id)

    # If post not found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id '{post_id}' not found."}), 404

    # Remove the post from the list
    POSTS.remove(post)

    # Return success message
    return (jsonify({"message": f"Post with id '{post_id}' has been "
                                "deleted successfully."}),200)


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates a post and returns success message. Returns error message when
    post cannot be found or no update data was provided.
    """
    # Find the post with the given ID
    post = find_post_by_id(post_id)

    # If post not found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id '{post_id}' not found."}), 404

    data = request.get_json()

    # Check if data was submitted
    if not data:
        return jsonify({
            "error": "No update data provided"
        }), 400

    # Update post fields
    if "title" in data:
        post["title"] = data["title"]

    if "content" in data:
        post["content"] = data["content"]

    # Return success message
    return (jsonify({"message": f"Post with id '{post_id}' has been "
                                "updated successfully."}), 200)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Returns a list of all posts with title or content that matches the
    user's search input. Returns an empty list when no matches are found.
    """
    title = request.args.get("title")
    content = request.args.get("content")

    results = POSTS

    if title:
        results = [
            post for post in results
            if title.lower() in post["title"].lower()
        ]

    if content:
        results = [
            post for post in results
            if content.lower() in post["content"].lower()
        ]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
