#!/usr/bin/env python
'''
This is the Python Code for a drone.io plugin to send messages using Cisco Spark
'''

import requests
import os

spark_urls = {
    "messages": "https://api.ciscospark.com/v1/messages",
    "rooms": "https://api.ciscospark.com/v1/rooms",
    "people": "https://api.ciscospark.com/v1/people"
}

spark_headers = {}
spark_headers["Content-type"] = "application/json"

def get_roomId():
    '''
    Determine the roomId to send the message to.
    '''

    # If an explict roomId was provided as a varg, verify it's a valid roomId
    if os.environ["plugin_roomId"]:
        if verify_roomId(os.environ["plugin_roomId"]):
            return os.environ["plugin_roomId"]
    # If a roomName is provided, send to room with that title
    elif os.environ["plugin_roomName"]:
        # Try to find room based on room name
        response = requests.get(
            spark_urls["rooms"],
            headers = spark_headers
        )
        rooms = response.json()["items"]
        #print("Number Rooms: " + str(len(rooms)))
        for room in rooms:
            #print("Room: " + room["title"])
            if os.environ["plugin_roomName"] == room["title"]:
                return room["id"]

    # If no valid roomId could be found, raise error
    raise(LookupError("roomId can't be determined"))

def verify_roomId(roomId):
    '''
    Check if the roomId provided is valid
    '''
    url = "%s/%s" % (spark_urls["rooms"], roomId)

    response = requests.get(
        url,
        headers = spark_headers
    )

    if response.status_code == 200:
        return True
    else:
        return False

def standard_message():
    '''
    This will create a standard notification message.
    '''
    status = os.environ["plugin_build_status"]
    if status == "success":
        message = "##Build for %s is Successful \n" % (os.environ["plugin_repo_full_name"])
        message = message + "**Build author:** [%s](%s) \n" % (os.environ["plugin_build_author"], os.environ["plugin_plugin_build_author_email"])
    else:
        message = "#Build for %s FAILED!!! \n" % (os.environ["plugin_repo_full_name"])
        message = message + "**Drone blames build author:** [%s](%s) \n" % (os.environ["plugin_build_author"], os.environ["plugin_build_author_email"])

    message = message + "###Build Details \n"
    message = message + "* [Build Log](%s/%s/%s)\n" % (os.environ["plugin_system_link_url"], os.environ["plugin_repo_full_name"], os.environ["plugin_build_number"])
    message = message + "* [Commit Log](%s)\n" % (os.environ["plugin_build_link_url"])
    message = message + "* **Branch:** %s\n" % (os.environ["plugin_build_branch"])
    message = message + "* **Event:** %s\n" % (os.environ["plugin_build_event"])
    message = message + "* **Commit Message:** %s\n" % (os.environ["plugin_build_message"])

    return message

def send_message(message_data, message_text):

    message_data["markdown"] = message_text

    response = requests.post(
        spark_urls["messages"],
        headers = spark_headers,
        json = message_data
    )

    return response

def main():

    # Prepare headers and message objects
    spark_headers["Authorization"] = "Bearer %s" % (os.environ["plugin_auth_token"])
    spark_message = {}

    # Determine destination for message
    try:
        # First look for a valid roomId or roomName
        roomId = get_roomId()
        spark_message["roomId"] = roomId
    except LookupError:
        # See if a personEmail was provided
        if os.environ["plugin_auth_token"]:
            spark_message["toPersonEmail"] = os.environ["plugin_auth_token"]
        else:
            raise(LookupError("Requires valid roomId, roomName, or personEmail to be provided.  "))

    # Send Standard message
    standard_notify = send_message(spark_message, standard_message())
    if standard_notify.status_code != 200:
        print(standard_notify.json()["message"])
        raise(SystemExit("Something went wrong..."))

if __name__ == "__main__":
    main()
