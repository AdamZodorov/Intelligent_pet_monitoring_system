import os
import glob
import argparse
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

def load_image(image_path, transform):
    """Загружает изображение и применяет предобработку."""
    img = Image.open(image_path).convert('RGB')
    return transform(img)

def compute_embedding(model, image, device):
    """
    Вычисляет эмбеддинг для одного изображения.
    Предполагается, что модель возвращает вектор признаков.
    """
    image = image.unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model(image)
    # Нормализуем эмбеддинг (если модель не нормализует автоматически)
    embedding = F.normalize(embedding, dim=1)
    return embedding.squeeze(0).cpu()

def build_gallery(model, gallery_dir, transform, device):
    """
    Для каждого субкаталога в gallery_dir (каждая папка соответствует одной собаке)
    вычисляет эмбеддинги всех изображений и усредняет их.
    """
    gallery_embeddings = {}
    # Перебираем подпапки — каждая папка называется, например, dog_01, dog_02 и т.д.
    for dog_id in sorted(os.listdir(gallery_dir)):
        dog_folder = os.path.join(gallery_dir, dog_id)
        if not os.path.isdir(dog_folder):
            continue
        img_paths = glob.glob(os.path.join(dog_folder, '*.jpg'))
        embeddings = []
        for img_path in img_paths:
            img = load_image(img_path, transform)
            emb = compute_embedding(model, img, device)
            embeddings.append(emb.unsqueeze(0))
        if embeddings:
            # Усредняем эмбеддинги для данного индивида
            avg_emb = torch.cat(embeddings, dim=0).mean(dim=0, keepdim=True)
            avg_emb = F.normalize(avg_emb, dim=1)
            gallery_embeddings[dog_id] = avg_emb
            print(f"Обработана собака {dog_id}: {len(embeddings)} изображений")
    return gallery_embeddings

def recognize_query(model, query_img_path, gallery_embeddings, transform, device):
    """Для данного query изображения находит в галерее наиболее похожего кандидата."""
    img = load_image(query_img_path, transform)
    query_emb = compute_embedding(model, img, device)
    query_emb = query_emb.unsqueeze(0)
    query_emb = F.normalize(query_emb, dim=1)
    best_score = -1
    best_match = None
    for dog_id, gallery_emb in gallery_embeddings.items():
        score = F.cosine_similarity(query_emb, gallery_emb)
        if score.item() > best_score:
            best_score = score.item()
            best_match = dog_id
    return best_match, best_score

def main(args):
    device = torch.device(args.device)
    # Загрузите модель. Здесь предполагается, что модель имеет метод forward,
    # возвращающий эмбеддинг. При необходимости замените этот блок на свой.
    model = torch.load(args.model_checkpoint, map_location=device)
    model.eval()
    print("Модель загружена.")

    # Преобразования должны совпадать с теми, что использовались при обучении.
    transform = transforms.Compose([
        transforms.Resize((args.image_height, args.image_width)),
        transforms.ToTensor(),
        transforms.Normalize(mean=args.pixel_mean, std=args.pixel_std)
    ])

    # Построим галерею: каждая подпапка в gallery_dir соответствует одному классу (одной собаке)
    print("Вычисление эмбеддингов галереи...")
    gallery_embeddings = build_gallery(model, args.gallery_dir, transform, device)

    # Распознавание для новых изображений (query)
    query_img_paths = glob.glob(os.path.join(args.query_dir, '*.jpg'))
    print("Распознавание query изображений...")
    for q_path in query_img_paths:
        best_match, score = recognize_query(model, q_path, gallery_embeddings, transform, device)
        print(f"Изображение {os.path.basename(q_path)} распознано как: {best_match} (сходство: {score:.4f})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Распознавание новых собак на основе обученной модели")
    parser.add_argument('--model_checkpoint', type=str, required=True,
                        help='Путь к файлу с весами модели (например, checkpoint.pth)')
    parser.add_argument('--gallery_dir', type=str, required=True,
                        help='Путь к директории галереи (подпапки — отдельные собаки, около 8 фото в каждой)')
    parser.add_argument('--query_dir', type=str, required=True,
                        help='Путь к директории с query изображениями')
    parser.add_argument('--device', type=str, default='cuda',
                        help='Устройство для вычислений (cuda или cpu)')
    parser.add_argument('--image_height', type=int, default=256,
                        help='Высота изображения (например, 256)')
    parser.add_argument('--image_width', type=int, default=128,
                        help='Ширина изображения (например, 128)')
    parser.add_argument('--pixel_mean', type=float, nargs=3, default=[0.5, 0.5, 0.5],
                        help='Значения mean для нормализации (например, 0.5 0.5 0.5)')
    parser.add_argument('--pixel_std', type=float, nargs=3, default=[0.5, 0.5, 0.5],
                        help='Значения std для нормализации (например, 0.5 0.5 0.5)')
    args = parser.parse_args()
    main(args)
