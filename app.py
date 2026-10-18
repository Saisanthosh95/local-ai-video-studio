
import streamlit as st
from PIL import Image, ImageDraw
from moviepy import ImageClip, concatenate_videoclips
from io import BytesIO
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Local AI Video Studio", page_icon="🎬")
st.title("🎬 Local AI Video Studio")
st.write("Version 0.1 — Storyboard to vertical video")

st.info(
    "Upload your own images, add captions, and create a vertical MP4. "
    "AI animation and voice-over will come in later versions."
)

title = st.text_input("Video title", "My First Story")
count = st.number_input(
    "Number of scenes", min_value=1, max_value=10, value=3
)

scenes = []

for i in range(int(count)):
    st.subheader(f"Scene {i + 1}")

    image_file = st.file_uploader(
        f"Upload image for scene {i + 1}",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"image_{i}"
    )

    caption = st.text_input(
        f"Caption for scene {i + 1}",
        key=f"caption_{i}"
    )

    duration = st.slider(
        f"Duration for scene {i + 1} (seconds)",
        min_value=1,
        max_value=15,
        value=4,
        key=f"duration_{i}"
    )

    scenes.append((image_file, caption, duration))


def make_frame(upload, caption):
    image = Image.open(BytesIO(upload.getvalue())).convert("RGB")

    width, height = 720, 1280
    ratio = max(width / image.width, height / image.height)

    image = image.resize((
        int(image.width * ratio),
        int(image.height * ratio)
    ))

    left = (image.width - width) // 2
    top = (image.height - height) // 2
    image = image.crop((left, top, left + width, top + height))

    if caption.strip():
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle(
            (35, 1000, 685, 1190),
            fill=(0, 0, 0, 190)
        )
        draw.text(
            (55, 1050),
            caption[:180],
            fill="white",
            stroke_width=1,
            stroke_fill="black"
        )

    return image


if st.button("Export vertical MP4", type="primary"):
    missing = [
        str(i + 1)
        for i, scene in enumerate(scenes)
        if scene[0] is None
    ]

    if missing:
        st.error("Upload an image for every scene.")
    else:
        clips = []
        output = None

        try:
            with st.spinner("Creating your video..."):
                for upload, caption, duration in scenes:
                    frame = make_frame(upload, caption)
                    clips.append(
                        ImageClip(frame).with_duration(duration)
                    )

                final = concatenate_videoclips(clips, method="compose")

                output = Path(
                    f"story_{datetime.now():%Y%m%d_%H%M%S}.mp4"
                )

                try:
                    final.write_videofile(
                        str(output),
                        fps=24,
                        codec="libx264",
                        audio=False,
                        preset="ultrafast",
                        logger=None
                    )
                finally:
                    final.close()

            st.success("Your video is ready!")
            st.video(str(output))

            st.download_button(
                "Download MP4",
                data=output.read_bytes(),
                file_name=output.name,
                mime="video/mp4"
            )

        except Exception as error:
            st.error(f"Video export failed: {error}")

        finally:
            for clip in clips:
                clip.close()
