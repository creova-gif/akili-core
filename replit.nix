{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.ffmpeg-full   # required by AMPLIFY audio-only visualizer
  ];
}
