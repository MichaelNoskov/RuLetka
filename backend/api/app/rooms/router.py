from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay
from pydantic.types import PastDate
from datetime import date
from common.schemas.user import UserInfo
from common.schemas.params import SearchRoom
import json
import random
from app.utils import get_user_id
from common.core.config import settings
from common.storage.rabbit import send_message
from common.storage.redis import VectorStorage
from logger import logger
import numpy as np

router = APIRouter()

rooms: dict[str, list[RTCPeerConnection]] = {}
tracks: dict[RTCPeerConnection, set[MediaStreamTrack]] = {}

@router.on_event('shutdown')
async def on_shutdown():
    for room in rooms.values():
        for pc in room:
            await pc.close()

async def send_user_list(room_id: str):
    """Отправляет список пользователей в комнате всем участникам."""
    if room_id in rooms:
        user_ids = [pc.client_id for pc in rooms[room_id] if hasattr(pc, 'client_id')]
        for pc in rooms[room_id]:
            if hasattr(pc, 'data_channel') and pc.data_channel.readyState == 'open':
                pc.data_channel.send(
                    json.dumps({
                        'action': 'users',
                        'users': user_ids
                    })
                )

async def find_available_room(user_id, is_male=None, age=None, country=None):
    answer = await send_message({'user_id': user_id, 'action': 'get_user', 'target_user_id': user_id}, settings.MODEL_QUEUE, 'users', user_id, wait_answer=True)
    vector = np.array(json.loads(answer))

    rooms_id = await VectorStorage.search_rooms(vector, gender = "male" if is_male else "female" if is_male is False else None, age=age, country=country)

    if not rooms_id:
        return None

    room_id = random.choice(rooms_id)
    if room_id not in rooms:
        await VectorStorage.delete_room(room_id)
        return await find_available_room(user_id, is_male, age, country)

    await VectorStorage.delete_room(room_id)

    return room_id

async def save_room(user_id):
    answer = await send_message({'user_id': user_id, 'action': 'get_user', 'target_user_id': user_id}, settings.MODEL_QUEUE, 'users', user_id, wait_answer=True)
    vector = json.loads(answer)

    answer = await send_message({'user_id': user_id, 'action': 'get_user_info'}, settings.DB_QUEUE, 'users', user_id, wait_answer=True)
    user: UserInfo = UserInfo.model_validate_json(answer)

    today = date.today()
    age = today.year - user.birthdate.year
    if (today.month, today.day) < (user.birthdate.month, user.birthdate.day):
        age -= 1

    await VectorStorage.save_vector(user_id, np.array(vector), "male" if user.is_male else "female" if user.is_male is False else None, age, user.country)

@router.post('/initiate_connection')
async def initiate_connection(
    params: SearchRoom,
    user_id: str = Depends(get_user_id)
):

    room_id = await find_available_room(user_id, params.is_male, params.age, params.country)

    if not room_id:
        room_id = user_id
        await save_room(room_id)
        rooms[room_id] = []

    pc = RTCPeerConnection()
    pc.client_id = str(random.randint(0, 100)).rjust(3, '0')
    
    data_channel = pc.createDataChannel('renegotiation')
    pc.data_channel = data_channel

    @data_channel.on("open")
    async def on_open():
        await send_user_list(room_id)

    @data_channel.on('message')
    async def on_message(message):
        if message == 'keepalive':
            data_channel.send('keepalive')
            return

        offerData = json.loads(message)
        await pc.setRemoteDescription(RTCSessionDescription(sdp=offerData['sdp'], type=offerData['type']))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        data_channel.send(
            json.dumps({
                'action': 'answer',
                'sdp': pc.localDescription.sdp,
                'type': pc.localDescription.type,
            })
        )

    # pc.addTransceiver('audio', 'recvonly')
    pc.addTransceiver('video', 'recvonly')
    
    rooms[room_id].append(pc)
    tracks[pc] = set()
    
    for other_pc in rooms[room_id]:
        if other_pc != pc:
            for track in tracks[other_pc]:
                pc.addTransceiver(MediaRelay().subscribe(track), 'sendonly')

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState in ('failed', 'disconnected', 'closed'):
            logger.info(f'Client {pc.client_id} disconnected')
            
            await remove_client_from_room(pc)

    @pc.on('track')
    async def on_track(track):
        if track.kind not in ('video'):
            return

        tracks[pc].add(track)

        for other_pc in rooms[room_id]:
            if other_pc != pc:
                other_pc.addTrack(MediaRelay().subscribe(track))
                if hasattr(other_pc, 'data_channel') and other_pc.data_channel.readyState == 'open':
                    other_pc.data_channel.send(
                        json.dumps({'action': 'renegotiating'})
                    )

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    return JSONResponse(
        content={
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type,
            'id': pc.client_id,
            'room_id': room_id
        }
    )

@router.post('/answer')
async def answer(request: Request):
    params = await request.json()
    answer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    client_id = params['id']
    room_id = params['room_id']

    if room_id not in rooms:
        return JSONResponse(content={'error': 'Room not found.'}, status_code=404)
    
    pc = next((p for p in rooms[room_id] if hasattr(p, 'client_id') and p.client_id == client_id), None)

    if not pc:
        return JSONResponse(content={'error': 'Peer connection not found.'}, status_code=404)

    await pc.setRemoteDescription(answer)
    logger.info(f'Client {client_id} connected to room {room_id}')
    await send_user_list(room_id)
    return JSONResponse(content={'message': 'Connection established.'})

async def remove_client_from_room(pc: RTCPeerConnection):
    for room_id, room in list(rooms.items()):
        if pc in room:
            room.remove(pc)

            for other_pc in room:
                await other_pc.close()
                if other_pc in tracks:
                    del tracks[other_pc]
            
            if room_id in rooms:
                del rooms[room_id]

            if pc in tracks:
                del tracks[pc]

            break
    await pc.close()
