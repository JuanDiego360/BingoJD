#!/bin/bash

valor_carton=5000
num_cartones=$(ls cartones/* | wc -l)
valor_recodido=$((valor_carton * num_cartones))
premio=$(echo "$valor_recodido * 0.3/2" | bc)
Fondos=$((valor_recodido - premio * 2))
echo "número de cartones vendidos: $num_cartones"
echo "El valor recogido: $valor_recodido"
echo "Premio total: $((premio*2))"
echo "Premio1: $premio"
echo "Premio2: $premio"
echo "Fondos: $Fondos"
