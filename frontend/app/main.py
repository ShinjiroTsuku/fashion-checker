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
    cloth_text = ""

    # データ
    fashion_text = ""
    prefecture_city_data = {
        "北海道": ["札幌市", "旭川市", "函館市"],
        "青森県": ["青森市", "弘前市", "八戸市"],
        "岩手県": ["盛岡市", "花巻市", "北上市"],
        "宮城県": ["仙台市", "石巻市", "大崎市"],
        "秋田県": ["秋田市", "横手市", "大仙市"],
        "山形県": ["山形市", "鶴岡市", "酒田市"],
        "福島県": ["福島市", "郡山市", "いわき市"],
        "茨城県": ["水戸市", "つくば市", "日立市"],
        "栃木県": ["宇都宮市", "小山市", "足利市"],
        "群馬県": ["前橋市", "高崎市", "太田市"],
        "埼玉県": ["さいたま市", "川口市", "川越市"],
        "千葉県": ["千葉市", "船橋市", "柏市"],
        "東京都": ["新宿区", "渋谷区", "港区"],
        "神奈川県": ["横浜市", "川崎市", "相模原市"],
        "新潟県": ["新潟市", "長岡市", "上越市"],
        "富山県": ["富山市", "高岡市", "射水市"],
        "石川県": ["金沢市", "小松市", "白山市"],
        "福井県": ["福井市", "敦賀市", "坂井市"],
        "山梨県": ["甲府市", "富士吉田市", "甲斐市"],
        "長野県": ["長野市", "松本市", "上田市"],
        "岐阜県": ["岐阜市", "大垣市", "各務原市"],
        "静岡県": ["静岡市", "浜松市", "沼津市"],
        "愛知県": ["名古屋市", "豊田市", "岡崎市"],
        "三重県": ["津市", "四日市市", "鈴鹿市"],
        "滋賀県": ["大津市", "草津市", "長浜市"],
        "京都府": ["京都市", "宇治市", "舞鶴市"],
        "大阪府": ["大阪市", "堺市", "東大阪市"],
        "兵庫県": ["神戸市", "姫路市", "西宮市"],
        "奈良県": ["奈良市", "橿原市", "生駒市"],
        "和歌山県": ["和歌山市", "田辺市", "橋本市"],
        "鳥取県": ["鳥取市", "米子市", "倉吉市"],
        "島根県": ["松江市", "出雲市", "浜田市"],
        "岡山県": ["岡山市", "倉敷市", "津山市"],
        "広島県": ["広島市", "福山市", "呉市"],
        "山口県": ["山口市", "下関市", "宇部市"],
        "徳島県": ["徳島市", "阿南市", "鳴門市"],
        "香川県": ["高松市", "丸亀市", "三豊市"],
        "愛媛県": ["松山市", "今治市", "新居浜市"],
        "高知県": ["高知市", "南国市", "四万十市"],
        "福岡県": ["福岡市", "北九州市", "久留米市"],
        "佐賀県": ["佐賀市", "唐津市", "鳥栖市"],
        "長崎県": ["長崎市", "佐世保市", "諫早市"],
        "熊本県": ["熊本市", "八代市", "天草市"],
        "大分県": ["大分市", "別府市", "中津市"],
        "宮崎県": ["宮崎市", "都城市", "延岡市"],
        "鹿児島県": ["鹿児島市", "霧島市", "薩摩川内市"],
        "沖縄県": ["那覇市", "沖縄市", "うるま市"],
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

    if not hasattr(page, "weather_icon_url"):
        page.weather_icon_url = ""

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
            page.weather_icon_url = data.get("daily_icon_url", "取得失敗")
        except Exception as ex:
            fashion_text = f"エラー発生: {ex}"
            page.weather_icon_url = ""
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

    # 吹き出し形式のコンテナを生成
    def create_speech_bubble(content: str) -> ft.Container:
        content_widgets = []
    
        if page.weather_icon_url:
            content_widgets.append(
                ft.Image(
                    src=page.weather_icon_url,
                    width=50,
                    height=50,
                    fit=ft.ImageFit.CONTAIN,
                )
            )
    
        content_widgets.append(ft.Markdown(content))
    
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.icons.FACE, size=30),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=10),
                    ),
                    ft.Container(
                        content=ft.Column(
                            content_widgets,
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10,
                        ),
                        padding=20,
                        bgcolor=ft.colors.with_opacity(0.2, ft.colors.SURFACE_VARIANT),
                        border_radius=10,
                        width=300,
                        expand=True,
                    ),
                ],
                alignment="start",
                spacing=15,
                vertical_alignment="start",
            ),
            padding=ft.padding.only(left=50, right=50, top=10, bottom=10), 
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
                        create_speech_bubble(fashion_text),
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
            
            page.views.append(
                common_view(
                    "服装の確認",
                    [
                        create_speech_bubble(fashion_text),
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
                            create_blue_button("登録", on_click=add_cloth)
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