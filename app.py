from flask import Flask, request
import requests
from flask_cors import CORS
from flask import jsonify
from caller import find_activities_by_type, generate_story_text


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

@app.route("/hello_world", methods=["GET"])
def hello_world():
    """
    A simple endpoint that returns 'Hello World'.

    This is used for essentially testing that the server is online and working!

    The HTML site using Ping Server button will access this endpoint or you can navigate to a
    browser and type in the URL to see the response.
    """
    return "Hello World"


@app.route("/get-activities/<int:count>", methods=["GET"])
def get_activities(count):
    """
    Endpoint to fetch a list of activities based on the specified activity type.
    The route parameter 'count' specifies the number of unique activities desired.

    Should return a jsonified list of activities.
    """

    try:
        response = requests.get('http://www.boredapi.com/api/activity/')
        activity_data = response.json()
        activity_type = activity_data.get("type")
        activities = find_activities_by_type(activity_type, count)

        return jsonify(list(activities)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-story", methods=["POST"])
def generate_story():
    """
    Endpoint to generate a story based on specified attributes: 'name', 'product_id', and optional 'story_starter' and 'activity_type'.
    The activity_type could contain an activity or an empty string.
    """
    try: 
        data = request.get_json()
        activity_type = data.get('activity_type', '')
        name = data.get('name')
        product_id = data.get('product_id')
        story_starter = data.get('story_starter', '')

        if not name or not product_id:
            return jsonify({"error": "Name and product ID are required."}), 400

        story = generate_story_text(activity_type, name, product_id, story_starter)
        return story, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)