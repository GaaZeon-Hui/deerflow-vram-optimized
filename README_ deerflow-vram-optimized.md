本代码专为 Windows 11 + Docker Desktop (WSL2) 环境定制，包含 Codex-CLI 实施的显存保护逻辑。

本版本包含以下三项核心自动化机制，切勿删除 scripts/ 目录：

自动清理 (cleanup-stale-python.sh)：启动前自动杀掉残留进程，防止 Address already in use 报错。

显存保险丝 (enforce_cloud_embeddings.py)：启动前强制将 config.yaml 的 Embedding 和 Rerank 设为云端模式，防止 GTX 1650 (4GB) 溢出崩溃。

路径注入：在 docker-compose-dev.yaml 中强制注入了 PYTHONPATH，解决了 ModuleNotFoundError。

显存警戒：切勿在 config.yaml 中手动将 Embedding 切换为 local 或 huggingface 路径，这会导致容器在启动时反复重启（Restarting）。

版本冲突：执行 git pull 官方代码前，请先备份 scripts/ 目录和 docker/docker-compose-dev.yaml，否则你的优化逻辑会被覆盖。

WSL2 内存：如果 Docker 运行极慢，请检查 %USERPROFILE%\.wslconfig 是否限制了过小的内存。建议分配至少 8GB。

看似镇静，实则没招了。。。
