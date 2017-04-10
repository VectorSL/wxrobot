# -*- coding:utf-8 -*-
import itchat
import os
import re
import shutil
import time
import requests
import hashlib
import numpy as np
def get_response(msg, FromUserName):
    api_url = 'http://www.tuling123.com/openapi/api'
    apikey = '26be1b76152941d2bcc2b72af85ab5e0'
    # data中有userid才能实现上下文一致的聊天效果。
    hash = hashlib.md5()
    userid = hash.update(FromUserName.encode('utf-8'))
    data = {'key': apikey,
            'info': msg,
            'userid': userid
            }
    try:
        req = requests.post(api_url, data=data).json()
        return req.get('text')
    except:
        return
msg_dict={}
def ClearTimeOutMsg():
	if msg_dict.__len__()>0:
		for msgid in list(msg_dict):
			if time.time()-msg_dict.get(msgid,None)['msg_time']>130.0:
				item=msg_dict.pop(msgid)
def anti_revocation(msg):
	mytime = time.localtime()
	msg_id=msg['MsgId']
	msg_time = msg['CreateTime']
	msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
	msg_type = msg['Type']
	msg_content = None
	msg_url = None
	if msg['Type'] == 'Text':
		msg_content = msg['Text']
	elif msg['Type'] == 'Sharing':
		msg_content = msg['Text']
		msg_url = msg['Url']
	elif msg['Type'] == 'Picture':
		msg_content = msg['FileName']
		msg['Text'](msg['FileName'])
	elif msg['Type'] == 'Video':
		msg_content = msg['FileName']
		msg['Text'](msg['FileName'])
	elif msg['Type'] == 'Recording':
		msg_content = msg['FileName']
		msg['Text'](msg['FileName'])
	msg_dict.update(
		{msg_id: {"msg_from": msg_from, "msg_time": msg_time, "msg_time_touser": mytime, "msg_type": msg_type,
                  "msg_content": msg_content, "msg_url": msg_url}})
	ClearTimeOutMsg()
@itchat.msg_register(['Note'])
def SaveMsg(msg):
	if not os.path.exists('./Revocation/'):
		os.mkdir('Revocation/')
	if re.search('replacemsg', msg['Content'])!= None:
		old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
		old_msg = msg_dict.get(old_msg_id, {})
		msg_send=old_msg.get('msg_from',None)+' revocation a'+old_msg['msg_type']+':'+old_msg.get('msg_content', None)
	if old_msg['msg_type'] == 'Sharing':
		msg_send +=old_msg.get('msg_url',None)
	elif old_msg['msg_type'] == 'Picture' \
                or old_msg['msg_type'] == 'Recording' \
                or old_msg['msg_type'] == 'Video' \
                or old_msg['msg_type'] == 'Attachment':
			shutil.move(old_msg['msg_content'],'./Revocation/')
	itchat.send(msg_send,toUserName='filehelper')
	msg_dict.pop(old_msg_id)
	ClearTimeOutMsg()
itchat.auto_login(hotReload=True)
#signal 为控制信号 可以随时启/停 Robot 而不必关程序。
global signal
signal = True
@itchat.msg_register(['Text', 'Map','Card', 'Sharing'])
def Tuling_robot(msg):
	anti_revocation(msg)
	global signal
	if msg['Content'] == 'stop':
		signal = False
	elif msg['Content'] == 'startsl':
		signal = True
	if signal:
		respones = get_response(msg['Content'], msg['FromUserName'])
		itchat.send(respones, msg['FromUserName'])
	print msg['FromUserName'],msg['Content']
@itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'])
def reply_biaoqingbao(msg):
	anti_revocation(msg)
	if signal:
		pic= os.listdir('./pics/')
		itchat.send_image('pics/'+pic[np.random.randint(1, len(pic))], msg['FromUserName'])
itchat.run()