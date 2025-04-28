import { URLs } from "../const";

var pc = null;
var localStream = null;
var audioBlock = document.getElementById("audioContent");


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

export async function initiateConnection({ audio = true, video = true, searchParameters}) {
    console.log(searchParameters)

    try {
        // statusText.textContent = 'Создаём соединение'
        localStream = await navigator.mediaDevices.getUserMedia({ audio, video });
        console.log(localStream);

        document.getElementById('localVideo').srcObject = localStream;

        pc = new RTCPeerConnection();
        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
        pc.addEventListener('track', (evt) => {
            console.log(`Tack status: ${evt.track.readyState}`)
            audioBlock = document.getElementById("audioContent");
            if (evt.track.kind === 'video') {
                document.getElementById('remoteVideo').srcObject = evt.streams[0];
            } else if (evt.track.kind === 'audio') {
                let audioElement = document.createElement('audio');
                audioElement.srcObject = evt.streams[0];
                audioElement.type = "audio/mpeg";
                audioElement.autoplay = true;
                audioBlock.appendChild(audioElement);
                audioElement.load();
                // emptySound = true;
                console.log(`Received track (${evt.track.kind})`);
            }
        });

        // Detect connection state changes to identify interlocutor disconnect
        pc.addEventListener('connectionstatechange', () => {
            if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
                console.log('connection break');
                disconnect();
                // initiateConnection();
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
                    info = JSON.parse(event.data)
                } catch (error) {
                    info = { 'action': 'none' }
                }
                if (info.action === 'renegotiating') {
                    // statusText.textContent = 'Сервер хочет устроить пересогласование'
                    console.log(`Received negotiating ask from sever`);

                    const offer = await pc.createOffer();
                    await pc.setLocalDescription(offer);

                    receiveChannel.send(
                        JSON.stringify({
                            sdp: pc.localDescription.sdp,
                            type: pc.localDescription.type,
                        })
                    );
                } else if (info.action === 'answer') {
                    console.log(`Received negotiating answer from sever`);
                    // statusText.textContent = 'Получен ответ на оффер для пересогласования'
                    try {
                        await pc.setRemoteDescription(new RTCSessionDescription(JSON.parse(event.data)));
                    } catch (error) {
                        console.error(error)
                    }

                } else if (info.action === 'users') {
                    console.log(info.users)
                    // usersList.innerHTML = ''
                    info.users.forEach((item) => {
                        const li = document.createElement("li");
                        li.textContent = item;
                        // usersList.appendChild(li);
                    });
                }
            };
        };
        // statusText.textContent = 'Отправляем запрос на подключение'
        const response = await fetch(`${URLs.backendHost}/room/initiate_connection`, {  //Removed the room id
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: searchParameters,
            credentials: 'include',
        });

        const offerData = await response.json();
        console.log('Server offer asked')
        // statusText.textContent = 'Получен оффер на соединение'
        const offer = new RTCSessionDescription(offerData);
        await pc.setRemoteDescription(offer);
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        await fetch(`${URLs.backendHost}/room/answer`, {
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
        // statusText.textContent = 'Отправлен ответ на оффер для подключения'
        console.log('Answer sended to server');
    } catch (error) {
        console.error("Error starting WebRTC:", error);
        alert("Failed to start WebRTC: " + error.message);
    }
}

export async function disconnect() {
    if (pc) {
        // statusText.textContent = 'Отключаемся...';
        // Остановка локального потока
        if (localStream) {
            localStream.getTracks().forEach(track => {
                track.stop();
                localStream.removeTrack(track); // Ensure the track is removed from the stream
            });
        }

        // Очистка удаленного видео
        document.getElementById('remoteVideo').srcObject = null;

        pc.getSenders().forEach(sender => {
            pc.removeTrack(sender);
        });

        pc.close();
        pc = null;
        localStream = null;

        document.getElementById('localVideo').srcObject = null;
        // audioBlock.innerHTML = '';
        // statusText.textContent = 'Отключено';
    }
}