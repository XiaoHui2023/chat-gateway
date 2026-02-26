import argparse
import logging
import uuid

from ai_hub_agents.client import AgentClient
from qq_adapter_protocol import MessageRequest, MessageResponse, run_all
from config import setup_logging
from models import AppConfig

logger = logging.getLogger("chat_gateway")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = AppConfig.load(args.config)
    setup_logging(config.log)

    client = AgentClient(config.agent.url)

    async def handle(msg: MessageRequest) -> MessageResponse:

        logger.info(f"[{msg.sender_id}] ← {msg.content}")
        result = client.invoke(msg.content, thread_id=msg.sender_id)
        logger.info(f"[{msg.sender_id}] → {result.text}")

        return MessageResponse(content=result.text)

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