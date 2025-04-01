import os
import torch
import argparse
from PIL import Image
import torchvision.transforms as T
import torch.nn.functional as F

from config import cfg
from model.make_model_clipreid import make_model
from utils.logger import setup_logger
from datasets.mpdd import MPDD

val_transforms = T.Compose([
    T.Resize((256, 128)),
    T.ToTensor(),
    T.Normalize(mean=[0.5,0.5,0.5], std=[0.5,0.5,0.5])
])

def load_model(weight_path):
    num_classes = 1
    camera_num = 1
    view_num = 1
    model = make_model(cfg, num_class=num_classes, camera_num=camera_num, view_num=view_num)
    model.load_param(weight_path)
    model.eval()
    return model

def build_gallery(model, dataset_root, device):
    """Собираем галерею из датасета MPDD (у которого внутри dataset_root есть папка MPDD)."""
    dataset = MPDD(root=dataset_root)
    gallery_list = dataset.gallery
    gallery_features = []
    gallery_ids = []
    model.to(device)
    model.eval()
    with torch.no_grad():
        for (img_path, pid, _, _) in gallery_list:
            try:
                img = Image.open(img_path).convert('RGB')
            except Exception as e:
                print(f"Ошибка открытия {img_path}: {e}")
                continue
            img_tensor = val_transforms(img).unsqueeze(0).to(device)
            feat = model(img_tensor, cam_label=None, view_label=None)
            gallery_features.append(feat.cpu())
            gallery_ids.append(pid)
    if gallery_features:
        gallery_features = torch.cat(gallery_features, dim=0).to(device)
    else:
        gallery_features = torch.empty((0, 0)).to(device)
    return gallery_features, gallery_ids

def run_inference(model, input_image, device):
    try:
        img = Image.open(input_image).convert('RGB')
    except Exception as e:
        print(f"Ошибка открытия {input_image}: {e}")
        return None
    img_tensor = val_transforms(img).unsqueeze(0).to(device)
    with torch.no_grad():
        feat = model(img_tensor, cam_label=None, view_label=None)
    return feat

def main():
    parser = argparse.ArgumentParser(description="Inference for Dog Image with Gallery Matching")
    parser.add_argument("--config_file", default="configs/MPDD/vit_clipreid.yml", type=str)
    parser.add_argument("--weight_file", default="./logs/mpdd/ViT-B-16_30.pth", type=str)
    parser.add_argument("--input_image", required=True, type=str, help="Path to input image")
    parser.add_argument("--dataset_root", default="/mnt/c/reID/data", type=str,
                        help="Inside should be MPDD subfolder with train/query/gallery data")
    parser.add_argument("--device", default="cuda", type=str)
    args = parser.parse_args()
    
    if args.config_file:
        cfg.merge_from_file(args.config_file)
    cfg.freeze()
    
    output_dir = cfg.OUTPUT_DIR
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    logger = setup_logger("transreid_inference", output_dir, if_train=False)
    
    os.environ['CUDA_VISIBLE_DEVICES'] = cfg.MODEL.DEVICE_ID
    device = args.device

    model = load_model(args.weight_file)
    model.to(device)
    model.eval()
    
    gallery_features, gallery_ids = build_gallery(model, dataset_root=args.dataset_root, device=device)
    if gallery_features.shape[0] == 0:
        print("Gallery пуста, невозможно выполнить сопоставление.")
        return
    
    feat = run_inference(model, args.input_image, device)
    if feat is None:
        print("Inference failed.")
        return

    sim = F.cosine_similarity(feat, gallery_features, dim=1)
    best_index = torch.argmax(sim).item()
    best_sim = sim[best_index].item()
    pred_id = gallery_ids[best_index]
    print(f"Predicted dog id: {pred_id}, similarity: {best_sim:.4f}")

if __name__ == "__main__":
    main()
