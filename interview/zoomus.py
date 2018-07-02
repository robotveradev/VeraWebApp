import requests
import jwt
import time
import json


class ZoomusApi(object):
    def __init__(self, api_key, api_secret, user_id, ttl=30):
        self.api_key = api_key
        self.api_secret = api_secret

        self.__api_root = 'https://api.zoom.us/v2/'
        self.__schedule = 'users/{0}/meetings'.format(user_id)
        self.__meeting = 'meetings/{meetingId}'

        self.ttl = ttl

    def get_token(self):
        now = int(time.time())
        return jwt.encode({'iss': self.api_key, 'exp': now + self.ttl}, self.api_secret, algorithm='HS256').decode(
            "utf-8")

    def get_header(self):
        return {'Content-type': 'application/json', "Authorization": "Bearer " + self.get_token()}

    def schedule_meeting(self, topic=None, start_time=None, duration=None, timezone=None):
        """
        Schedule new meeting
        :param topic: Topic name
        :param start_time: start meeting time
        :param duration: meeting duration in minutes
        :param timezone: Timezone
        :return: json meeting object
        Valid response: 201 Created
        """
        if topic and start_time and duration and timezone:
            data = {'topic': topic, 'start_time': start_time, 'duration': duration, 'timezone': timezone, 'type': 2}
            return requests.post(self.__api_root + self.__schedule, data=json.dumps(data), headers=self.get_header())
        else:
            raise ValueError

    def get_meetings(self):
        """
        Get all user meetings
        :return: json meeting objects array
        Valid response: 200 OK
        """
        return requests.get(self.__api_root + self.__schedule, headers=self.get_header())

    def get_meeting(self, meeting_id):
        """
        Return meeting object by meeting id
        :param meeting_id:
        :return: json meeting object
        Valid response: 200 OK
        """
        if not meeting_id:
            raise ValueError
        return requests.get(self.__api_root + self.__meeting.format(meetingId=meeting_id), headers=self.get_header())

    def update_meeting(self, meeting_id, topic=None, start_time=None, duration=None, timezone=None):
        """
        Update existing meeting by new value(s)
        :param meeting_id: meeting id to be updated
        :param topic: Topic name
        :param start_time: start meeting time
        :param duration: meeting duration in minutes
        :param timezone: Timezone
        :return: None
        Valid response 204 No Content
        """
        if not meeting_id:
            raise ValueError
        if not topic and not start_time and not duration and timezone:
            raise ValueError
        data = {}
        if topic:
            data['topic'] = topic
        if start_time:
            data['start_time'] = start_time
        if duration:
            data['duration'] = duration
        if timezone:
            data['timezone'] = timezone
        return requests.patch(self.__api_root + self.__meeting.format(meetingId=meeting_id), data=json.dumps(data),
                              headers=self.get_header())

    def delete_meeting(self, meeting_id):
        """
        Delete existing meeting
        :param meeting_id:
        :return: None
        Valid response 204 No Content
        """
        if not meeting_id:
            raise ValueError
        return requests.delete(self.__api_root + self.__meeting.format(meetingId=meeting_id), headers=self.get_header())
