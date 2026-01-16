import { URLs } from "../const";

var pc = null;
var localStream = null;
var audioBlock = document.getElementById("audioContent");
let currentRemoteUserId = null;

export function toggleAudioMute(mute) {
    if (localStream) {
        localStream.getAudioTracks().forEach(track => {
            track.enabled = !mute;
        });
        console.log(`Audio tracks are now ${mute ? 'muted' : 'unmuted'}`);
    }
}

export function toggleVideoMute(mute) {
    if (localStream) {
        localStream.getVideoTracks().forEach(track => {
            track.enabled = !mute;
        });
        console.log(`Video tracks are now ${mute ? 'muted' : 'unmuted'}`);
    }
}

export const loadRemoteAvatar = async (userId) => {
    try {
        const response = await fetch(`${URLs.backendHost}/api/profile/image?user_id=${userId}`, {
            method: 'GET',
            credentials: 'include',
        });
        
        if (response.ok) {
            const blob = await response.blob();
            return URL.createObjectURL(blob);
        }
        return null;
    } catch (error) {
        console.log('ℹ️ Не удалось загрузить аватар собеседника:', error);
        return null;
    }
};

export async function initiateConnection({ audio = true, video = true, searchParameters}) {
    console.log(searchParameters);

    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio, video });
        console.log(localStream);
        document.getElementById('localVideo').srcObject = localStream;

        pc = new RTCPeerConnection();
        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
        
        pc.addEventListener('track', (evt) => {
            console.log(`Track status: ${evt.track.readyState}`);
            audioBlock = document.getElementById("audioContent");
            
            if (evt.track.kind === 'video') {
                document.getElementById('remoteVideo').srcObject = evt.streams[0];
            } else if (evt.track.kind === 'audio') {
                let audioElement = document.createElement('audio');
                audioElement.srcObject = evt.streams[0];
                audioElement.autoplay = true;
                audioBlock.appendChild(audioElement);
                audioElement.load();
                console.log(`Received track (${evt.track.kind})`);
            }
        });

        pc.addEventListener('connectionstatechange', () => {
            if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
                console.log('connection break');
                currentRemoteUserId = null;
                disconnect();
            }
        });

        pc.ondatachannel = (event) => {
            const receiveChannel = event.channel;
            receiveChannel.onopen = () => {
                console.log("Data channel is open!");
            };
            
            receiveChannel.onmessage = async (event) => {
                let info;
                try {
                    info = JSON.parse(event.data);
                } catch (error) {
                    info = { 'action': 'none' };
                }

                if (info.action === 'renegotiating') {
                    console.log(`Received negotiating ask from server`);
                    const offer = await pc.createOffer();
                    await pc.setLocalDescription(offer);
                    receiveChannel.send(
                        JSON.stringify({
                            sdp: pc.localDescription.sdp,
                            type: pc.localDescription.type,
                        })
                    );
                } 
                else if (info.action === 'answer') {
                    console.log(`Received negotiating answer from server`);
                    try {
                        await pc.setRemoteDescription(new RTCSessionDescription(JSON.parse(event.data)));
                    } catch (error) {
                        console.error(error);
                    }
                } 
                else if (info.action === 'users') {
                    console.log('Users info:', info.users);
                    if (info.users && info.users.length > 0 && info.users[0]) {
                        const remoteUserId = info.users[0].id || info.users[0];
                        if (remoteUserId && remoteUserId !== currentRemoteUserId) {
                            currentRemoteUserId = remoteUserId;
                            console.log('🎯 Новый собеседник:', remoteUserId);
                            window.onRemoteUserConnected?.(remoteUserId);
                        }
                    }
                }
            };
        };

        const response = await fetch(`${URLs.backendHost}/room/initiate_connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: searchParameters,
            credentials: 'include',
        });

        const offerData = await response.json();
        console.log('Server offer received:', offerData);
        
        const offer = new RTCSessionDescription(offerData);
        await pc.setRemoteDescription(offer);
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        
        await fetch(`${URLs.backendHost}/room/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                sdp: answer.sdp,
                type: answer.type,
                id: offerData.id,
                room_id: offerData.room_id,
            }),
        });
        console.log('Answer sent to server');
    } catch (error) {
        console.error("Error starting WebRTC:", error);
        alert("Failed to start WebRTC: " + error.message);
    }
}

export async function disconnect() {
    if (pc) {
        if (localStream) {
            localStream.getTracks().forEach(track => {
                track.stop();
                localStream.removeTrack(track);
            });
        }

        document.getElementById('remoteVideo').srcObject = null;
        pc.getSenders().forEach(sender => {
            pc.removeTrack(sender);
        });

        pc.close();
        pc = null;
        localStream = null;
        currentRemoteUserId = null;

        document.getElementById('localVideo').srcObject = null;
    }
}

export const getCurrentRemoteUserId = () => currentRemoteUserId;
