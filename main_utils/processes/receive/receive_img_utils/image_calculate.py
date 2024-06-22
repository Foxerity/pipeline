from PIL import Image
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn.functional as f

from skimage.metrics import structural_similarity as ssim
from skimage.transform import resize

from pipeline_abc import Pipeline


class ImageCalculator(Pipeline):
    def __init__(self):
        super().__init__()
        self.device = None
        self.PerceptualLoss = None

    def setup(self, **kwargs):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.modules = [
            PerceptualLoss(feature_layer=['conv4_4', 'conv5_4']).to(self.device)
        ]
        self.initialize_modules()

    @staticmethod
    def load_image_to_tensor(image_path):
        """
        图像---tensor。
        """
        image = Image.open(image_path)
        image = np.array(image)  # 将PIL图像转换为numpy数组
        image = torch.from_numpy(image)  # 将numpy数组转换为PyTorch张量
        # 确保图像是float32类型，并且CHW格式
        image = image.float().permute(2, 0, 1)  # 从HWC转换到CHW格式
        return image

    @staticmethod
    def calculate_ssim(self, img1, img2):
        image1 = np.array(img1).astype(np.float32)
        image2 = np.array(img2).astype(np.float32)
        height, width = image1.shape[:2]
        image2 = resize(image2, (height, width), anti_aliasing=True)

        score, diff = ssim(image1, image2, full=True, channel_axis=-1, data_range=1.0)
        # score 是一个介于 -1 和 1 之间的值，1 表示两幅图像完全相同
        # diff 是一个灰度图像，显示两幅图像之间的差异
        return score

    # 感知损失中图像预处理
    @staticmethod
    def preprocess_image_ploss(img):
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        image = img.convert('RGB')
        image = transform(image).unsqueeze(0)
        return image

    # P S N R
    @staticmethod
    def calculate_psnr(img1, img2):
        mse = f.mse_loss(img1, img2)
        if mse == 0:
            return float('inf')
        max_pixel_value = 255.0
        psnr = 20 * torch.log10(max_pixel_value / torch.sqrt(mse))
        return psnr.item()

    # PSNR中图像预处理
    @staticmethod
    def preprocess_image_psnr(image):
        image = image.convert('RGB')
        image = torch.tensor(np.array(image), dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        return image

    def overall_semantic_evaluation(self, img1_path, img2_path):
        img1_psnr = self.preprocess_image_psnr(img1_path)
        img2_psnr = self.preprocess_image_psnr(img2_path)
        psnr_value = self.calculate_psnr(img1_psnr, img2_psnr)
        if psnr_value > 20:
            psnr_value = 20
        psnr_value_normalized = psnr_value / 20
        print(psnr_value_normalized)

        img1_ploss = self.preprocess_image_ploss(img1_path).to(self.device)
        img2_ploss = self.preprocess_image_ploss(img2_path).to(self.device)
        perceptual_loss = self.PerceptualLoss(img1_ploss, img2_ploss)
        perceptual_loss = perceptual_loss.item()
        perceptual_loss_normalized = 1.0 - perceptual_loss
        print(perceptual_loss_normalized)

        print("---------------")
        ssim_value = self.calculate_ssim(img1_path, img2_path)
        print(ssim_value)

        w_ssim = 0.15
        w_psnr = 0.8
        w_perceptual = 0.05
        weighted_sum = w_ssim * ssim_value + w_psnr * psnr_value_normalized + w_perceptual * perceptual_loss_normalized

        return weighted_sum


# # 感 知 损 失
class PerceptualLoss(nn.Module):
    def __init__(self, feature_layer=None):
        super(PerceptualLoss, self).__init__()
        if feature_layer is None:
            feature_layer = ['conv3_3']
        self.vgg = models.vgg19(pretrained=True).features
        self.feature_layer = feature_layer
        self.layers = {'0': 'conv1_1', '2': 'conv1_2', '5': 'conv2_1', '7': 'conv2_2',
                       '10': 'conv3_1', '12': 'conv3_2', '14': 'conv3_3', '16': 'conv3_4',
                       '19': 'conv4_1', '21': 'conv4_2', '23': 'conv4_3', '25': 'conv4_4',
                       '28': 'conv5_1', '30': 'conv5_2', '32': 'conv5_3', '34': 'conv5_4'}
        for param in self.vgg.parameters():
            param.requires_grad = False

    def forward(self, x, y):
        x = self._extract_features(x)
        y = self._extract_features(y)
        loss = 0
        for l in self.feature_layer:
            loss += torch.nn.functional.mse_loss(x[l], y[l])
        return loss

    def _extract_features(self, x):
        features = {}
        for name, layer in self.vgg._modules.items():
            x = layer(x)
            if name in self.layers:
                features[self.layers[name]] = x
        return features



