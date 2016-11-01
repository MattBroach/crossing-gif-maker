#!/bin/bash

OUTPUT_FOLDER='output'
SOURCE_FOLDER='PNG'
MAP_IMAGE='map.png'

FIRST_NAME=$1
SECOND_NAME=$2
LOCATION=$3
ID=$4
ATTRIBUTION="Map data © OpenStreetMap (CC BY-SA)"

# CREATE INITIAL TEXT
echo "Creating Text Overlays"

convert -background '#0e8044' -fill white -font Helvetica -size 200x40 -gravity Center label:"$FIRST_NAME" first_name.png
convert  -background '#0e8044' -fill white -font Helvetica -size 200x40 -gravity Center label:"$SECOND_NAME" second_name.png
convert -background '#0e8044' -fill white -font Helvetica -size 500x30 -gravity Center label:"$LOCATION" location.png

mkdir -p $OUTPUT_FOLDER

composite_with_offset () {
    FIRST_OFFSET=$1
    SECOND_OFFSET=$2
    LOCATION_OFFSET=$3
    ATTRIBUTION_OFFSET=$4
    INDEX=$5

    SOURCE_FILE=$SOURCE_FOLDER/GIF_$(printf %02d $INDEX).png
    OUTPUT_FILE=$OUTPUT_FOLDER/COMBINED_$(printf %02d $INDEX).png

    convert -page 0 $MAP_IMAGE -page 0 $SOURCE_FILE -page $FIRST_OFFSET+33 first_name.png \
            -page +$SECOND_OFFSET+33 second_name.png -page +70+$LOCATION_OFFSET location.png \
            -fill black -pointsize 10 -annotate +435+$ATTRIBUTION_OFFSET "$ATTRIBUTION" \
            -layers flatten $OUTPUT_FILE
}


# COMPOSE INDIVIDUAL IMAGES
echo "Compositing Intermediaries"
GIF_PARAMS=()
for i in {0..71}; do
    SOURCE_FILE=$SOURCE_FOLDER/GIF_$(printf %02d $i).png
    OUTPUT_FILE=$OUTPUT_FOLDER/COMBINED_$(printf %02d $i).png

    # Before text enters, we only need to combine the animation and the map
    if [ $i -lt 49 ]; then
        composite $SOURCE_FILE $MAP_IMAGE $OUTPUT_FILE
    # While text is moving, combine all images with the proper offsts
    elif [ $i -lt 58 ]; then
        case $i in
            49)
                composite_with_offset "-172" 613 494 494 $i
                ;;
            50)
                composite_with_offset "-110" 554 494 494 $i
                ;;
            51)
                composite_with_offset "-62" 502 494 494 $i
                ;;
            52)
                composite_with_offset "-26" 466 494 482 $i
                ;;
            53)
                composite_with_offset "+0" 440 475 458 $i
                ;;
            54)
                composite_with_offset "+15" 425 461 444 $i
                ;;
            55)
                composite_with_offset "+20" 420 451 434 $i
                ;;
            56)
                composite_with_offset "+20" 420 447 430 $i
                ;;
            57)
                composite_with_offset "+20" 420 445 428 $i
                ;;
        esac
    # After animation is done, repeate last frame for hold
    else
        OUTPUT_FILE=$OUTPUT_FOLDER/COMBINED_57.png
    fi

    GIF_PARAMS+=("-page")
    GIF_PARAMS+=("0")
    GIF_PARAMS+=($OUTPUT_FILE)
done

# CREATE GIF
echo "Making Gif"
convert -delay 83x1000 -size 640x480 "${GIF_PARAMS[@]/#/}" -loop 0 temp.gif
convert temp.gif +dither -layers Optimize -colors 32 $ID.gif

# CLEAN UP TEMP FILES
echo "Cleaning"
rm first_name.png
rm second_name.png
rm location.png
rm $OUTPUT_FOLDER/*.png
rm temp.gif
rm map.png
