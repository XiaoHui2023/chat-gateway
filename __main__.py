import argparse
import logging
import asyncio
import ai_hub_agents
import peer_protocol
from onebot_protocol import MessagePayload,TextMessageSegment
from config import Config, Bridge
from log import setup_logging
logger = logging.getLogger("chat_gateway")

async def build_bridge(bridge: Bridge):
    bot_client = peer_protocol.Client(
        url=bridge.bot_url,
    )

    @bot_client.on_receive
    async def _(payload: MessagePayload):
        robot_id = payload.bot_id
        session_id = payload.session_id
        user_id = payload.user_id
        thread_id = f"{robot_id}-{session_id}"
        content = "".join([x.data.text for x in payload.messages if isinstance(x, TextMessageSegment)])
        source_type = payload.source_type
        message_id = payload.message_id

        logger.info(f"[{thread_id}] ← {content}")

        result = ai_hub_agents.client.post(
            url=bridge.hub_url,
            thread_id=thread_id,
            query=content,
            user_name=user_id
        )

        logger.info(f"[{thread_id}] → {result.response}")

        await bot_client.send(MessagePayload(
            source_type=source_type,
            message_id=message_id,
            bot_id=robot_id,
            session_id=session_id,
            user_id=user_id,
            messages=[TextMessageSegment(data={"text": result.response})],
        ))

    await bot_client.run()

async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="配置文件路径")
    args = parser.parse_args()

    config = Config.load(args.config)
    setup_logging(config.log_dir)
    
    tasks = [build_bridge(bridge) for bridge in config.bridges]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())