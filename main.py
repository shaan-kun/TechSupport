import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from mediator import Mediator, WebSocketType

app = FastAPI()


mediator = Mediator()


@app.websocket("/ask")
async def websocket_endpoint(websocket: WebSocket):
    await mediator.manager.connect(websocket, WebSocketType.ASKING)

    try:
        answering = await mediator.get_answering(websocket)
        mediator.chats[websocket] = answering
    except WebSocketDisconnect:
        return mediator.manager.disconnect(websocket, WebSocketType.ASKING)

    try:
        while True:
            question = await websocket.receive_text()
            await mediator.manager.send_personal_messsage(question, answering)
    except WebSocketDisconnect:
        mediator.manager.disconnect(websocket, WebSocketType.ASKING)

        await mediator.manager.send_personal_messsage(
            "*asking has left the chat*", answering
        )
        mediator.manager.disconnect(answering, WebSocketType.ANSWERING)

        del mediator.chats[websocket]


@app.websocket("/answer")
async def websocket_endpoint(websocket: WebSocket):
    await mediator.manager.connect(websocket, WebSocketType.ANSWERING)
    asking = await mediator.get_asking(websocket)
    while True:
        answer = await websocket.receive_text()
        await mediator.manager.send_personal_messsage(answer, asking)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
