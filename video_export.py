
from pathlib import Path

from moviepy import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


def create_scene_image(image_path, caption, output_path):
    """Create a vertical scene image with a caption."""
    background = Image.open(image_path).convert("RGB")
    background = background.resize(
        (VIDEO_WIDTH, VIDEO_HEIGHT),
        Image.Resampling.LANCZOS,
    )

    draw = ImageDraw.Draw(background)
    font = ImageFont.load_default(size=48)

    margin = 60
    text = str(caption or "").strip()

    if text:
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if draw.textbbox((0, 0), test_line, font=font)[2] > VIDEO_WIDTH - 2 * margin:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        line_height = 65
        box_height = len(lines) * line_height + 50
        box_top = VIDEO_HEIGHT - box_height - 100

        draw.rectangle(
            (0, box_top, VIDEO_WIDTH, VIDEO_HEIGHT),
            fill=(0, 0, 0),
        )

        for index, line in enumerate(lines):
            draw.text(
                (margin, box_top + 25 + index * line_height),
                line,
                font=font,
                fill=(255, 255, 255),
            )

    background.save(output_path)
    return output_path


def export_video(scenes, output_path="story.mp4", fps=24):
    """Export scenes as a vertical MP4.

    Each scene is a dictionary with:
    image_path, caption, duration
    """
    clips = []
    temporary_images = []

    try:
        for index, scene in enumerate(scenes):
            image_path = scene["image_path"]
            caption = scene.get("caption", "")
            duration = max(float(scene.get("duration", 3)), 1)

            temp_path = f"scene_{index}_render.png"
            create_scene_image(image_path, caption, temp_path)
            temporary_images.append(temp_path)

            clip = ImageClip(temp_path).with_duration(duration)
            clips.append(clip)

        if not clips:
            raise ValueError("Add at least one scene before exporting.")

        final_video = CompositeVideoClip(
            clips,
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        )

        final_video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio=False,
        )
        final_video.close()

        return output_path

    finally:
        for clip in clips:
            clip.close()

        for temp_path in temporary_images:
            Path(temp_path).unlink(missing_ok=True)
