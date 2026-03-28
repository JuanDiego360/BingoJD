#!/bin/bash

audio_dir="/home/juandiego/Documentos/bingo/voces_bingo"

mkdir -p "$audio_dir"

echo "🎯 Generando audios del bingo..."
echo "📁 Directorio: $audio_dir"
echo ""

for letra in B I N G O; do
    case $letra in
        B) start=1;   end=15 ;;
        I) start=16;  end=30 ;;
        N) start=31;  end=45 ;;
        G) start=46;  end=60 ;;
        O) start=61;  end=75 ;;
    esac

    for num in $(seq $start $end); do
        texto="$letra,$num"
        archivo="${letra}_$(printf '%02d' $num).mp3"
        ruta="$audio_dir/$archivo"

        echo "🔊 Generando: $texto -> $archivo"
        gtts-cli -l es "$texto" -o "$ruta"
        sleep 0.3
    done
done

echo ""
echo "✅ ¡Generación completada!"
echo "📂 Ubicación: $audio_dir"
