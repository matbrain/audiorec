import threading

import flet as ft
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write


def main(page: ft.Page):
    info = sd.query_devices(sd.default.device[0])
    name = info["name"]
    print(name)
    sample_rate = int(info["default_samplerate"])
    print(sample_rate)

    page.title = "音声録音アプリ"
    page.focused = True
    is_recording = False
    recording_thread = None
    audio_data = []
    # sample_rate = 48000  # 44100

    texts: list[str] = [
        "こんにちは！",
        "FletでGUIを作っています。",
        "矢印キーでテキストが切り替わります。",
        "左キーで戻り、右キーで次へ。",
        "お疲れさまでした！"
    ]

    current_index = 0

    text_display = ft.Text(
        value=texts[current_index],
        size=50,
        color=ft.Colors.BLACK,
        text_align=ft.TextAlign.CENTER,
        expand=True,
        max_lines=4,
        overflow=ft.TextOverflow.ELLIPSIS,
        selectable=False,
        width=page.width,
        # height=page.height * 0.6,
    )
    index_display = ft.Text(
        value=f"{current_index + 1} / {len(texts)}",
        size=30,
        color=ft.Colors.BLACK,
        text_align=ft.TextAlign.CENTER,
    )
    status_text = ft.Text(
        value="Enterキーで録音開始",
        size=30,
        text_align=ft.TextAlign.CENTER
    )

    def record():
        nonlocal audio_data
        audio_data = []

        def callback(indata, frames, time, status):
            audio_data.append(indata.copy())

        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            while is_recording:
                sd.sleep(100)  # 0.1秒ごとにループしてチェック

    def on_keyboard(e: ft.KeyboardEvent):
        nonlocal current_index
        nonlocal is_recording, recording_thread, audio_data

        if e.key == "Enter":
            if not is_recording:
                # 録音開始
                print("is_recording")
                is_recording = True
                status_text.value = "録音中... Enterで停止"
                recording_thread = threading.Thread(target=record)
                recording_thread.start()
            else:
                # 録音停止
                is_recording = False
                recording_thread.join()
                status_text.value = "録音完了！ファイル保存中..."

                # 音声をWAVに保存
                recorded = np.concatenate(audio_data, axis=0)
                write("recorded_audio.wav", sample_rate, recorded)

                status_text.value = "録音完了！Enterで再録音"
        elif e.key == "Arrow Right" and current_index < len(texts) - 1:
            current_index += 1
        elif e.key == "Arrow Left" and current_index > 0:
            current_index -= 1

        text_display.value = texts[current_index]
        index_display.value = f"{current_index + 1} / {len(texts)}"
        page.update()

    page.on_keyboard_event = on_keyboard

    # レイアウトを中央に配置
    page.add(
        ft.Column(
            [
                text_display,
                status_text,
                index_display,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    )


ft.app(main)
