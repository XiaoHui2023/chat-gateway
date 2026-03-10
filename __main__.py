import argparse
import logging

from ai_hub_agents import client
from qq_adapter_protocol import MessageRequest, MessageResponse, run_all
from config import setup_logging
from models import AppConfig

logger = logging.getLogger("chat_gateway")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default="config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = AppConfig.load(args.config)
    setup_logging(config.log)

    async def handle(msg: MessageRequest) -> MessageResponse:
        robot_id = msg.msg_id
        source_id = msg.source_id
        sender_id = msg.sender_id
        thread_id = f"{robot_id}-{source_id}"

        logger.info(f"[{thread_id}: {sender_id}] ← {msg.content}")

        result = client.post(
            url=config.agent.url,
            thread_id=thread_id,
            query=msg.content,
            user_name=sender_id
        )
        logger.info(f"[{thread_id}: {sender_id}] → {result}")

        return MessageResponse(content=result.response)

    if not config.bots:
        logger.warning("config.yaml 中未配置任何 bot")
        return

    connections = tuple(
        {"handler": handle, "server_url": bot.server_url}
        for bot in config.bots
    )

    logger.info("启动 %d 个 bot 连接:", len(config.bots))

    run_all(*connections)


if __name__ == "__main__":
    main()