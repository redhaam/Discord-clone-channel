import asyncio
from datetime import datetime
from urllib.request import Request, urlopen
from io import BytesIO
import json
import os
import sys
import aiohttp
from discord import Webhook, AsyncWebhookAdapter, File, Embed
from types import SimpleNamespace

from discord.mentions import AllowedMentions


def load_config():
    global config
    if not os.path.isfile("config.json"):
        sys.exit("'config.json' not found! Please add it and try again.")
    else:
        config = loads_to_object("config.json")
    return config


async def create_webhook(webhook_url):  
    session= aiohttp.ClientSession()
    return Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))

async def send_webhook(webhook,message):
    files = resolve_files(get_files(message))
    embeds= resolve_embeds(get_embeds(message))
    append_date_footer(embeds, message['timestamp'])
    allowed_mentions= AllowedMentions()
    return await webhook.send(content=message['content'],username=get_username_dislay(message['author']),avatar_url=message['author']['avatarUrl'],files=files,embeds=embeds,allowed_mentions=allowed_mentions,wait=True)

def read_file_url(url) -> BytesIO:
    req=Request(url, headers={'User-Agent' : "Magic Browser"})
    f= urlopen(req)
    data= f.read()
    return BytesIO(data)

def resolve_embeds(embeds):
    attach =[]
    for em in embeds:
        if 'color' in em:
            em.pop('color')
        attach.append( Embed.from_dict(em))
    return attach

def append_date_footer(embeds:list, date):
    try:
        date=datetime.strptime(date,'%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        date= datetime.fromisoformat(date)
    date_time = date.strftime("%d/%m/%Y, %H:%M:%S")
    embeds.append(Embed(description= date_time))

def resolve_files(files):
    attachements= []
    for f in files:
        file_url= f["url"]
        data = read_file_url(file_url)
        attachements.append(File(data,filename=f["filename"]))
    return attachements


def get_files(message):
    return  message['attachments'] if 'attachments' in message else []

def get_embeds(message):
    return  message['embeds'] if 'embeds' in message else []

def get_username_dislay(user):
    return user['nickname'] if 'nickname' in user else user['name']

def loads_to_object(json_file):
    return json.loads(open(json_file, "r").read(),object_hook=lambda d: SimpleNamespace(**d))

def loads_to_array(json_file):
    return json.load(open(json_file, "r"))

def load_channel(path):
    channel= loads_to_array(path)
    return channel

async def main():
    config= load_config()
    channel=load_channel(config.channelPath)
    start= config.start
    end= config.end
    messages= channel['messages']
    webhook= await create_webhook(config.webhookUrl)
    for i in range(start,end):
        m= messages[i]
        response = await  send_webhook(webhook,m)
        print("sent ",i)

    print("done")
    


asyncio.run(main())
