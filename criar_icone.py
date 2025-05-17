from PIL import Image, ImageDraw, ImageFont
import os

# Criar uma imagem 512x512 com fundo azul
img = Image.new('RGBA', (512, 512), color=(25, 118, 210, 255))
draw = ImageDraw.Draw(img)

# Desenhar círculo branco
draw.ellipse((50, 50, 462, 462), fill=(255, 255, 255, 255))

# Tentar usar fonte Arial ou uma fonte padrão
try:
    # Para Windows
    if os.path.exists('C:/Windows/Fonts/Arial.ttf'):
        font = ImageFont.truetype('C:/Windows/Fonts/Arial.ttf', 250)
    # Para Linux
    elif os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 250)
    else:
        font = ImageFont.load_default()
        print("Usando fonte padrão")
except Exception as e:
    print(f"Erro ao carregar fonte: {e}")
    font = ImageFont.load_default()
    
# Desenhar texto G no centro
draw.text((256, 256), 'G', fill=(25, 118, 210, 255), anchor='mm', font=font)

# Salvar a imagem
img.save('icon.png')
print("Ícone criado com sucesso!") 