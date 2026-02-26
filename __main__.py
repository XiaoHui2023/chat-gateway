import uuid

from ai_hub_agents.client import AgentClient
from qq_adapter_protocol import MessageRequest, MessageResponse, run_all

from .models import AppConfig


def make_handler(client: AgentClient, bot_name: str):
    """为每个 bot 创建独立的 handler，各自维护会话线程。"""
    threads: dict[str, str] = {}

    async def handle(msg: MessageRequest) -> MessageResponse:
        print(f"message=\n{msg}")
        return MessageResponse(content=msg.content)
        thread_key = f"{msg.sender_id}"
        if thread_key not in threads:
            threads[thread_key] = str(uuid.uuid4())

        print(f"[{bot_name}] {msg.sender_id}: {msg.content}")
        result = client.invoke(msg.content, thread_id=threads[thread_key])
        print(f"[{bot_name}] → {result}")

        return MessageResponse(content=result)

    return handle


def main() -> None:
    config = AppConfig.load()

    client = AgentClient(config.agent.url)

    if not config.bots:
        print("config.yaml 中未配置任何 bot")
        return

    connections = tuple(
        (bot.host, bot.port, make_handler(client, bot.name))
        for bot in config.bots
    )

    print(f"启动 {len(config.bots)} 个 bot 连接:")
    for bot in config.bots:
        print(f"  - {bot.name} → {bot.host}:{bot.port}")

    run_all(*connections)


if __name__ == "__main__":
    main()