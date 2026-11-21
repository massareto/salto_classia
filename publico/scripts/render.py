"""Render three readable proto-persona cards from the workshop research."""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH, HEIGHT = 1600, 1120
PAPER, INK, MUTED, DARK = '#f6f2e8', '#132d27', '#425650', '#102a23'
LABELS = {
    'pt': {
        'behaviors': 'Comportamentos', 'needs_goals': 'Necessidades/Metas',
        'needs': 'Necessidades', 'goals': 'Metas',
        'demographics_title': 'Dados demográficos', 'scene_title': 'Na foto',
        'demographics': ('Idade', 'Sexo / gênero', 'Profissão', 'Formação',
                         'Tem filhos?', 'Estado civil', 'Localidade'),
        'scene': ('Onde', 'Ao fundo', 'Na mão', 'Roupa'),
        'mixed': 'Perfil composto', 'hypothesis': 'Perfil estimado',
        'footer': 'Personagem fictício. Fontes e estimativas no relatório de pesquisa.',
    },
    'en': {
        'behaviors': 'Behaviors', 'needs_goals': 'Needs/Goals',
        'needs': 'Needs', 'goals': 'Goals',
        'demographics_title': 'Demographics', 'scene_title': 'In the photo',
        'demographics': ('Age', 'Sex / gender', 'Occupation', 'Education',
                         'Has children?', 'Marital status', 'Location'),
        'scene': ('Setting', 'Backdrop', 'In hand', 'Clothing'),
        'mixed': 'Composite profile', 'hypothesis': 'Estimated profile',
        'footer': 'Fictional persona. Sources and estimates in the research report.',
    },
}
BULLET_LIMITS = {'behaviors': 7, 'needs': 6, 'goals': 6}
DEMOGRAPHIC_FIELDS = ('age', 'sex', 'occupation', 'education', 'children', 'marital_status', 'location')
SCENE_FIELDS = ('setting', 'background', 'in_hand', 'clothing')
PALETTES = (('#cae1d2', '#2d6250'), ('#f1dab0', '#8b522a'), ('#d8dcf2', '#555d8f'))


def font(size, bold=False):
    filenames = ('Arial Bold.ttf', 'DejaVuSans-Bold.ttf', 'arialbd.ttf') if bold else (
        'Arial.ttf', 'DejaVuSans.ttf', 'arial.ttf')
    directories = (
        Path('/System/Library/Fonts/Supplemental'),
        Path('/usr/share/fonts/truetype/dejavu'),
        Path('C:/Windows/Fonts'),
    )
    for directory, filename in zip(directories, filenames):
        candidate = directory / filename
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def wrap(draw, text, typeface, width):
    lines = []
    current = ''
    for word in text.split():
        proposal = f'{current} {word}'.strip()
        if draw.textlength(proposal, font=typeface) <= width:
            current = proposal
        else:
            if not current or draw.textlength(word, font=typeface) > width:
                raise ValueError(f'Word does not fit: {word}')
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def portrait(canvas, box, path):
    x, y, width, height = box
    with Image.open(path) as source:
        image = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'),
                             (width, height), centering=(.5, .32))
    mask = Image.new('L', (width, height))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=25, fill=255)
    canvas.paste(image, (x, y), mask)


def draw_bullets(draw, items, x, y, width, bottom, accent, field):
    gap = 5
    for size in (27, 25, 23, 21):
        typeface = font(size)
        lines = [wrap(draw, item, typeface, width - 23) for item in items]
        line_height = size + 6
        height = sum(len(item) * line_height for item in lines) + (len(lines) - 1) * gap
        if y + height <= bottom:
            break
    else:
        raise ValueError(f'Shorten the text in {field}.')
    for item in lines:
        draw.ellipse((x, y + 10, x + 7, y + 17), fill=accent)
        for line in item:
            draw.text((x + 23, y), line, fill=INK, font=typeface)
            y += line_height
        y += gap


def draw_demographics(draw, fields, labels, x, y, width, bottom):
    rows = [(label, fields[key]) for key, label in zip(DEMOGRAPHIC_FIELDS, labels)]
    label_font = font(20, bold=True)
    value_offset = 150
    for size in (24, 22, 20):
        value_font = font(size)
        values = [wrap(draw, value, value_font, width - value_offset) for _, value in rows]
        line_height = size + 5
        row_heights = [max(32, len(lines) * line_height + 6) for lines in values]
        if y + sum(row_heights) <= bottom:
            break
    else:
        raise ValueError('Shorten the demographic values.')

    for i, ((label, _), lines, row_height) in enumerate(zip(rows, values, row_heights)):
        draw.text((x, y), label, fill=MUTED, font=label_font)
        for index, line in enumerate(lines):
            draw.text((x + value_offset, y + index * line_height), line, fill=INK, font=value_font)
        y += row_height
        if i < len(rows) - 1:
            draw.line((x, y - 5, x + width, y - 5), fill='#dddcd0', width=1)


def render(profile, labels, palette, directory):
    soft, accent = palette
    canvas = Image.new('RGB', (WIDTH, HEIGHT), DARK)
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 44), 'PROTO-PERSONA', fill=soft, font=font(27, bold=True))
    draw.text((1536, 44), labels[profile['evidence']], fill='#e8e4d7', font=font(25), anchor='ra')

    segment_font = font(54, bold=True)
    segment = wrap(draw, profile['segment'], segment_font, 1472)
    if len(segment) > 2:
        raise ValueError('Shorten the segment title.')
    for index, line in enumerate(segment):
        draw.text((64, 92 + index * 59), line, fill=PAPER, font=segment_font)

    portrait(canvas, (64, 224, 720, 344), directory / profile['portrait'])

    draw.rounded_rectangle((816, 224, 1536, 568), radius=25, fill=PAPER)
    draw.text((846, 249), labels['behaviors'], fill=INK, font=font(35, bold=True))
    draw_bullets(draw, profile['behaviors'], 848, 312, 656, 547, accent, labels['behaviors'])

    draw.rounded_rectangle((64, 592, 784, 1024), radius=25, fill=PAPER)
    name_font = font(33, bold=True)
    name = wrap(draw, profile['name'], name_font, 656)
    if len(name) > 2:
        raise ValueError('Shorten the fictional name.')
    for index, line in enumerate(name):
        draw.text((94, 615 + index * 37), line, fill=INK, font=name_font)
    columns_top = 624 + len(name) * 37
    draw.text((94, columns_top), labels['demographics_title'], fill=accent, font=font(25, bold=True))
    draw.text((484, columns_top), labels['scene_title'], fill=accent, font=font(25, bold=True))
    draw.line((465, columns_top, 465, 997), fill='#d9d9ce', width=2)
    draw_demographics(draw, profile['demographics'], labels['demographics'], 94, columns_top + 44, 352, 1003)
    scene = [f'{label} · {profile["scene"][field]}' for field, label in zip(SCENE_FIELDS, labels['scene'])]
    draw_bullets(draw, scene, 484, columns_top + 44, 270, 1003, accent, labels['scene_title'])

    draw.rounded_rectangle((816, 592, 1536, 1024), radius=25, fill=PAPER)
    draw.text((846, 617), labels['needs_goals'], fill=INK, font=font(35, bold=True))
    draw.line((1176, 680, 1176, 997), fill='#d9d9ce', width=2)
    for column, field in enumerate(('needs', 'goals')):
        left = 848 + column * 352
        draw.text((left, 680), labels[field], fill=accent, font=font(25, bold=True))
        draw_bullets(draw, profile[field], left, 723, 304, 997, accent, labels[field])
    draw.text((64, 1062), labels['footer'], fill='#e8e4d7', font=font(24))
    return canvas


def validate(document, directory):
    if not isinstance(document, dict) or document.get('language') not in LABELS:
        raise ValueError('Provide language pt or en.')
    profiles = document.get('profiles')
    if not isinstance(profiles, list) or len(profiles) != 3:
        raise ValueError('Provide exactly three profiles.')
    portraits = set()
    for expected_profile, profile in enumerate(profiles, 1):
        if not isinstance(profile, dict):
            raise ValueError(f'Profile {expected_profile:02} must be a JSON object.')
        if profile.get('evidence') not in ('mixed', 'hypothesis'):
            raise ValueError('Set evidence to mixed or hypothesis.')
        for field in ('name', 'segment', 'portrait'):
            if not isinstance(profile.get(field), str) or not profile[field].strip():
                raise ValueError(f'Provide text for {field}.')
        portrait_file = (directory / profile['portrait']).resolve()
        if not portrait_file.is_file():
            raise ValueError(f'Generated portrait missing for profile {expected_profile:02}.')
        portrait_digest = sha256(portrait_file.read_bytes()).digest()
        if portrait_digest in portraits:
            raise ValueError('Provide a different generated portrait file for each profile.')
        portraits.add(portrait_digest)
        scene = profile.get('scene')
        if not isinstance(scene, dict) or not all(
                isinstance(scene.get(key), str) and scene[key].strip() for key in SCENE_FIELDS):
            raise ValueError('Describe the setting, background, object in hand, and clothing.')
        demographics = profile.get('demographics')
        if not isinstance(demographics, dict) or set(demographics) != set(DEMOGRAPHIC_FIELDS):
            raise ValueError('Complete all seven demographics fields before generating the portrait.')
        for key, value in demographics.items():
            pending = r'\b(?:a validar|a confirmar|to validate|tbd|não informado|unknown|unverified)\b'
            if not isinstance(value, str) or not value.strip() or re.search(pending, value, flags=re.I):
                raise ValueError(f'Provide a researched value or a grounded estimate for {key}.')
        for field, limit in BULLET_LIMITS.items():
            items = profile.get(field)
            if not isinstance(items, list) or not 1 <= len(items) <= limit:
                raise ValueError(f'Provide one to {limit} short items for {field}.')
            if not all(isinstance(item, str) and item.strip() for item in items):
                raise ValueError(f'Provide non-empty text for each item in {field}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profiles', type=Path, help='Input JSON. PNGs are saved next to it.')
    args = parser.parse_args()
    try:
        data = json.loads(args.profiles.read_text(encoding='utf-8'))
        folder = args.profiles.parent
        validate(data, folder)
        images = [render(profile, LABELS[data['language']], palette, folder)
                  for profile, palette in zip(data['profiles'], PALETTES)]
        for index, image in enumerate(images, 1):
            path = folder / f'{index:02}.png'
            image.save(path)
            print(path)
    except (ValueError, OSError) as error:
        parser.exit(2, f'{error}\n')


if __name__ == '__main__':
    main()
