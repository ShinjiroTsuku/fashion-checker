# frontend/app/main.py
import flet as ft
import requests
import json
import os
import time

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
FLET_PORT = int(os.getenv("FLET_PORT", 8550))

# テーマカラーを定義
PRIMARY_COLOR = ft.colors.BLUE_700
SECONDARY_COLOR = ft.colors.LIGHT_BLUE_200
ACCENT_COLOR = ft.colors.AMBER_600
BACKGROUND_COLOR = ft.colors.WHITE
TEXT_COLOR = ft.colors.BLUE_GREY_900

def main(page: ft.Page):
    page.title = "Fashion Checker"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BACKGROUND_COLOR
    
    # カスタムテーマの設定
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY_COLOR,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    
    # フォントを設定
    page.fonts = {
        "Noto Sans JP": "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap",
    }
    
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
    
    # 上部ナビゲーションバー
    def create_navbar():
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.HOME,
                        icon_color=PRIMARY_COLOR,
                        icon_size=28,
                        tooltip="ホーム",
                        on_click=lambda _: page.go("/"),
                    ),
                    ft.Text("Fashion Checker", 
                           size=28, 
                           weight=ft.FontWeight.W_600, 
                           color=PRIMARY_COLOR),
                    ft.IconButton(
                        icon=ft.icons.LIST_ALT,
                        icon_color=PRIMARY_COLOR,
                        icon_size=28,
                        tooltip="服一覧",
                        on_click=lambda _: page.go("/list"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(20),
            bgcolor=BACKGROUND_COLOR,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
        )

    # ボタン有効化チェック
    def update_view_button_state(e=None):
        if fashion_button.current is None:
            return
        enabled = bool(selected_city.current.value)
        fashion_button.current.disabled = not enabled
        fashion_button.current.bgcolor = PRIMARY_COLOR if enabled else ft.colors.GREY_300
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
            show_snackbar("服の名前を入力してください")
            return

        try:
            # アニメーション効果を追加
            page.splash = ft.ProgressBar(visible=True, color=PRIMARY_COLOR)
            page.update()
            
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
            
            # 完了後にプログレスバーを非表示
            page.splash.visible = False
            page.update()
            
            show_snackbar(f"'{name}'を登録しました")
            page.go("/list")
            
        except Exception as e:
            page.splash.visible = False
            page.update()
            show_snackbar(f"エラー発生: {e}")

    # スナックバー表示関数
    def show_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="閉じる",
            bgcolor=ACCENT_COLOR,
        )
        page.snack_bar.open = True
        page.update()
    
    def delete_cloth(e, item_name):
        try:
            # 削除確認ダイアログ
            def confirm_delete(e):
                page.dialog.open = False
                page.update()
                
                # 削除処理
                try:
                    # ローディングアニメーション
                    page.splash = ft.ProgressBar(visible=True, color=PRIMARY_COLOR)
                    page.update()
                    
                    json_data = json.dumps({"name": item_name})
                    response = requests.post(
                        f"{API_BASE_URL}/delete",
                        data=json_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    response.raise_for_status()
                    data = response.json()
                    page.cloth_list = data
                    
                    page.splash.visible = False
                    page.update()
                    
                    show_snackbar(f"'{item_name}'を削除しました")
                    
                    page.views.pop()
                    page.route = "/list"
                    route_change(None)
                    
                except Exception as e:
                    page.splash.visible = False
                    page.update()
                    show_snackbar(f"削除エラー: {e}")
            
            # 確認ダイアログを表示
            page.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"'{item_name}'を削除しますか？"),
                content=ft.Text("この操作は元に戻せません。"),
                actions=[
                    ft.TextButton("キャンセル", on_click=lambda e: setattr(page.dialog, "open", False)),
                    ft.TextButton("削除", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.colors.RED_600)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog.open = True
            page.update()

        except Exception as e:
            show_snackbar(f"エラー発生: {e}")

    if not hasattr(page, "weather_icon_url"):
        page.weather_icon_url = ""

    # 服のリストを取得する関数を追加
    def fetch_clothes_list():
        try:
            response = requests.get(
                f"{API_BASE_URL}/list",  # 新しいエンドポイントを追加する必要があります
                timeout=10
            )
            response.raise_for_status()
            page.cloth_list = response.json()
            page.update()
        except Exception as e:
            print(f"服のリスト取得エラー: {e}")
            # エラー時は空のリストを設定
            if not hasattr(page, "cloth_list"):
                page.cloth_list = []

    # 服装アドバイス取得
    def fetch_fashion_advice(e=None):
        nonlocal fashion_text

        if not selected_city.current.value:
            show_snackbar("市区町村を選択してください")
            return

        # ローディング開始
        fashion_button.current.disabled = True
        loading.current.visible = True
        page.update()

        name = f"{selected_prefecture.current.value}_{selected_city.current.value}"
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json={"name": name},
                timeout=20  # 生成AIの応答を待つ時間を長めに
            )
            response.raise_for_status()
            data = response.json()
            fashion_text = data.get("generated_text", "取得失敗")
            page.weather_icon_url = data.get("daily_icon_url", "")
            # ローディング終了
            loading.current.visible = False
            fashion_button.current.disabled = False
            
            # 成功メッセージ
            show_snackbar(f"{selected_prefecture.current.value}{selected_city.current.value}の服装提案を生成しました")
            page.go("/confirm")
            
        except Exception as ex:
            # エラー処理
            loading.current.visible = False
            fashion_button.current.disabled = False
            page.update()
            
            fashion_text = f"エラー発生: {ex}"
            page.weather_icon_url = ""
            show_snackbar(f"サーバーとの通信エラー: {ex}")

    # スタイリッシュなプライマリボタン
    def create_primary_button(text, on_click, width=250, icon=None, ref=None, disabled=False):
        button = ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR if not disabled else ft.colors.GREY_300,
                color=ft.colors.WHITE if not disabled else ft.colors.GREY_600,
                padding=16,
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=3,
                animation_duration=300,
                shadow_color=ft.colors.with_opacity(0.3, PRIMARY_COLOR),
            ),
            width=width,
            disabled=disabled,
        )
        
        if ref is not None:
            ref.current = button
        
        return button

    # スタイリッシュなセカンダリボタン
    def create_secondary_button(text, on_click, width=250, icon=None):
        return ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.WHITE,
                color=PRIMARY_COLOR,
                padding=16,
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(width=1, color=PRIMARY_COLOR),
                elevation=0,
                animation_duration=300,
            ),
            width=width,
        )

    # スタイリッシュなカード
    def create_card(content, width=None, height=None, on_click=None):
        return ft.Container(
            content=content,
            width=width,
            height=height,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.FAST_OUT_SLOWIN),
            on_click=on_click,
            padding=20,
        )

    # 共通ビューのレイアウト
    def common_view(title, controls, show_navbar=True):
        view_controls = []
        
        if show_navbar:
            view_controls.append(create_navbar())
        
        content_controls = [
            ft.Container(
                content=ft.Text(
                    title, 
                    size=36, 
                    weight=ft.FontWeight.W_500, 
                    color=PRIMARY_COLOR,
                    text_align="center",
                ),
                margin=ft.margin.only(top=20, bottom=20),
            )
        ] + controls
        
        view_controls.append(
            ft.Container(
                content=ft.Column(
                    content_controls,
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=20,
                ),
                expand=True,
                padding=ft.padding.only(left=20, right=20),
            )
        )
        
        return ft.View(
            route=page.route,
            controls=view_controls,
            vertical_alignment="start",
            horizontal_alignment="stretch",
            padding=0,
        )

    # 吹き出し形式のコンテナを生成（スタイリッシュにリデザイン）
    def create_speech_bubble(content: str) -> ft.Container:
        weather_section = None
        if page.weather_icon_url:
            weather_section = ft.Container(
                content=ft.Row([
                    ft.Image(
                        src=page.weather_icon_url,
                        width=64,
                        height=64,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Text("今日の天気", size=16, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
                ]),
                bgcolor=SECONDARY_COLOR,
                padding=10,
                border_radius=ft.border_radius.only(
                    top_left=8, top_right=8, bottom_left=0, bottom_right=0
                ),
            )

        return ft.Container(
            content=ft.Column([
                weather_section if weather_section else ft.Container(),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [ft.Markdown(
                                        content,
                                        selectable=True,
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    )],
                                    spacing=10,
                                ),
                                padding=20,
                                bgcolor=ft.colors.WHITE,
                                width=None,
                                expand=True,
                            ),
                        ],
                        alignment="start",
                        vertical_alignment="start",
                    ),
                    border_radius=ft.border_radius.only(
                        top_left=0 if weather_section else 8, 
                        top_right=0 if weather_section else 8, 
                        bottom_left=8, 
                        bottom_right=8
                    ),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                        offset=ft.Offset(0, 2),
                    ),
                )
            ]),
            padding=ft.padding.symmetric(horizontal=20),
            margin=ft.margin.symmetric(vertical=10),
        )

    # 共通ビューのレイアウト
    def common_view(title, controls, show_navbar=True):
        view_controls = []
        
        if show_navbar:
            view_controls.append(create_navbar())
        
        content_controls = [
            ft.Container(
                content=ft.Text(
                    title, 
                    size=36, 
                    weight=ft.FontWeight.W_500, 
                    color=PRIMARY_COLOR,
                    text_align="center",
                ),
                margin=ft.margin.only(top=20, bottom=20),
            )
        ] + controls
        
        view_controls.append(
            ft.Container(
                content=ft.Column(
                    content_controls,
                    alignment="start",  # centerからstartに変更
                    horizontal_alignment="center",
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,  # スクロール可能に設定
                ),
                expand=True,
                padding=ft.padding.only(left=20, right=20, bottom=20),  # 下部にもパディングを追加
            )
        )
        
        return ft.View(
            route=page.route,
            controls=view_controls,
            vertical_alignment="start",
            horizontal_alignment="stretch",
            padding=0,
            scroll=ft.ScrollMode.AUTO,  # View自体もスクロール可能に設定
        )
    
    # 服のアイテムカードを作成
    def create_clothes_item(item):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.CHECKROOM, color=PRIMARY_COLOR),
                    ft.Text(
                        item,
                        size=16,
                        weight=ft.FontWeight.W_500,
                        color=TEXT_COLOR,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.RED_400,
                        tooltip="削除",
                        on_click=lambda e, item=item: delete_cloth(e, item),
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=3,
                color=ft.colors.with_opacity(0.05, ft.colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE),
            animate_opacity=200,
            margin=ft.margin.only(bottom=8),
        )

    # ルートハンドリング
    def route_change(route):
        page.views.clear()

        # /list ルートに移動したときにリストを取得
        if page.route == "/list":
            fetch_clothes_list()

        if page.route == "/":
            page.views.append(
                common_view(
                    "今日の服装を提案してもらおう",
                    [
                        create_card(
                            ft.Column([
                                ft.Text("地域を選択してください", size=16, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                                ft.Row([
                                    ft.Dropdown(
                                        ref=selected_prefecture,
                                        label="都道府県",
                                        hint_text="選択してください",
                                        options=[ft.dropdown.Option(pref) for pref in prefecture_city_data.keys()],
                                        on_change=update_cities,
                                        width=180,
                                        filled=True,
                                        border_color=PRIMARY_COLOR,
                                        focused_border_color=PRIMARY_COLOR,
                                        focused_bgcolor=ft.colors.with_opacity(0.05, PRIMARY_COLOR),
                                    ),
                                    ft.Dropdown(
                                        ref=selected_city,
                                        label="市区町村",
                                        hint_text="選択してください",
                                        options=[],
                                        on_change=update_view_button_state,
                                        width=180,
                                        filled=True,
                                        border_color=PRIMARY_COLOR,
                                        focused_border_color=PRIMARY_COLOR,
                                        focused_bgcolor=ft.colors.with_opacity(0.05, PRIMARY_COLOR),
                                    )
                                ], alignment="center", spacing=20),
                            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                            width=500,
                        ),

                        ft.Stack([
                            create_primary_button(
                                "服装提案を見る",
                                ref=fashion_button,
                                on_click=fetch_fashion_advice,
                                disabled=True,
                                icon=ft.icons.STYLE,
                                width=300,
                            ),
                            ft.ProgressRing(
                                ref=loading, 
                                visible=False, 
                                width=24, 
                                height=24, 
                                stroke_width=3, 
                                color=ft.colors.WHITE
                            ),
                        ], width=300, height=60),
                        
                        ft.Container(
                            content=ft.Row([
                                ft.TextButton(
                                    "服一覧を管理する",
                                    icon=ft.icons.LIST_ALT,
                                    on_click=lambda _: page.go("/list"),
                                    style=ft.ButtonStyle(
                                        color=PRIMARY_COLOR,
                                    ),
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            margin=ft.margin.only(top=20),
                        ),
                    ]
                )
            )

        elif page.route == "/confirm":
            page.views.append(
                common_view(
                    "あなたにおすすめの服装",
                    [
                        create_speech_bubble(fashion_text),
                        ft.Container(
                            content=ft.Row(
                                [
                                    create_secondary_button(
                                        "戻る", 
                                        on_click=lambda _: page.go("/"), 
                                        icon=ft.icons.ARROW_BACK,
                                        width=180
                                    ),
                                    create_primary_button(
                                        "再生成", 
                                        on_click=lambda _: fetch_fashion_advice(), 
                                        icon=ft.icons.REFRESH,
                                        width=180
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            margin=ft.margin.only(top=20, bottom=40),
                        ),
                    ]
                )
            )

        # list画面
        elif page.route == "/list":
            controls = [
                ft.Container(
                    content=ft.Text("あなたの持っている服", size=16, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                    margin=ft.margin.only(bottom=10),
                ),
            ]

            # 服のリストをスタイリッシュなカードスタイルで表示
            if hasattr(page, "cloth_list") and page.cloth_list:
                clothes_container = ft.Container(
                    content=ft.Column(
                        [create_clothes_item(item) for item in page.cloth_list],
                        spacing=5,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.colors.with_opacity(0.03, PRIMARY_COLOR),
                    height=300,
                    width=500,
                )
                controls.append(clothes_container)
            else:
                controls.append(
                    create_card(
                        ft.Column([
                            ft.Icon(ft.icons.CHECKROOM_OUTLINED, size=48, color=ft.colors.GREY_400),
                            ft.Text("服が登録されていません", size=16, color=ft.colors.GREY_600),
                            ft.Text("「服を登録する」から服を追加してください", size=14, color=ft.colors.GREY_500),
                        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=500,
                        height=200,
                    )
                )

            # ボタン
            controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            create_secondary_button(
                                "戻る", 
                                on_click=lambda _: page.go("/"), 
                                icon=ft.icons.ARROW_BACK,
                                width=180
                            ),
                            create_primary_button(
                                "服を登録する", 
                                on_click=lambda _: page.go("/register"), 
                                icon=ft.icons.ADD,
                                width=180
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    margin=ft.margin.only(top=20, bottom=40),
                )
            )

            page.views.append(
                common_view("服一覧", controls)
            )
            
        elif page.route == "/register":
            page.views.append(
                common_view(
                    "新しい服を登録",
                    [
                        create_card(
                            ft.Column([
                                ft.TextField(
                                    ref=cloth_name_field,
                                    label="服の名称",
                                    hint_text="例: 白Tシャツ、黒スラックス、デニムジャケット",
                                    border_color=PRIMARY_COLOR,
                                    focused_border_color=PRIMARY_COLOR,
                                    prefix_icon=ft.icons.CHECKROOM,
                                    width=400,
                                ),
                                ft.Dropdown(
                                    label="カテゴリ",
                                    hint_text="選択してください",
                                    options=[
                                        ft.dropdown.Option("トップス"),
                                        ft.dropdown.Option("ボトムス"),
                                        ft.dropdown.Option("アウター"),
                                        ft.dropdown.Option("シューズ"),
                                        ft.dropdown.Option("アクセサリー"),
                                    ],
                                    filled=True,
                                    border_color=PRIMARY_COLOR,
                                    focused_border_color=PRIMARY_COLOR,
                                    width=400,
                                )
                            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                            width=500,
                        ),
                        
                        ft.Container(
                            content=ft.Row([
                                create_secondary_button(
                                    "キャンセル", 
                                    on_click=lambda _: page.go("/list"), 
                                    icon=ft.icons.CANCEL,
                                    width=180
                                ),
                                create_primary_button(
                                    "登録する", 
                                    on_click=add_cloth, 
                                    icon=ft.icons.CHECK,
                                    width=180
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                            margin=ft.margin.only(top=20),
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
    # 初期データの取得
    fetch_clothes_list()
    page.go(page.route)

ft.app(target=main, port=FLET_PORT, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)