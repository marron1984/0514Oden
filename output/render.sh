#!/usr/bin/env bash
set -euo pipefail

W=1080
H=1920
FPS=30
WORK=/tmp/oden_work
SCN=$WORK/scenes
mkdir -p "$SCN"

render_scene () {
  local src="$1"      # source image (jpg/png) — full path
  local ovr="$2"      # overlay png — full path
  local dur="$3"      # seconds
  local out="$4"      # output mp4
  local zoom="$5"     # zoom direction: in / out / pan / none

  # zoompan expression. d = total frames; on = current frame index
  local frames
  frames=$(python3 -c "print(int($dur*$FPS))")

  local zexpr="1.0"
  local xexpr="iw/2-(iw/zoom/2)"
  local yexpr="ih/2-(ih/zoom/2)"
  case "$zoom" in
    in)  zexpr="1.0+0.08*on/$frames" ;;
    out) zexpr="1.08-0.08*on/$frames" ;;
    pan) zexpr="1.05" ; xexpr="iw/2-(iw/zoom/2)+30*sin(on/$frames*3.14)"; ;;
    *)   zexpr="1.0" ;;
  esac

  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -framerate $FPS -t "$dur" -i "$src" \
    -loop 1 -framerate $FPS -t "$dur" -i "$ovr" \
    -filter_complex "
      [0:v]scale=${W}*2:${H}*2:force_original_aspect_ratio=increase,
            crop=${W}*2:${H}*2,setsar=1,
            zoompan=z='${zexpr}':x='${xexpr}':y='${yexpr}':d=1:s=${W}x${H}:fps=${FPS}[bg];
      [bg][1:v]overlay=0:0,format=yuv420p[v]
    " \
    -map "[v]" -c:v libx264 -profile:v high -level 4.0 -preset medium -crf 19 \
    -pix_fmt yuv420p -r $FPS -t "$dur" "$out"
  echo "  ok: $out"
}

render_solid () {
  # Scene built from overlay only (no source image). overlay must already cover full frame.
  local ovr="$1"
  local dur="$2"
  local out="$3"
  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -framerate $FPS -t "$dur" -i "$ovr" \
    -filter_complex "[0:v]scale=${W}:${H},format=yuv420p[v]" \
    -map "[v]" -c:v libx264 -profile:v high -level 4.0 -preset medium -crf 19 \
    -pix_fmt yuv420p -r $FPS -t "$dur" "$out"
  echo "  ok: $out"
}

# Map images
IMG7=$WORK/img7.jpg   # おでん釜_お出汁  (steaming pot, 3840x5760)
IMG8=$WORK/img8.jpg   # おでん釜_盛り付け (3840x5760)
IMG1=$WORK/img1.jpg   # Skewer A
IMG2=$WORK/img2.jpg   # Skewer B
IMG3=$WORK/img3.jpg   # Skewer C
IMG5=$WORK/img5.jpg   # group shot
IMG6=$WORK/img6.jpg   # assorted plate
IMG9=$WORK/img9.png   # QR

OV=$WORK/overlays

echo "[1/9] hook"     ; render_scene "$IMG7" "$OV/01_hook.png"     2.0 "$SCN/s01.mp4" in
echo "[2/9] tease"    ; render_scene "$IMG8" "$OV/02_tease.png"    2.0 "$SCN/s02.mp4" out
echo "[3/9] logo"     ; render_solid          "$OV/03_logo.png"    2.5 "$SCN/s03.mp4"
echo "[4/9] A skewer" ; render_scene "$IMG1" "$OV/04_skewer_A.png" 2.5 "$SCN/s04.mp4" in
echo "[5/9] B skewer" ; render_scene "$IMG2" "$OV/05_skewer_B.png" 2.5 "$SCN/s05.mp4" in
echo "[6/9] C skewer" ; render_scene "$IMG3" "$OV/06_skewer_C.png" 2.5 "$SCN/s06.mp4" in
echo "[7/9] tagline"  ; render_scene "$IMG5" "$OV/07_tagline.png"  2.5 "$SCN/s07.mp4" out
echo "[8/9] price"    ; render_scene "$IMG6" "$OV/08_price.png"    3.0 "$SCN/s08.mp4" in
echo "[9/9] cta"      ; render_scene "$IMG9" "$OV/09_cta.png"      3.5 "$SCN/s09.mp4" out

# Concat list
LIST=$WORK/concat.txt
> "$LIST"
for i in 1 2 3 4 5 6 7 8 9; do
  printf "file '%s/s%02d.mp4'\n" "$SCN" "$i" >> "$LIST"
done

# Concat (re-encode for safety; per-scene encoders/timestamps can mismatch otherwise)
ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i "$LIST" \
  -c:v libx264 -profile:v high -level 4.0 -preset medium -crf 19 \
  -pix_fmt yuv420p -r $FPS \
  "$WORK/video_silent.mp4"
echo "concat ok"

# Mux audio (BGM from repo MP3) — trim to 23s, fade in/out, light loudness normalize
BGM="$WORK/source_bgm.mp3"
[ -f "$BGM" ] || BGM="$WORK/bgm.wav"

ffmpeg -y -hide_banner -loglevel error \
  -i "$WORK/video_silent.mp4" \
  -i "$BGM" \
  -filter_complex "[1:a]atrim=0:23,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.6,afade=t=out:st=21.4:d=1.6,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  "$WORK/chibi_oden_reel.mp4"

echo
echo "DONE → $WORK/chibi_oden_reel.mp4"
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=noprint_wrappers=1 "$WORK/chibi_oden_reel.mp4"
