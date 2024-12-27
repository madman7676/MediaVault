import librosa
import cv2
import numpy as np
import os
import logging
import json
import time
import subprocess

# Налаштування порогів
FRAME_DIFF_THRESHOLD = 70  # Поріг для визначення зміни кадрів
AUDIO_DELTA = 0.5          # Чутливість до аудіо
AUDIO_WAIT = 20            # Мінімальна відстань між піками у кадрах
MIN_SKIP_DURATION = 10      # Мінімальна тривалість пропуску в секундах
MERGE_GAP = 1             # Максимальний проміжок між інтервалами для об'єднання

def seconds_to_time(seconds):
    """
    Конвертує час у секундах у формат HH:MM.

    Parameters:
        seconds (float): Час у секундах.

    Returns:
        str: Час у форматі HH:MM.
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"


def clear_analysis_cache(video_path=None):
    """
    Видаляє кешовані результати аналізу для конкретного відеофайлу або всіх відеофайлів.

    Parameters:
        video_path (str, optional): Шлях до конкретного відеофайлу. Якщо None, видаляє кеш для всіх файлів.
    """
    if video_path:
        cache_file = f"{video_path}.analysis.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logging.info(f"Cache cleared for file: {cache_file}")
        else:
            logging.warning(f"No cache found for file: {cache_file}")
    else:
        cache_dir = os.getcwd()  # Або вказати папку, де зберігається кеш
        for file in os.listdir(cache_dir):
            if file.endswith(".analysis.json"):
                os.remove(os.path.join(cache_dir, file))
                logging.info(f"Cache cleared for file: {file}")


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_audio_chunk(video_path, start_time, end_time):
    """
    Витягує аудіо частину з відео за допомогою FFmpeg.

    Parameters:
        video_path (str): Шлях до відеофайлу.
        start_time (int): Початок частини у секундах.
        end_time (int): Кінець частини у секундах.

    Returns:
        np.ndarray: Масив аудіоданих.
        int: Частота дискретизації.
    """
    output_path = f"temp_chunk_{start_time}_{end_time}.wav"
    command = [
        "ffmpeg", "-i", video_path,
        "-ss", str(start_time), "-to", str(end_time),
        "-ar", "44100", "-ac", "1", "-y", output_path
    ]

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        y, sr = librosa.load(output_path, sr=None, mono=True)
        os.remove(output_path)
        return y, sr
    except Exception as e:
        logging.error(f"Failed to extract audio chunk: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise

def analyze_audio_in_chunks(video_path, chunk_duration=120, overlap=10):
    """
    Аналізує аудіо файлу частинами, щоб уникнути перевантаження пам'яті.

    Parameters:
        video_path (str): Шлях до відеофайлу.
        chunk_duration (int): Тривалість одного шматка в секундах.
        overlap (int): Перекриття між шматками в секундах.

    Returns:
        list: Список піків звуку у секундах.
    """
    logging.info("Starting audio analysis in chunks...")
    audio_peaks = []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Unsupported video format or file cannot be opened: {video_path}")

    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    for start_time in range(0, int(duration), chunk_duration - overlap):
        end_time = min(start_time + chunk_duration, duration)

        try:
            y, sr = extract_audio_chunk(video_path, start_time, end_time)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            peaks = librosa.util.peak_pick(onset_env, pre_max=10, post_max=10, pre_avg=20, post_avg=20, delta=AUDIO_DELTA, wait=AUDIO_WAIT)

            audio_peaks.extend([peak / sr + start_time for peak in peaks])
        except Exception as e:
            logging.error(f"Audio analysis error for chunk {start_time}-{end_time}: {e}")

    logging.info(f"Audio analysis completed with {len(audio_peaks)} peaks detected.")
    return sorted(set(audio_peaks))

def merge_intervals(intervals, max_gap=MERGE_GAP):
    merged = []
    for interval in intervals:
        start = float(interval["start"])
        end = float(interval["end"])

        if not merged or start > merged[-1]["end"] + max_gap:
            merged.append({"start": start, "end": end})
        else:
            merged[-1]["end"] = max(merged[-1]["end"], end)
    return merged

def analyze_video(video_path):
    """
    Аналізує відео для визначення таймкодів рекомендованих пропусків.

    Parameters:
        video_path (str): Шлях до відеофайлу.

    Returns:
        list: Список таймкодів для пропуску у форматі [{"start": <start>, "end": <end>}].
    """
    logging.info(f"Starting analysis for video: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")

    cache_file = f"{video_path}.analysis.json"
    if os.path.exists(cache_file):
        cache_timestamp = os.path.getmtime(cache_file)
        video_timestamp = os.path.getmtime(video_path)
        if cache_timestamp >= video_timestamp:
            logging.info("Loading analysis results from cache.")
            with open(cache_file, 'r') as f:
                return json.load(f)
        else:
            logging.info("Cache is outdated. Reanalyzing...")

    recommend_to_skip = []

    # --- Аналіз кадрів ---
    logging.info("Analyzing frames...")
    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Unsupported video format or file cannot be opened: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_skip = 5  # Пропуск кожного 5-го кадру

    scene_changes = []
    prev_frame = None
    for i in range(0, frame_count, frame_skip):
        ret, frame = cap.read()
        if not ret:
            break

        if frame is None:
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray_frame)
            diff_score = np.sum(diff) / diff.size

            if diff_score > FRAME_DIFF_THRESHOLD:  # Поріг для визначення зміни сцени
                scene_changes.append(i / fps)

        prev_frame = gray_frame

    cap.release()
    end_time = time.time()
    logging.info(f"Frame analysis completed in {end_time - start_time:.2f} seconds. Detected scene changes: {len(scene_changes)}")

    # --- Аналіз аудіо ---
    logging.info("Analyzing audio...")
    try:
        start_time = time.time()
        audio_peaks = analyze_audio_in_chunks(video_path, chunk_duration=120, overlap=10)
        end_time = time.time()
        logging.info(f"Audio analysis completed in {end_time - start_time:.2f} seconds. Detected audio peaks: {len(audio_peaks)}")
    except Exception as e:
        logging.error(f"Audio analysis error: {e}")
        audio_peaks = []

    # --- Комбінування результатів ---
    logging.info("Combining results...")
    combined_peaks = sorted(set(float(peak) for peak in (scene_changes + audio_peaks)))
    
    # logging.info(f"Combined peaks before processing: {combined_peaks}")

    for i in range(len(combined_peaks) - 1):
        start = float(combined_peaks[i])  # Приводимо до числа
        end = float(combined_peaks[i + 1])  # Приводимо до числа

        if end - start > MIN_SKIP_DURATION:  # Мінімальна тривалість пропуску
            recommend_to_skip.append({"start": start, "end": end})


    recommend_to_skip = merge_intervals(recommend_to_skip, max_gap=MERGE_GAP)

    formatted_recommendations = [
        {"start": seconds_to_time(interval["start"]), "end": seconds_to_time(interval["end"])}
        for interval in recommend_to_skip
    ]

    # Збереження в кеш
    try:
        with open(cache_file, 'w') as f:
            json.dump(formatted_recommendations, f)
        logging.info(f"Analysis results saved to cache: {cache_file}")
    except IOError as e:
        logging.error(f"Failed to write cache: {e}")

    return formatted_recommendations
