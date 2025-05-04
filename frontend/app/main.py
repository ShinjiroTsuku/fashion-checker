# frontend/app/main.py
import flet as ft
import requests
import json
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
FLET_PORT = int(os.getenv("FLET_PORT", 8550))

def main(page: ft.Page):
    page.title = "fashion checker"
    page.theme_mode = ft.ThemeMode.LIGHT

    # 参照オブジェクト
    cloth_name_field = ft.Ref[ft.TextField]()
    fashion_button = ft.Ref[ft.ElevatedButton]()
    loading = ft.Ref[ft.ProgressRing]()
    selected_prefecture = ft.Ref[ft.Dropdown]()
    selected_city = ft.Ref[ft.Dropdown]()

    # データ
    fashion_text = ""
    prefecture_city_data = {
        "東京都": ["渋谷区", "新宿区", "港区"],
        "大阪府": ["堺市", "大阪市", "岸和田市"],
        "北海道": ["札幌市", "旭川市", "函館市"],
    }

    if not hasattr(page, "cloth_list"):
        page.cloth_list = []

    # ボタン有効化チェック
    def update_view_button_state(e=None):
        if fashion_button.current is None:
            return
        enabled = bool(selected_city.current.value)
        fashion_button.current.disabled = not enabled
        fashion_button.current.bgcolor = ft.colors.BLUE_700 if enabled else ft.colors.GREY_300
        fashion_button.current.color = ft.colors.WHITE if enabled else ft.colors.GREY_600
        page.update()

    # 都道府県選択時に市区町村を更新
    def update_cities(e):
        prefecture = selected_prefecture.current.value
        if prefecture and prefecture in prefecture_city_data:
            cities = prefecture_city_data[prefecture]
            selected_city.current.options = [ft.dropdown.Option(city) for city in cities]
            selected_city.current.value = None
            page.update()
        update_view_button_state()

    # 服装アドバイス取得
    def fetch_fashion_advice(e=None):
        nonlocal fashion_text

        if not selected_city.current.value:
            return

        # ローディング開始
        fashion_button.current.disabled = True
        fashion_button.current.bgcolor = ft.colors.GREY
        loading.current.visible = True
        page.update()

        name = f"{selected_prefecture.current.value}_{selected_city.current.value}"
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json={"name": name},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            fashion_text = data.get("generated_text", "取得失敗")
        except Exception as ex:
            fashion_text = f"エラー発生: {ex}"

        page.go("/confirm")

    # 汎用ボタン
    def create_blue_button(text, on_click, width=250):
        return ft.ElevatedButton(
            text,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_700,
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
                color=ft.colors.BLUE_700,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=20),
            ),
            width=width,
        )

    # 共通ビュー
    def common_view(title, controls):
        return ft.View(
            route=page.route,
            controls=[
                ft.Column([
                    ft.Text(title, size=50, weight="bold", text_align="center")
                ] + controls, alignment="center", horizontal_alignment="center", spacing=40)
            ],
            vertical_alignment="center",
            horizontal_alignment="center"
        )

    # ルートハンドリング
    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(
                common_view(
                    "服装チェッカー",
                    [
                        ft.Row([
                            ft.Text("都道府県："),
                            ft.Dropdown(
                                ref=selected_prefecture,
                                options=[ft.dropdown.Option(pref) for pref in prefecture_city_data.keys()],
                                on_change=update_cities,
                                width=200,
                            ),
                            ft.Text("市区町村："),
                            ft.Dropdown(
                                ref=selected_city,
                                options=[],
                                on_change=update_view_button_state,
                                width=200,
                            )
                        ], alignment="center", spacing=10),

                        ft.Stack([
                            ft.ElevatedButton(
                                "服装を見る",
                                ref=fashion_button,
                                on_click=fetch_fashion_advice,
                                disabled=True,
                                style=ft.ButtonStyle(
                                    padding=20,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    text_style=ft.TextStyle(size=20),
                                ),
                                width=250
                            ),
                            ft.ProgressRing(ref=loading, visible=False, width=30, height=30, stroke_width=3, top=10, left=110)
                        ]),

                        ft.OutlinedButton("服装一覧", on_click=lambda _: page.go("/list"), width=150)
                    ]
                )
            )

        elif page.route == "/confirm":
            page.views.append(
                common_view(
                    "服装の確認",
                    [
                        ft.Markdown(fashion_text),
                        ft.Row([
                            create_white_button("戻る", on_click=lambda _: page.go("/")),
                            create_blue_button("再生成する", on_click=fetch_fashion_advice)
                        ], alignment="center", spacing=20)
                    ]
                )
            )

        elif page.route == "/list":
            controls = []
            if page.cloth_list:
                controls += [ft.Container(content=ft.Text(item), padding=2, alignment=ft.alignment.center) for item in page.cloth_list]
            controls.append(
                ft.Row([
                    create_white_button("戻る", on_click=lambda _: page.go("/")),
                    create_blue_button("服装を登録する", on_click=lambda _: page.go("/register"))
                ], alignment="center", spacing=20)
            )
            page.views.append(common_view("服装一覧", controls))

        elif page.route == "/register":
            page.views.append(
                common_view(
                    "服装登録",
                    [
                        ft.Text("服の名称:"),
                        ft.TextField(ref=cloth_name_field, width=300),
                        ft.Text("ジャンル:"),
                        ft.Dropdown(options=[ft.dropdown.Option("ジャケット")], autofocus=True),
                        ft.Row([
                            create_white_button("戻る", on_click=lambda _: page.go("/list")),
                            create_blue_button("登録", on_click=lambda _: None)  # 仮
                        ], alignment="center", spacing=20)
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

ft.app(target=main, port=FLET_PORT, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)