import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set

from ..dependencies import get_db
from ..services.chat_service import ChatService
from ..services.message_service import MessageService
from ..schemas import MessageCreate

router = APIRouter(prefix="/ws", tags=["WebSocket"])

active_connections: Dict[int, Set[WebSocket]] = {}


async def connect_user(user_id: int, websocket: WebSocket):
    await websocket.accept()
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)


def disconnect_user(user_id: int, websocket: WebSocket):
    if user_id in active_connections:
        active_connections[user_id].discard(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]
    print(f"Disconnected user_id={user_id}")


async def broadcast_message(chat_participant_ids, message_data):

    for participant_id in chat_participant_ids:
        connections = active_connections.get(participant_id, [])
        for ws in connections:
            await ws.send_json(message_data)


@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    await connect_user(user_id, websocket)
    print(f"User {user_id} connected via WS.")

    try:
        while True:
            data = await websocket.receive_json()
            print("RECEIVED DATA:", data)
            chat_id = data.get("chat_id")
            text = data.get("text")
            client_msg_id = data.get("client_message_id")

            new_message = await MessageService.create_message(
                db,
                user_id,
                MessageCreate(
                    chat_id=chat_id,
                    text=text,
                    client_message_id=client_msg_id
                )
            )

            chat = await ChatService.get_chat(db, chat_id)
            participant_ids = [u.id for u in chat.participants]
            if user_id not in participant_ids:
                participant_ids.append(user_id)
            print("Broadcasting to participants:", participant_ids)


            message_data = {
                "type": "new_message",
                "id": new_message.id,
                "chat_id": new_message.chat_id,
                "sender_id": new_message.sender_id,
                "text": new_message.text,
                "timestamp": str(new_message.timestamp),
                "is_read": new_message.is_read,
                "client_message_id": new_message.client_message_id,
            }


            await broadcast_message(participant_ids, message_data)

    except WebSocketDisconnect:
        print(f"WebSocketDisconnect for user_id={user_id}")
        disconnect_user(user_id, websocket)
    except Exception as e:
        print("UNEXPECTED ERROR in WebSocket:", e)
        traceback.print_exc()
        disconnect_user(user_id, websocket)
    finally:
        print(f"Connection closed for user_id={user_id}")
