# -*- coding: utf-8 -*-
from io import BytesIO
import telebot
import torch
import cv2
from torchvision.transforms.functional import to_tensor
from PIL import Image
import numpy as np
from PIL import ImageOps


model = torch.load('segm_model.pth')
bot = telebot.TeleBot('<MyToken>')







def photo_transform(img_pil):
    pad_width = 32 - img_pil.width % 32
    pad_height = 32 - img_pil.height % 32

    if pad_width != 0 or pad_height != 0:
        img_pil = ImageOps.pad(img_pil, (img_pil.width + pad_width, img_pil.height + pad_height))

    img_tensor = to_tensor(img_pil).unsqueeze(0)
    output = model(img_tensor)
    out1 = output[0][0].detach().numpy()

    out2 = (out1 >= 0.7).astype(int)

    mask_image = (out2 * 255).astype(np.uint8)

    mask_image = Image.fromarray(mask_image)
    mask_image = mask_image.convert('L')
    img_pil = img_pil.convert("RGBA")


    img_pil.putalpha(mask_image)


    return img_pil, mask_image

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для удаления фона у фотографий с человеком. GitHub этого проекта и мой kaggle в описании бота.')
    bot.send_message(message.chat.id, 'присылай фото!')

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.send_message(message.chat.id, 'уже обрабатываю твой запрос!⏳')
    file_info = bot.get_file(message.photo[-1].file_id)
    image_stream = bot.download_file(file_info.file_path)
    img_pil = Image.open(BytesIO(image_stream))



    def process_image():
        out_image, mask_image = photo_transform(img_pil)
        out_image_stream = BytesIO()
        out_image.save('out image.png',format('PNG'))
        out_image.save(out_image_stream, format='PNG')
        out_image_stream.seek(0)

        mask_image_stream = BytesIO()
        mask_image.save(mask_image_stream, format='PNG')
        mask_image_stream.seek(0)


        with open('out image.png','rb') as f:
            bot.send_document(message.chat.id,f )
        bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(out_image_stream),telebot.types.InputMediaPhoto(mask_image_stream)])

    process_image()

bot.polling()




