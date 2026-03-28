#!/bin/bash

audio_dir="/home/juandiego/Documentos/bingo/voces_bingo"

mkdir -p "$audio_dir"

echo "🔎 Revisando qué audios faltan..."
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
        archivo="${letra}_$(printf '%02d' $num).mp3"
        ruta="$audio_dir/$archivo"
        texto="$letra,$num"

        # Si el archivo no existe o está vacío (<1 KB)
        if [ ! -s "$ruta" ] || [ $(stat -c%s "$ruta") -lt 1000 ]; then
            echo "⚠️  Faltaba o estaba corrupto: $archivo → regenerando..."
            gtts-cli -l es "$texto" -o "$ruta"
            sleep 0.5
        fi
    done
done

echo ""
echo "✅ Revisión completada. Todos los audios deberían estar listos."
echo "📂 Ubicación: $audio_dir"
