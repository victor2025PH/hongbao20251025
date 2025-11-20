import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class Service:
    name: str
    url: str
    docker_service: str
    description: str


SERVICES: List[Service] = [
    Service(
        name="web_admin_api",
        url=os.getenv("WEB_ADMIN_HEALTH_URL", "http://localhost:8001/healthz"),
        docker_service="web_admin",
        description="FastAPI Web Admin 后端",
    ),
    Service(
        name="miniapp_api",
        url=os.getenv("MINIAPP_HEALTH_URL", "http://localhost:8080/healthz"),
        docker_service="miniapp_api",
        description="FastAPI MiniApp 后端",
    ),
    Service(
        name="frontend",
        url=os.getenv("FRONTEND_HEALTH_URL", "http://localhost:3001"),
        docker_service="frontend",
        description="Next.js 管理后台前端",
    ),
]


def log(msg: str) -> None:
    print(f"[health_watchdog] {msg}", flush=True)


def check_service(service: Service, timeout: int) -> bool:
    try:
        resp = requests.get(service.url, timeout=timeout)
        if resp.status_code < 400:
            log(f"{service.name} OK ({resp.status_code})")
            return True
        log(f"{service.name} unhealthy, status={resp.status_code}")
        return False
    except requests.RequestException as exc:
        log(f"{service.name} check failed: {exc}")
        return False


def docker_compose_restart(service: Service) -> None:
    cmd = ["docker", "compose", "restart", service.docker_service]
    log(f"尝试重启 Docker 服务: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        log(f"{service.name} 已触发重启")
    except subprocess.CalledProcessError as exc:
        log(f"重启 {service.name} 失败: {exc}")


def suggest_fix(service: Service) -> None:
    log("=== 修复建议 ===")
    log(f"- 查看容器日志: docker compose logs {service.docker_service} | tail -n 100")
    log("- 检查数据库与 Redis 等依赖是否正常")
    log("- 检查 .env 与部署配置是否正确")


def run_once(timeout_each: int, auto_heal: bool) -> int:
    unhealthy = []
    for svc in SERVICES:
        ok = check_service(svc, timeout_each)
        if not ok:
            unhealthy.append(svc)

    for svc in unhealthy:
        if auto_heal:
            docker_compose_restart(svc)
        suggest_fix(svc)

    return 0 if not unhealthy else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30, help="循环模式下两次检查的间隔秒数")
    parser.add_argument("--timeout", type=int, default=5, help="单个 HTTP 请求超时时间（秒）")
    parser.add_argument("--once", action="store_true", help="只执行一次检查后退出")
    parser.add_argument("--no-auto-heal", action="store_true", help="只告警不自动重启")

    args = parser.parse_args()

    auto_heal = not args.no_auto_heal

    if args.once:
        sys.exit(run_once(args.timeout, auto_heal))

    log("进入循环健康检查模式...")
    while True:
        run_once(args.timeout, auto_heal)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

