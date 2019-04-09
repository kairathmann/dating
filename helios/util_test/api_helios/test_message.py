# # -*- coding: utf-8 -*-
#
# import json, requests
#
# from silo_user.user.db import User
# from util_test.base import get_url, create_test_user, login_test_user
# from util_test.database import flush_database
#
#
# def test_create():
#
#     flush_database()
#
#     result = create_test_user()
#
#     assert result['success'] is True
#
#
# def test_login():
#
#
#     s = requests.Session()
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.Login'),
#
#         data = {
#
#             'email': 'test@example.com',
#             'password': '12345678'
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#
# def test_update_pass():
#
#     s, viewer_hid = login_test_user()
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.UpdatePass'),
#
#         data = {
#
#             'target_hid': viewer_hid,
#             'old_password': '12345678',
#             'new_password': '87654321'
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     # Reset the password to the default value so that further unit tests work
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.UpdatePass'),
#
#         data = {
#
#             'target_hid': viewer_hid,
#             'old_password': '87654321',
#             'new_password': '12345678'
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#
# def test_update_profile():
#
#     s, viewer_hid = login_test_user()
#
#     new_first_name = 'NewName'
#     new_tagline = 'New Tagline'
#     new_bio = 'New Bio'
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.UpdateProfile'),
#
#         data = {
#
#             'target_hid': viewer_hid,
#             'first_name': new_first_name,
#             'tagline': new_tagline,
#             'bio': new_bio
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     # Verify all of the row's columns have been correctly updated by fetching the User
#     # record directly from the database
#
#     user = User.objects.filter(email='test@example.com').first()
#
#     assert user.first_name == new_first_name
#     assert user.tagline == new_tagline
#     assert user.bio == new_bio
#
#
# def test_retrieve_single():
#
#     s, viewer_hid = login_test_user()
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.RetrieveSingle'),
#
#         data = {
#
#             'target_hid': viewer_hid
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     assert result['data']['bio'] == 'New Bio'
#     assert result['data']['first_name'] == 'NewName'
#     assert result['data']['viewer_hid'] == viewer_hid
#     assert result['data']['target_hid'] == viewer_hid
#     assert result['data']['tagline'] == 'New Tagline'
#     assert result['data']['avatar_url'] == 'hydra/img/src/user/avatar_7.jpg'
#
#
# def test_retrieve_edit():
#
#     s, viewer_hid = login_test_user()
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.RetrieveEdit'),
#
#         data = {
#
#             'target_hid': viewer_hid
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     assert result['data']['bio'] == 'New Bio'
#     assert result['data']['first_name'] == 'NewName'
#     assert result['data']['viewer_hid'] == viewer_hid
#     assert result['data']['target_hid'] == viewer_hid
#     assert result['data']['tagline'] == 'New Tagline'
#     assert result['data']['avatar_url'] == 'hydra/img/src/user/avatar_7.jpg'
#     assert result['data']['email'] == 'test@example.com'
#
#
# def test_avatar():
#
#     s, viewer_hid = login_test_user()
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.AvatarStash'),
#
#         files = {
#
#             'image': open('/srv/luna/helios/util_test/assets/nasa_moon.jpg', 'rb')
#         },
#
#         data = {
#
#             'target_hid': viewer_hid,
#             'resize_width': 600,
#             'resize_height': 600,
#             'mode': 'avatar'
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     assert result['data']['x'] == 600
#     assert result['data']['y'] == 600
#     assert len(result['data']['image']) > 0
#     assert len(result['data']['guid']) > 0
#     assert 0.0 < float(result['data']['min_crop_x']) < 1.0
#     assert 0.0 < float(result['data']['min_crop_y']) < 1.0
#
#
#     result = json.loads(s.post(
#
#         url = get_url('ApiHelios.User.AvatarCrop'),
#
#         data = {
#
#             'target_hid': viewer_hid,
#             'stash_guid': result['data']['guid'],
#             'x1': 10,
#             'y1': 10,
#             'x2': 590,
#             'y2': 590,
#         }
#
#     ).text)
#
#     assert result['success'] is True
#
#     assert len(result['data']['avatar_url']) > 0
