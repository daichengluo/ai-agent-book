"""
实验 10-1 演示入口：一条命令跑通“需求澄清 -> 代码实现 -> 代码审查”三阶段。

    python demo.py

演示任务：用户想要“写一个整理下载文件夹的 Python 脚本”。
需求本身模糊，因此需求澄清阶段的 Agent 会主动提问，由模拟用户自动回答；
之后进入实现阶段写代码、审查阶段严格把关（可能回退重写）。
"""

from agent import StagedAgent
from config import Config


USER_TASK = "帮我写一个整理下载文件夹的 Python 脚本。"


def main() -> None:
    print("模型：%s  | base_url：%s" % (Config.MODEL, Config.BASE_URL))
    agent = StagedAgent(max_revisions=3, verbose=True)
    agent.run(USER_TASK)
    agent.print_summary()

    # 打印最终产出的主文件，方便肉眼确认实现阶段真的写了代码
    if agent.workspace.files:
        print("\n" + "=" * 70)
        print("最终产出文件内容：")
        print("=" * 70)
        for path, content in agent.workspace.files.items():
            print(f"\n--- {path} ---\n{content}")


if __name__ == "__main__":
    main()
