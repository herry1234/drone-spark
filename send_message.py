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
    roomid = os.environ.get("PLUGIN_ROOMID")
    roomname = os.environ.get("PLUGIN_ROOMNAME")


    # If an explict roomId was provided as a varg, verify it's a valid roomId
    if roomid:
        if verify_roomId(roomid):
            return roomid
    # If a roomName is provided, send to room with that title
    elif roomname:
        # Try to find room based on room name
        response = requests.get(
            spark_urls["rooms"],
            headers=spark_headers
        )
        rooms = response.json()["items"]
        # print("Number Rooms: " + str(len(rooms)))
        for room in rooms:
            # print("Room: " + room["title"])
            if roomname == room["title"]:
                return room["id"]

    # If no valid roomId could be found, raise error
    raise(
        LookupError("roomId can't be determined"))


def verify_roomId(roomId):
    '''
    Check if the roomId provided is valid
    '''
    url = "%s/%s" % (spark_urls["rooms"], roomId)

    response = requests.get(
        url,
        headers=spark_headers
    )

    if response.status_code == 200:
        return True
    else:
        return False


def standard_message():
    '''
    This will create a standard notification message.
    '''
    status = os.environ.get("PLUGIN_BUILD_STATUS")
    repo_fullname = os.environ.get("PLUGIN_REPO_FULL_NAME")
    author = os.environ.get("PLUGIN_BUILD_AUTHOR")
    author_email = os.environ.get("PLUGIN_BUILD_AUTHOR_EMAIL")
    url = os.environ.get("PLUGIN_SYSTEM_LINK_URL")
    fullname = os.environ.get("PLUGIN_REPO_FULL_NAME")
    build_number = os.environ.get("PLUGIN_BUILD_NUMBER")
    build_link = os.environ.get("PLUGIN_BUILD_LINK_URL")
    build_branch = os.environ.get("PLUGIN_BUILD_BRANCH")
    build_event = os.environ.get("PLUGIN_BUILD_EVENT")
    build_msg = os.environ.get("PLUGIN_BUILD_MESSAGE")
    if status == "success":
        message = "##Build for %s is Successful \n" % (
            repo_fullname)
        message = message + "**Build author:** [%s](%s) \n" % (
            author, author_email)
    else:
        message = "#Build for %s FAILED!!! \n" % (
            repo_fullname)
        message = message + "**Drone blames build author:** [%s](%s) \n" % (
            author, author_email)

    message = message + "###Build Details \n"
    message = message + \
        "* [Build Log](%s/%s/%s)\n" % (url, fullname, build_number)
    message = message + \
        "* [Commit Log](%s)\n" % (build_link)
    message = message + \
        "* **Branch:** %s\n" % (build_branch)
    message = message + \
        "* **Event:** %s\n" % (build_event)
    message = message + \
        "* **Commit Message:** %s\n" % (build_msg)

    return message


def send_message(message_data, message_text):

    message_data["markdown"] = message_text

    response = requests.post(
        spark_urls["messages"],
        headers=spark_headers,
        json=message_data
    )

    return response


def main():
    token = os.environ.get("PLUGIN_AUTH_TOKEN")
    if token is None:
        raise(LookupError(
            "Requires valid PLUGIN_AUTH_TOKEN to be provided."))

    # Prepare headers and message objects
    spark_headers["Authorization"] = "Bearer %s" % (token)
    spark_message = {}

    # Determine destination for message
    try:
        # First look for a valid roomId or roomName
        spark_message["roomId"] = get_roomId()
    except LookupError:
        raise(LookupError(
            "Requires valid roomId, roomName, or personEmail to be provided.  "))
        # Send Standard message
    standard_notify = send_message(spark_message, standard_message())
    if standard_notify.status_code != 200:
        print(
            standard_notify.json()["message"])
        raise(
            SystemExit("Something went wrong..."))

if __name__ == "__main__":
    main()
