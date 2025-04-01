import pandas as pd
import csv

# Создаем словарь преобразования из старых индексов в новые.
original_to_new = {
    68: 0,    # Keeping still
    133: 1,   # Walking
    40: 2,    # Eating
    78: 3,    # Moving
    100: 4,   # Running
    38: 5,    # Drinking
    1: 6,     # Attacking
    47: 7,    # Fighting
    26: 8,    # Displaying Defensive Pose
    116: 9,  # Standing
    108: 10,  # Sitting
    95: 11,   # Resting
    70: 12    # Lying Down
}

# Допустимые действия – это все ключи, кроме "Biting" (ключ 8).
allowed_keys = set(original_to_new.keys())

def update_labels(input_csv, output_csv):
    # Читаем файл, где столбцы разделены пробелами.
    # Формат строки: video_id, video_numeric, frame_id, path, labels
    df = pd.read_csv(
        input_csv,
        delim_whitespace=True,
        header=None,
        names=["video_id", "video_numeric", "frame_id", "path", "labels"]
    )
    
    def remap_labels(label_str):
        # Разбиваем строку на токены по запятым
        tokens = [token.strip() for token in str(label_str).split(",") if token.strip().isdigit()]
        # Если ни одна метка не найдена – возвращаем пустую строку
        if not tokens:
            return ""
        # Если хотя бы один токен не входит в разрешённое множество (allowed_keys), возвращаем None
        if any(int(token) not in allowed_keys for token in tokens):
            return None
        # Если все токены допустимы, преобразуем их в новые индексы
        new_labels = [str(original_to_new[int(token)]) for token in tokens]
        return ",".join(new_labels)
    
    # Применяем преобразование и сохраняем результат в новый столбец "new_labels"
    df["new_labels"] = df["labels"].apply(remap_labels)
    
    # Оставляем только строки, где new_labels не None и не пустой
    df_filtered = df[df["new_labels"].notnull() & (df["new_labels"] != "")]
    
    # Заменяем старые метки новыми
    df_filtered["labels"] = df_filtered["new_labels"]
    df_filtered = df_filtered.drop(columns=["new_labels"])
    
    # Сохраняем результат в новый CSV с пробелом в качестве разделителя, без заголовков и без кавычек.
    df_filtered.to_csv(
        output_csv,
        sep=" ",
        index=False,
        header=False,
        quoting=csv.QUOTE_NONE,
        escapechar="\\"
    )
    print(f"Updated labels saved to {output_csv}")

if __name__ == '__main__':
    # Обновляем файлы для train и val (предполагается, что исходные файлы уже отфильтрованы по видео)
    update_labels("train.csv", "train_new.csv")
    update_labels("val.csv", "val_new.csv")
