#  -*- coding: UTF8 -*-

import newrelic.agent
import boto3
import uuid
from django.conf import settings
from api_helios.base import AbstractHeliosEndpoint

class BubbleCreateLink(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Creates a new pre-signed url to S3

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "presignedUrl": "https://s3-bucket-address.aws-something.com/videos/userhid/video-uuid4-name.mp4"},
                    "success": true
                }
        """


        upstream = self.get_upstream_for_platform(request)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        try:
            s3 = boto3.client('s3')
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': settings.BUCKET_NAME,
                    'Key': 'video/' + request.user.hid + '/' + str(uuid.uuid4()) + '.mp4',
                    'ACL': 'public-read',
                },
                ExpiresIn= 600
            )
        except:
            return self.render_error(request, code='not_possible_to_create_presigned_url', status=400)


        return self.render_response(

            request=request,

            data={
                'presigned_url': url,
            }
        )
