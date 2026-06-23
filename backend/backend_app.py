""" Module handles backend flask routing to navigate the blog application. """

import json
import os
from datetime import datetime
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'data.json')

def load_posts():
    """
    Loads the json data file. Saves an empty file when no json file exists
    or the existing file is invalid. If invalid, it prints an error message.
    """
    try:
        with open(DATA_FILE, encoding='utf-8') as file:
            return json.load(file)

    except FileNotFoundError:
        save_posts([])
        return []

    except json.JSONDecodeError:
        print(f"WARNING: '{DATA_FILE}' is invalid, recreating empty database.")
        save_posts([])
        return []


def save_posts(posts):
    """ Saves posts to the json file. """
    with open(DATA_FILE, "w", encoding='utf-8') as file:
        json.dump(posts, file, indent=4)


def validate_post_data(data):
    """ Takes the POST input data and returns any missing fields. """
    required_fields = ["title", "content", "author"]

    missing_fields = [
        field for field in required_fields
        if field not in data or not data[field]
    ]
    return missing_fields


def find_post_by_id(posts, post_id):
    """
    Finds the post with the id `post_id`. If there is no post with this
    id, return None.
    """
    for post in posts:
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
    posts = load_posts()

    # return jsonify(POSTS)
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    results = posts.copy()

    if sort_field:
        if sort_field not in ["title", "content", "author", "date"]:
            return jsonify({
                "error": "sort field must be 'title', 'content', 'author' or 'date'."
            }), 400

        if sort_field == "date":
            results = sorted(
                results,
                key=lambda post: datetime.strptime(post["date"], "%Y-%m-%d"),
                reverse=(direction.lower() == "desc")
            )
        else:
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
    posts = load_posts()
    data = request.get_json()

    missing_fields = validate_post_data(data)

    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: "
                     f"{', '.join(missing_fields)}"
        }), 400

    next_id = max(post["id"] for post in posts) + 1 if posts else 1

    new_post = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"],
        "author": data["author"],
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    # Add new post to the list and save
    posts.append(new_post)
    save_posts(posts)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes the selected post from the database and returns a
    success message. Returns error message when post id does not exist.
    """
    posts = load_posts()

    # Find the post with the given ID
    post = find_post_by_id(posts, post_id)

    # If post not found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id '{post_id}' not found."}), 404

    # Remove the post from the list and save
    posts.remove(post)
    save_posts(posts)

    # Return success message
    return (jsonify({"message": f"Post with id '{post_id}' has been "
                                "deleted successfully."}),200)


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates a post and returns success message. Returns error message when
    post cannot be found or no update data was provided.
    """
    posts = load_posts()

    # Find the post with the given ID
    post = find_post_by_id(posts, post_id)

    # If post not found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id '{post_id}' not found."}), 404

    data = request.get_json()

    # Check if data was submitted
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Update post fields
    if "title" in data:
        post["title"] = data["title"]

    if "content" in data:
        post["content"] = data["content"]

    if "author" in data:
        post["author"] = data["author"]

    save_posts(posts)

    # Return success message
    return (jsonify({"message": f"Post with id '{post_id}' has been "
                                "updated successfully."}), 200)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Returns a list of all posts with title or content that matches the
    user's search input. Returns an empty list when no matches are found.
    """
    posts = load_posts()

    title = request.args.get("title")
    content = request.args.get("content")
    author = request.args.get("author")
    date = request.args.get("date")

    results = posts

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

    if author:
        results = [
            post for post in results
            if author.lower() in post["author"].lower()
        ]

    if date:
        try:
            search_date = datetime.strptime(date, "%Y-%m-%d").date()
            results = [
                post for post in results
                if datetime.strptime(post["date"],
                                     "%Y-%m-%d").date() == search_date
            ]
        except ValueError:
            return jsonify({
                "error": "Invalid date format. Use YYYY-MM-DD"
            }), 400

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
