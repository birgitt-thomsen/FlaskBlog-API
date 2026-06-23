let currentPosts = [];
let editingPostId = null;

// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
};

// Display posts on the page
function displayPosts(data) {

    currentPosts = data;

    const postContainer = document.getElementById('post-container');
    postContainer.innerHTML = '';

    data.forEach(post => {

        const postDiv = document.createElement('div');
        postDiv.className = 'post';

        postDiv.innerHTML = `
            <h2>${post.title}</h2>
            <p><em>By ${post.author} on ${post.date}</em></p>
            <p>${post.content}</p>
            <button onclick="editPost(${post.id})">Edit</button>
            <button onclick="deletePost(${post.id})">Delete</button>
        `;

        postContainer.appendChild(postDiv);
    });
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(baseUrl + '/posts')
         // Parse the JSON data from the response
        .then(response => response.json())
        .then(data => displayPosts(data))
        .catch(error => console.error('Error:', error));
}

// Search posts by title, content, author or date
function searchPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var searchValue = document.getElementById('search-value').value.trim();
    var searchField = document.getElementById('search-field').value;

    if (!searchValue) {
        loadPosts();
        return;
    }

    fetch(
        baseUrl +
        '/posts/search?' +
        searchField +
        '=' +
        encodeURIComponent(searchValue)
    )
    .then(response => response.json())
    .then(data => displayPosts(data))
    .catch(error => console.error('Error:', error));
}

// Function to send a POST request to the API to add a new post
function addPost() {

    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    const postData = {
        title: postTitle,
        content: postContent,
        author: postAuthor
    };

    // UPDATE existing post
    if (editingPostId !== null) {

        fetch(baseUrl + '/posts/' + editingPostId, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(data => {
            cancelEdit();
            loadPosts();
        });

    }

    // CREATE new post
    else {

        fetch(baseUrl + '/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(post => {

            document.getElementById('post-title').value = '';
            document.getElementById('post-content').value = '';
            document.getElementById('post-author').value = '';

            loadPosts();
        });
    }
}

// Function to allow sorting the posts
function sortPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var sortField = document.getElementById('sort-field').value;
    var direction = document.getElementById('sort-direction').value;

    var url = baseUrl +
              '/posts?sort=' +
              sortField +
              '&direction=' +
              direction;

    fetch(url)
        .then(response => response.json())
        .then(data => displayPosts(data))
        .catch(error => console.error('Error:', error));
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    if (!confirm("Are you sure you want to delete this post?")) {
        return;
    }
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts();// Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));
}

function editPost(postId) {

    const post = currentPosts.find(post => post.id === postId);

    if (!post) {
        return;
    }

    document.getElementById('post-title').value = post.title;
    document.getElementById('post-content').value = post.content;
    document.getElementById('post-author').value = post.author;

    editingPostId = postId;

    document.getElementById('submit-button').innerText = "Update Post";
    document.getElementById('cancel-button').style.display = "inline";
}

function cancelEdit() {

    editingPostId = null;

    document.getElementById('post-title').value = '';
    document.getElementById('post-content').value = '';
    document.getElementById('post-author').value = '';

    document.getElementById('submit-button').innerText = "Add Post";

    document.getElementById('cancel-button').style.display = "none";
}
