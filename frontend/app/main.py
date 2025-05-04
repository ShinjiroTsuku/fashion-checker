# frontend/app/main.py
import flet as ft
import requests
import json
import os

# バックエンドAPIのURL (Docker Composeのサービス名を利用)
# 環境変数から取得するか、デフォルト値を設定
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

# Fletアプリがリッスンするポート (Dockerfile CMDと合わせる)
FLET_PORT = int(os.getenv("FLET_PORT", 8550))

def main(page: ft.Page):
    page.title = "fashion checker"
    cloth_name_field = ft.Ref[ft.TextField]()
    cloth_text = ""
    loading = ft.Ref[ft.ProgressRing]() # ローディングアニメーション用
    fashion_button = ft.Ref[ft.ElevatedButton]()

    def create_blue_button(text, on_click, width=250):
        return ft.ElevatedButton(
            text,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_900,
                color=ft.colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=20),
            ),
            width=width,
    )

    def create_white_button(text, on_click, width=250):
        return ft.ElevatedButton(
            text,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.WHITE,
                color=ft.colors.BLUE_900,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=20),
            ),
            width=width,
    )

    def create_loading_button(text, on_click, ref=None, loading_ref = None, is_loading=False, width=250):
        return ft.Stack(
            [
                ft.ElevatedButton(
                    text,
                    ref=ref,
                    on_click=on_click,
                    disabled=is_loading,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.GREY if is_loading else ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        text_style=ft.TextStyle(size=20),
                    ),
                    width=width,
                ),
                ft.ProgressRing(
                    ref=loading_ref,
                    visible=is_loading,
                    width=30,
                    height=30,
                    stroke_width=3,
                    top=10,  # ボタンの中央に近づける
                    left=(width - 30) // 2,  # ボタンの真ん中に表示する
                )
            ]
        )

    if not hasattr(page, "cloth_list"):
        page.cloth_list = []

    def add_cloth(e):
        nonlocal cloth_text
        name = cloth_name_field.current.value
        if not name:
            page.dialog = ft.AlertDialog(
                 title=ft.Text("エラー"),
                 content=ft.Text("服の名前が入力されていません。"),
                 actions=[ft.TextButton("OK", on_click=lambda _: page.dialog.close())]
            )
            page.dialog.open = True
            page.update()
            return
        try:
            json_data = json.dumps({"name": name})
            response = requests.post(
                f"{API_BASE_URL}/register",
                data = json_data,
                headers={"Content-Type": "application/json"},
                timeout = 10
            )
            response.raise_for_status()
            data = response.json()
            page.cloth_list = data
        except Exception as e:
            page.dialog = ft.AlertDialog(
                title=ft.Text("エラー"),
                content=ft.Text(f"エラー発生: {e}"),
                actions=[ft.TextButton("OK", on_click=lambda _: page.dialog.close())]
            )
            page.dialog.open = True
            page.update()
            return 
        page.go("/list")

    

    selected_name = ft.Ref() # ドロップダウンの選択を参照
    fashion_text = "" # APIの返答をここに保持

    def fetch_fashion_advice():
        nonlocal fashion_text

        # ボタンを押した後
        fashion_button.current.disabled = True
        fashion_button.current.bgcolor = ft.colors.GREY
        loading.current.visible = True
        page.update()

        name = selected_name.current.value # ドロップダウンの現在の値を保持
        if not name: # 場所が選択されていない時の処理
            page.dialog = ft.AlertDialog(
                title=ft.Text("エラー"),
                content=ft.Text("場所が選択されていません。"),
                actions=[ft.TextButton("OK", on_click=lambda _: page.dialog.close())]
            )
            page.dialog.open = True
            page.update()
            # ボタンを戻す
            fashion_button.current.disabled = False
            fashion_button.current.bgcolor = ft.colors.BLUE_900
            loading.current.visible = False
            page.update()
            return
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json={"name": name},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            fashion_text = data.get("generated_text", "取得失敗")
        except Exception as e:
            fashion_text = f"エラー発生: {e}"
        page.go("/confirm")

    def common_view(title, controls):
        return ft.View(
            route=page.route,
            controls=[
                ft.Column(
                    [
                        ft.Text(title, size=50, weight="bold", text_align="center")
                    ] + controls,
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=40,
                )
            ],
            vertical_alignment="center",
            horizontal_alignment="center",
        )

    def route_change(route):
        page.views.clear()
        # ホーム画面
        if page.route == "/":
            page.views.append(
                common_view(
                    "服装チェッカー",
                    [
                        ft.Row(
                            [
                                ft.Text("場所：", size=16),
                                ft.Dropdown(
                                    ref=selected_name,
                                    options=[
                                        ft.dropdown.Option("大阪府_堺市"),
                                        ft.dropdown.Option("大阪府_大阪市"),
                                        ft.dropdown.Option("大阪府_岸和田市"),
                                    ],
                                    width=200,
                                ),
                            ],
                            alignment="center",
                            spacing=10,
                        ),
                        create_loading_button("服装を見る", on_click=lambda _: fetch_fashion_advice(), ref=fashion_button, loading_ref=loading),
                        ft.OutlinedButton(
                            "服装一覧",
                            on_click=lambda _: page.go("/list"),
                            width=150,
                        )
                    ]
                )
            )

        # confirm画面
        if page.route == "/confirm":
            page.views.append(
                common_view(
                    "服装の確認",
                    [
                        ft.Icon(name=ft.Icons.FACE, size=30),
                        ft.Markdown(fashion_text),
                        ft.Row(
                            [
                                create_white_button("戻る", on_click=lambda _: page.go("/")),
                                create_blue_button("再生成する", on_click=lambda _: fetch_fashion_advice()),
                            ],
                            alignment="center",
                            spacing=20,
                        ),
                    ]
                )
            )

        # list画面
        if page.route == "/list":
            controls = []
            if hasattr(page, "cloth_list") and page.cloth_list:
                for item in page.cloth_list:
                    controls.append(
                        ft.Container(
                            content=ft.Text(item),
                            padding=2,
                            margin=ft.margin.only(bottom=2),
                            alignment=ft.alignment.center,
                        )
                    )

            controls.append(
                ft.Row(
                    [
                        create_white_button("戻る", on_click=lambda _: page.go("/")),
                        create_blue_button("服装を登録する", on_click=lambda _: page.go("/register")),
                    ],
                    alignment="center",
                    spacing=20,
                )
            )

            page.views.append(
                common_view("服装一覧", controls)
            )

        # register画面
        if page.route == "/register":
            page.views.append(
                common_view(
                    "服装登録",
                    [
                        ft.Text("服の名称:"),
                        ft.TextField(ref=cloth_name_field, width=300),
                        ft.Text("ジャンル:"),
                        ft.Dropdown(
                        options=[
                            ft.dropdown.Option("ジャケット"),
                        ],
                        autofocus=True,
                        ),
                        ft.Row(
                            [
                                create_white_button("戻る", on_click=lambda _: page.go("/list")),
                                create_blue_button("登録", on_click=add_cloth),
                            ],
                            alignment="center",
                            spacing=20,
                        ),
                    ]
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

# Docker内でWebアプリとして実行
# ホスト 0.0.0.0 を指定し、ポートを固定
# view=ft.AppView.WEB_BROWSER は flet run コマンドのデフォルトなので不要な場合も
ft.app(target=main, port=FLET_PORT, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)