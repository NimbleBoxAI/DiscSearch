# wrapper for dall-e model

try:
  from daily import *
except ImportError as e:
  import requests
  x = requests.get("https://gist.githubusercontent.com/yashbonde/62df9d16858a43775c22a6af00a8d707/raw/0764da94f5e243b2bca983a94d5d6a4e4a7eb28a/daily.py").content
  with open("daily.py", "wb") as f:
    f.write(x.content)
  from daily import *

import io
import PIL
import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF

from typing import Tuple
from dall_e import map_pixels, unmap_pixels


class DallE:
  # First time loading will take a bit of time because of downloading the weights binaries
  # also note that fetch will return the data as bytes object, so we will need to wrap it
  # with io.BytesIO
  def __init__(self, fp_encoder = None, fp_decoder = None):
    # auto determine the path for to load from, if nothing is given
    # it will automatically download from CDN.
    enc_load = io.BytesIO(
      fetch("https://cdn.openai.com/dall-e/encoder.pkl")
    ) if fp_encoder is None else fp_encoder
    dec_load = io.BytesIO(
      fetch("https://cdn.openai.com/dall-e/decoder.pkl")
    ) if fp_decoder is None else fp_decoder

    # load the models
    self.device = torch.device("cuda:0") if torch.cuda.is_available() else "cpu"
    self.encoder = torch.load(enc_load, map_location = self.device)
    self.decoder = torch.load(dec_load, map_location = self.device)
    self.vocab_size = self.encoder.vocab_size

  def preprocess(self, imglist, target_image_size = 256):
    if not isinstance(imglist, list):
      img = [imglist]

    all_t = []
    for img in imglist:
      s = min(img.size)
      if s < target_image_size:
        raise ValueError(f'min dim for image {s} < {target_image_size}')
          
      r = target_image_size / s
      s = (round(r * img.size[1]), round(r * img.size[0]))
      img = TF.resize(img, s, interpolation=PIL.Image.LANCZOS)
      img = TF.center_crop(img, output_size=2 * [target_image_size])
      img = TF.to_tensor(img).unsqueeze(0)
      out = map_pixels(img)
      all_t.append(out)
    out = torch.cat(all_t, dim = 0)
    return out

  @torch.no_grad()
  def encode_image(self, x: PIL.Image) -> torch.Tensor:
    imgs = self.preprocess(x)
    z_logits = self.encoder(imgs)
    z = torch.argmax(z_logits, axis=1)
    return z

  @torch.no_grad()
  def decode_logits(self, z: torch.Tensor) -> Tuple[list, torch.Tensor]:
    z = F.one_hot(z, num_classes=self.vocab_size).permute(0, 3, 1, 2).float()
    x_stats = self.decoder(z).float()
    x_rec = unmap_pixels(torch.sigmoid(x_stats[:, :3]))
    if z.shape[0] > 1:
      imgs = [TF.to_pil_image(x, mode = "RGB") for x in x_rec]
    else:
      imgs = [TF.to_pil_image(x_rec[0], mode = "RGB")]
    return (imgs, x_rec)
