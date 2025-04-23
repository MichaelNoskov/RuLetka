import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay
import json
import random

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

def find_available_room():
    """Находит свободную комнату (менее 2 участников) или возвращает None."""
    for room_id, room in rooms.items():
        if len(room) < 2:
            return room_id
    return None

def generate_room_id():
    """Генерирует новый уникальный ID комнаты."""
    return str(random.randint(1000, 9999))  # Simple random ID

@router.post('/initiate_connection')
async def initiate_connection(request: Request):
    room_id = find_available_room()

    if not room_id:
        room_id = generate_room_id()
        rooms[room_id] = []
        print(f"Created new room: {room_id}")
    else:
        print(f"Joining existing room: {room_id}")

    if len(rooms[room_id]) >= 2:
        return JSONResponse(content={'error': 'Room is full.'}, status_code=403)

    pc = RTCPeerConnection()
    pc.client_id = str(random.randint(0, 100)).rjust(3, '0')
    
    data_channel = pc.createDataChannel('renegotiation')
    pc.data_channel = data_channel

    @data_channel.on("open")
    async def on_open():
        await send_user_list(room_id)

    @data_channel.on('message')
    async def on_message(message):
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

    pc.addTransceiver('audio', 'recvonly')
    pc.addTransceiver('video', 'recvonly')
    
    rooms[room_id].routerend(pc)
    tracks[pc] = set()
    
    for other_pc in rooms[room_id]:
        if other_pc != pc:
            for track in tracks[other_pc]:
                pc.addTrack(MediaRelay().subscribe(track))

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState in ('failed', 'disconnected', 'closed'):
            print(f'Client {pc.client_id} disconnected')
            
            await remove_client_from_room(pc)

    @pc.on('track')
    async def on_track(track):
        if track.kind not in ('audio', 'video'):
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
    print(f'Client {client_id} connected to room {room_id}')
    await send_user_list(room_id)
    return JSONResponse(content={'message': 'Connection established.'})

async def remove_client_from_room(pc: RTCPeerConnection):
    """Удаляет клиента из комнаты и рассылает обновления."""
    for room_id, room in rooms.items():
        if pc in room:
            rooms[room_id].remove(pc)
            await send_user_list(room_id)
            
            # Remove tracks from other peers
            for other_pc in room:
                for transceiver in other_pc.getTransceivers():
                    if transceiver.receiver and transceiver.receiver.track:
                        if transceiver.receiver.track in tracks.get(pc, set()):
                            other_pc.removeTrack(transceiver.sender.track)  # Remove the track

            await pc.close()

            if pc in tracks:
                del tracks[pc]

            if not rooms[room_id]:
                del rooms[room_id]
            return
