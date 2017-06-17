#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_FOLDER=/tmp
OUTPUT_FOLDER=$BASE_FOLDER/output
SOURCE_FOLDER=$DIR/PNG

FIRST_NAME=$1
SECOND_NAME=$2
LOCATION=$3
ID=$4
ATTRIBUTION="Map data © OpenStreetMap (CC BY-SA)"
MAP_IMAGE=$BASE_FOLDER/map_$ID.png

# CREATE INITIAL TEXT
echo "Creating Text Overlays"

convert -background '#0e8044' -fill white -font Helvetica -size 200x40 -gravity Center caption:"$FIRST_NAME" $BASE_FOLDER/first_name_$ID.png
convert  -background '#0e8044' -fill white -font Helvetica -size 200x40 -gravity Center caption:"$SECOND_NAME" $BASE_FOLDER/second_name_$ID.png
convert -background '#0e8044' -fill white -font Helvetica -size 500x30 -gravity Center caption:"$LOCATION" $BASE_FOLDER/location_$ID.png

mkdir -p $OUTPUT_FOLDER

composite_with_offset () {
    FIRST_OFFSET=$1
    SECOND_OFFSET=$2
    LOCATION_OFFSET=$3
    ATTRIBUTION_OFFSET=$4
    INDEX=$5

    SOURCE_FILE=$SOURCE_FOLDER/Gif_$(printf %02d $INDEX).png
    OUTPUT_FILE=$OUTPUT_FOLDER/COMBINED_$(printf %02d $INDEX)_$ID.png

    convert -page 0 $MAP_IMAGE -page 0 $SOURCE_FILE -page $FIRST_OFFSET+33 $BASE_FOLDER/first_name_$ID.png \
            -page +$SECOND_OFFSET+33 $BASE_FOLDER/second_name_$ID.png -page +70+$LOCATION_OFFSET $BASE_FOLDER/location_$ID.png \
            -fill black -pointsize 10 -annotate +435+$ATTRIBUTION_OFFSET "$ATTRIBUTION" \
            -layers flatten $OUTPUT_FILE
}


# COMPOSE INDIVIDUAL IMAGES
echo "Compositing Intermediaries"
GIF_PARAMS=()
for i in {0..71}; do
    SOURCE_FILE=$SOURCE_FOLDER/Gif_$(printf %02d $i).png
    OUTPUT_FILE=$OUTPUT_FOLDER/COMBINED_$(printf %02d $i)_${ID}.png

    # Before text enters, we only need to combine the animation and the map
    if [ $i -lt 49 ]; then
        composite $SOURCE_FILE $MAP_IMAGE $OUTPUT_FILE
    # While text is moving, combine all images with the proper offsts
    elif [ $i -lt 58 ]; then
        case $i in
            49)
                composite_with_offset "-172" 613 500 500 $i
                ;;
            50)
                composite_with_offset "-110" 554 500 500 $i
                ;;
            51)
                composite_with_offset "-62" 502 500 500 $i
                ;;
            52)
                composite_with_offset "-26" 466 497 497 $i
                ;;
            53)
                composite_with_offset "+0" 440 447 425 $i
                ;;
            54)
                composite_with_offset "+15" 425 415 393 $i
                ;;
            55)
                composite_with_offset "+20" 420 392 370 $i
                ;;
            56)
                composite_with_offset "+20" 420 379 357 $i
                ;;
            57)
                composite_with_offset "+20" 420 375 353 $i
                ;;
        esac
    # After animation is done, repeate last frame for hold
    else
        cp $OUTPUT_FOLDER/COMBINED_57_${ID}.png $OUTPUT_FOLDER/COMBINED_${i}_$ID.png
    fi

done

# CREATE GIF
echo "Making Gif"
$DIR/ffmpeg -y -framerate 12 -i $OUTPUT_FOLDER/COMBINED_%02d_${ID}.png -c:v libx264 -vf fps=12 -pix_fmt yuv420p $BASE_FOLDER/$ID.mp4

# CLEAN UP TEMP FILES
echo "Cleaning"
rm $BASE_FOLDER/first_name_$ID.png
rm $BASE_FOLDER/second_name_$ID.png
rm $BASE_FOLDER/location_$ID.png
rm $OUTPUT_FOLDER/*_$ID.png
rm $BASE_FOLDER/map_$ID.png
