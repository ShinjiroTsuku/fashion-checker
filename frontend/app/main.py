# frontend/app/main.py
import flet as ft
import requests
import json
import os

# バックエンドAPIのURL (Docker Composeのサービス名を利用)
# 環境変数から取得するか、デフォルト値を設定
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
API_URL = f"{API_BASE_URL}/generate"

# Fletアプリがリッスンするポート (Dockerfile CMDと合わせる)
FLET_PORT = int(os.getenv("FLET_PORT", 8550))

def main(page: ft.Page):
    page.title = "fashion checker"

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Text("服装チェッカー",size=20),
                    ft.Text("場所:"),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("大阪"),
                            ft.dropdown.Option("東京"),
                            ft.dropdown.Option("愛知"),
                        ],
                        autofocus=True,
                    ),
                    ft.CupertinoButton("服装を見る", on_click=lambda _: page.go("/confirm")),
                    ft.CupertinoButton("服装一覧", on_click=lambda _: page.go("/list")),
                ],
            )
        )
        if page.route == "/confirm":
            page.views.append(
                ft.View(
                    "/confirm",
                    [
                        ft.Text("服装の確認"),
                        ft.Icon(name=ft.Icons.FACE, size=30),
                        ft.ElevatedButton("戻る", on_click=lambda _: page.go("/")),
                        ft.ElevatedButton("再生成する", on_click=lambda _: page.go("/confirm")),
                    ],
                )
            )
        if page.route == "/list":
            page.views.append(
                ft.View(
                    "/list",
                    [
                        ft.ElevatedButton("戻る", on_click=lambda _: page.go("/")),
                        ft.ElevatedButton("服装を登録する", on_click=lambda _: page.go("/register")),
                    ],
                )
            )    
        if page.route == "/register":
            page.views.append(
                ft.View(
                    "/register",
                    [
                        ft.Text("服の名称:"),
                        ft.ElevatedButton("戻る", on_click=lambda _: page.go("/list")),
                        ft.ElevatedButton("登録", on_click=lambda _: page.go("/list")),
                    ],
                )
            ) 
        page.update()

    def view_pop(view):
        pages.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

# Docker内でWebアプリとして実行
# ホスト 0.0.0.0 を指定し、ポートを固定
# view=ft.AppView.WEB_BROWSER は flet run コマンドのデフォルトなので不要な場合も
ft.app(target=main, port=FLET_PORT, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)