import speech_recognition as sr
import pyaudio
import numpy as np


# Функция обработки аудиоданных
def audio_callback(in_data, frame_count, time_info, status):
    # Преобразуем байты в массив NumPy
    audio_data = np.frombuffer(in_data, dtype=np.float32)

    # Вычисляем среднее значение амплитуды
    amplitude_mean = np.mean(np.abs(audio_data))

    # Устанавливаем пороговое значение для шума
    threshold = 0.01

    # Если среднее значение амплитуды превышает порог, считаем, что есть шум
    if amplitude_mean > threshold:
        print("Обнаружен шум!")

    return None, pyaudio.paContinue

# Настройки аудиоустройства
sample_rate = 48000
chunk_size = 1024

# Создаем объект PyAudio
audio = pyaudio.PyAudio()

# Открываем аудиоустройство для записи
stream = audio.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size,
                    stream_callback=audio_callback)

# Запускаем мониторинг аудио
stream.start_stream()

# Ждем, пока поток мониторинга не будет остановлен
while stream.is_active():
    pass

# Останавливаем поток и закрываем аудиоустройство
stream.stop_stream()
stream.close()

# Завершаем работу с объектом PyAudio
audio.terminate()
