# You need Inkscape and ImageMagick

# Make png's of different sizes
$sizes = 16, 24, 32
Foreach($size in $sizes) {
  inkscape "favicon.svg" -w $size -h $size -o "favicon-${size}.png"
}
# Combine the png's into an ico
$pngFiles = $sizes | ForEach-Object { "favicon-${_}.png" }
magick $pngFiles -verbose -alpha Remove -colors 16 "favicon.ico"
