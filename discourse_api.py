# Core packages
import re
import requests
import time


class DiscourseAPI:
    _errors = []

    def __init__(self, url, username, key, category_name):
        self.url = url
        self.username = username
        self.key = key

        print(f"- Getting ID for category {category_name}")
        category_info = requests.get(f"{self.url}/c/{category_name}/show.json")
        self.category = category_info.json()["category"]
        print(f"  > ID: {self.category['id']}")

    def get_category_topics(self):
        """
        Get all topics in the chosen category
        """

        category_data = requests.get(
            f"{self.url}/c/{self.category['id']}.json"
        )
        return category_data.json()["topic_list"]["topics"]

    def get_topic_markdown(self, topic_id):
        """
        Given a topic_id, get the markdown in the top post
        """

        post = self._get_post_from_topic(topic_id)

        return post["raw"]

    def create_topic(self, title, markdown):
        """
        Create a new topic
        """

        return self._call_api(
            message=(
                f"creating topic '{title}'' "
                f"in category '{self.category['name']}'"
            ),
            method=requests.post,
            url_path=f"/posts.json",
            extra_data={
                "title": title,
                "raw": markdown,
                "category": self.category["id"],
            },
        )

    def delete_topic(self, id):
        """
        Delete a topic by its ID
        """

        return self._call_api(
            message=(
                f"deleting topic {id} in category '{self.category['name']}'"
            ),
            method=requests.delete,
            url_path=f"/t/{id}.json",
        )

    def update_topic_content(self, topic_id, markdown):
        """
        Update raw Markdown content in the specified post
        """

        post = self._get_post_from_topic(topic_id)

        return self._call_api(
            message=f"updating markdown in post {post['id']}",
            method=requests.put,
            url_path=f"/posts/{post['id']}.json",
            extra_data={"post[raw]": markdown},
        )

    def convert_topic_to_wiki(self, topic_id):
        """
        Convert topic to wiki
        """

        post = self._get_post_from_topic(topic_id)

        return self._call_api(
            message=f"converting post {post['id']} in topic {topic_id} to Wiki",
            method=requests.put,
            url_path=f"/posts/{post['id']}/wiki",
            extra_data={"wiki": True},
        )

    def print_errors(self):
        """
        Print any errors encountered in the API so far
        """

        if self._errors:
            print("Errors:")
            for error in self._errors:
                print(error)

        return self._errors

    # Private methods
    # ===

    def _call_api(self, message, method, url_path, extra_data={}):
        """
        Call the Discourse API
        - request_callback: e.g. requests.get
        """

        response = None
        data = {"api_key": self.key, "api_username": self.username}

        data.update(extra_data)

        while response is None or response.status_code == 429:
            if response is not None and response.status_code == 429:
                seconds = 5
                error_message = response.json()["errors"][0]
                seconds_match = re.search("wait (\d+) seconds", error_message)

                if seconds_match:
                    seconds = int(seconds_match.groups()[0]) + 1

                print(
                    f"  > 429 from API, waiting {seconds} seconds ... "
                    f"('{response.json()['errors']}')"
                )
                time.sleep(seconds)

            print(f"  > {message[0].upper()}{message[1:]} ...")
            response = method(self.url + url_path, data=data)

        if response.ok:
            print(f"  > Success {message}")
        else:
            error_message = (
                f"Error {response.status_code} {message}: "
                f"{response.json()['errors']}"
            )
            print(f"  > {error_message}")
            self._errors.append(error_message)

        return response

    def _get_post_from_topic(self, topic_id):
        """
        Given a topic ID, get the data about the first post
        """

        get_response = requests.get(
            f"{self.url}/t/{topic_id}.json?include_raw=1"
        )
        return get_response.json()["post_stream"]["posts"][0]
