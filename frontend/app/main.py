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
    page.title = "Flet + FastAPI + Gemini (Docker)"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    prompt_input = ft.TextField(
        label="Geminiへの指示を入力",
        hint_text="例: Dockerについて簡単に説明して",
        multiline=True,
        min_lines=3,
        max_lines=5,
        expand=True,
    )

    result_text = ft.Text("ここに結果が表示されます。", selectable=True)
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    error_text = ft.Text("", color=ft.colors.RED, weight=ft.FontWeight.BOLD, visible=False)

    def generate_clicked(e):
        prompt = prompt_input.value
        if not prompt:
            error_text.value = "プロンプトを入力してください。"
            error_text.visible = True
            result_text.value = ""
            page.update()
            return

        progress_ring.visible = True
        error_text.visible = False
        result_text.value = "生成中..."
        generate_button.disabled = True
        page.update()

        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"prompt": prompt}),
                timeout=60 # タイムアウトを設定 (必要に応じて調整)
            )
            response.raise_for_status() # HTTPエラーチェック

            data = response.json()
            result_text.value = data.get("generated_text", "結果の取得に失敗しました。")

        except requests.exceptions.Timeout:
             error_text.value = f"バックエンドへの接続がタイムアウトしました ({API_URL})"
             error_text.visible = True
             result_text.value = ""
        except requests.exceptions.ConnectionError:
             error_text.value = f"バックエンドに接続できません ({API_URL})。バックエンドは起動していますか？"
             error_text.visible = True
             result_text.value = ""
        except requests.exceptions.RequestException as req_err:
            error_detail = f"リクエストエラー: {req_err}"
            if req_err.response is not None:
                error_detail += f"\nStatus: {req_err.response.status_code}"
                try:
                    error_data = req_err.response.json()
                    error_detail += f"\nDetail: {error_data.get('detail', req_err.response.text[:200])}"
                except json.JSONDecodeError:
                    error_detail += f"\nResponse: {req_err.response.text[:200]}"
            error_text.value = error_detail
            error_text.visible = True
            result_text.value = ""
        except Exception as ex:
            error_text.value = f"予期せぬエラー: {ex}"
            error_text.visible = True
            result_text.value = ""
        finally:
            progress_ring.visible = False
            generate_button.disabled = False
            page.update()

    generate_button = ft.ElevatedButton("テキスト生成", on_click=generate_clicked)

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    prompt_input,
                    ft.Row(
                        [generate_button, progress_ring],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    error_text,
                    ft.Text("生成されたテキスト:", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=result_text,
                        padding=ft.padding.all(10),
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=ft.border_radius.all(5),
                        margin=ft.margin.only(top=5),
                    )
                ],
                spacing=10,
            ),
            padding=20,
            width=600,
            alignment=ft.alignment.center,
        )
    )

# Docker内でWebアプリとして実行
# ホスト 0.0.0.0 を指定し、ポートを固定
# view=ft.AppView.WEB_BROWSER は flet run コマンドのデフォルトなので不要な場合も
ft.app(target=main, port=FLET_PORT, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)